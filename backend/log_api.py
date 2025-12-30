"""
日志监控API - 提供日志采集和查询接口
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import logging
import requests
from datetime import datetime

from log_collector import LogCollector, LogAnalyzer
from log_storage import LogStorage
from qwen_agent import QwenAgent
from server_config import ServerConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="日志监控系统")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局存储
storage = LogStorage()
config_manager = ServerConfigManager()


class SSHConfig(BaseModel):
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    key_file: Optional[str] = None


class CollectRequest(BaseModel):
    ssh_config: SSHConfig
    container_name: str
    lines: int = 1000
    analyze: bool = True


class CollectByConfigRequest(BaseModel):
    config_id: int
    container_name: str
    lines: int = 1000
    analyze: bool = True


class ServerConfigCreate(BaseModel):
    name: str
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    key_file: Optional[str] = None
    containers: Optional[List[str]] = None


@app.post("/api/collect")
async def collect_logs(request: CollectRequest, background_tasks: BackgroundTasks):
    """采集Docker容器日志"""
    try:
        # 创建采集器
        collector = LogCollector(
            host=request.ssh_config.host,
            port=request.ssh_config.port,
            username=request.ssh_config.username,
            password=request.ssh_config.password,
            key_file=request.ssh_config.key_file
        )
        
        # 连接SSH
        if not collector.connect():
            raise HTTPException(status_code=500, detail="SSH连接失败")
        
        # 获取日志
        logs = collector.get_docker_logs(request.container_name, request.lines)
        
        # 解析错误
        errors = collector.parse_error_logs(logs)
        
        collector.disconnect()
        
        # 如果需要AI分析，在后台执行
        if request.analyze and errors:
            background_tasks.add_task(
                analyze_and_save_errors,
                request.container_name,
                errors
            )
        else:
            # 直接保存未分析的错误
            for error in errors:
                storage.save_error(request.container_name, {'original': error})
        
        # 保存采集历史
        storage.save_collection_history(
            request.container_name,
            request.lines,
            len(errors)
        )
        
        return {
            "success": True,
            "message": f"成功采集 {len(errors)} 个错误",
            "error_count": len(errors),
            "analyzing": request.analyze
        }
        
    except Exception as e:
        logger.error(f"采集日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_and_save_errors(container_name: str, errors: List[dict]):
    """后台任务：分析并保存错误"""
    try:
        # 使用远程 Qwen API
        import requests
        
        # 远程模型服务地址
        AI_SERVICE_URL = "http://172.16.50.103:8000/v1/chat"
        
        for error in errors:
            error_content = error['content']
            context = '\n'.join(error['context'][:5])  # 取前5行上下文
            
            prompt = f"""请分析以下错误日志，并提供：
1. 错误类型和严重程度
2. 可能的原因
3. 建议的解决方案

错误日志：
{error_content}

上下文：
{context}
"""
            
            try:
                # 调用远程AI服务
                response = requests.post(
                    AI_SERVICE_URL,
                    json={
                        "prompt": prompt,
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result.get('response', '分析失败')
                else:
                    analysis = f"AI分析失败: HTTP {response.status_code}"
                    
            except Exception as e:
                analysis = f"AI分析失败: {str(e)}"
            
            analyzed = {
                'original': error,
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat()
            }
            storage.save_error(container_name, analyzed)
        
        logger.info(f"完成 {len(errors)} 个错误的分析")
    except Exception as e:
        logger.error(f"分析错误失败: {e}")


@app.get("/api/errors")
async def get_errors(
    container_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """获取错误日志列表"""
    try:
        errors = storage.get_errors(container_name, status, limit)
        return {
            "success": True,
            "data": errors,
            "count": len(errors)
        }
    except Exception as e:
        logger.error(f"获取错误列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/errors/{error_id}")
async def get_error_detail(error_id: int):
    """获取错误详情"""
    try:
        error = storage.get_error_by_id(error_id)
        if not error:
            raise HTTPException(status_code=404, detail="错误不存在")
        
        return {
            "success": True,
            "data": error
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取错误详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class StatusUpdate(BaseModel):
    status: str


@app.put("/api/errors/{error_id}/status")
async def update_error_status(error_id: int, update: StatusUpdate):
    """更新错误状态"""
    try:
        storage.update_error_status(error_id, update.status)
        return {
            "success": True,
            "message": "状态更新成功"
        }
    except Exception as e:
        logger.error(f"更新状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_collection_history(limit: int = 50):
    """获取采集历史"""
    try:
        history = storage.get_collection_history(limit)
        return {
            "success": True,
            "data": history
        }
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


# ========== 服务器配置管理 ==========

@app.get("/api/configs")
async def get_configs():
    """获取所有服务器配置"""
    try:
        configs = config_manager.get_all_configs()
        return {
            "success": True,
            "data": configs
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/configs")
async def create_config(config: ServerConfigCreate):
    """创建服务器配置"""
    try:
        new_config = config_manager.add_config(
            name=config.name,
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            key_file=config.key_file,
            containers=config.containers
        )
        return {
            "success": True,
            "data": new_config,
            "message": "配置创建成功"
        }
    except Exception as e:
        logger.error(f"创建配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/configs/{config_id}")
async def delete_config(config_id: int):
    """删除服务器配置"""
    try:
        config_manager.delete_config(config_id)
        return {
            "success": True,
            "message": "配置删除成功"
        }
    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collect-by-config")
async def collect_logs_by_config(request: CollectByConfigRequest, background_tasks: BackgroundTasks):
    """使用保存的配置采集日志"""
    try:
        # 获取配置
        config = config_manager.get_config(request.config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 创建采集器
        collector = LogCollector(
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config.get("password"),
            key_file=config.get("key_file")
        )
        
        # 连接SSH
        if not collector.connect():
            raise HTTPException(status_code=500, detail="SSH��接失败")
        
        # 获取日志
        logs = collector.get_docker_logs(request.container_name, request.lines)
        
        # 解析错误
        errors = collector.parse_error_logs(logs)
        
        collector.disconnect()
        
        # 如果需要AI分析，在后台执行
        if request.analyze and errors:
            background_tasks.add_task(
                analyze_and_save_errors,
                request.container_name,
                errors
            )
        else:
            # 直接保存未分析的错误
            for error in errors:
                storage.save_error(request.container_name, {'original': error})
        
        # 保存采集历史
        storage.save_collection_history(
            request.container_name,
            request.lines,
            len(errors)
        )
        
        return {
            "success": True,
            "message": f"成功采集 {len(errors)} 个错误",
            "error_count": len(errors),
            "analyzing": request.analyze
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"采集日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
