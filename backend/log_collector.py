"""
日志采集模块 - 通过SSH连接远程服务器获取Docker容器日志
"""
import paramiko
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LogCollector:
    """SSH连接并采集Docker容器日志"""
    
    def __init__(self, host: str, port: int, username: str, password: str = None, key_file: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None
    
    def connect(self):
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file
                )
            else:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            logger.info(f"成功连接到 {self.host}")
            return True
        except Exception as e:
            logger.error(f"SSH连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开SSH连接"""
        if self.client:
            self.client.close()
            logger.info("SSH连接已断开")
    
    def get_docker_logs(self, container_name: str, lines: int = 1000) -> str:
        """获取Docker容器日志"""
        if not self.client:
            raise Exception("SSH未连接")
        
        command = f"docker logs -n {lines} {container_name}"
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            logs = stdout.read().decode('utf-8', errors='ignore')
            errors = stderr.read().decode('utf-8', errors='ignore')
            
            # Docker logs 可能输出到 stderr，合并两者
            full_logs = logs + errors
            logger.info(f"成功获取 {container_name} 的 {lines} 行日志")
            return full_logs
        except Exception as e:
            logger.error(f"获取Docker日志失败: {e}")
            raise
    
    def parse_error_logs(self, logs: str) -> List[Dict]:
        """解析日志，提取错误信息"""
        error_patterns = [
            r'ERROR',
            r'Exception',
            r'Error',
            r'FATAL',
            r'CRITICAL',
            r'Traceback',
            r'Failed',
            r'failed'
        ]
        
        pattern = '|'.join(error_patterns)
        lines = logs.split('\n')
        
        errors = []
        current_error = None
        
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                if current_error:
                    errors.append(current_error)
                
                current_error = {
                    'line_number': i + 1,
                    'timestamp': self._extract_timestamp(line),
                    'content': line,
                    'context': []
                }
            elif current_error:
                # 收集错误的上下文（堆栈信息等）
                current_error['context'].append(line)
                if len(current_error['context']) > 10:  # 限制上下文行数
                    errors.append(current_error)
                    current_error = None
        
        if current_error:
            errors.append(current_error)
        
        return errors
    
    def _extract_timestamp(self, log_line: str) -> Optional[str]:
        """从日志行中提取时间戳"""
        # 常见时间戳格式
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
            r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group(0)
        
        return None


class LogAnalyzer:
    """日志分析器 - 使用AI解读错误日志"""
    
    def __init__(self, agent):
        self.agent = agent
    
    async def analyze_error(self, error_info: Dict) -> Dict:
        """分析单个错误"""
        error_content = error_info['content']
        context = '\n'.join(error_info['context'][:5])  # 取前5行上下文
        
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
            # 使用 run_sync 方法
            result = self.agent.run_sync(prompt)
            analysis = result.get('response', '分析失败')
            
            return {
                'original': error_info,
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return {
                'original': error_info,
                'analysis': f"分析失败: {str(e)}",
                'analyzed_at': datetime.now().isoformat()
            }
