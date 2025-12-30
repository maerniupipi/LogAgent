"""主程序入口"""
from agent import SimpleAgent

def main():
    print("=" * 50)
    print("LangGraph Agent 启动")
    print("=" * 50)
    
    # 创建 agent
    agent = SimpleAgent()
    
    # 测试示例
    test_queries = [
        "现在几点了？",
        "帮我计算 25 * 4",
        "告诉我关于 DGX 的信息",
    ]
    
    for query in test_queries:
        try:
            agent.run(query)
        except Exception as e:
            print(f"错误: {str(e)}")
        print("\n")
    
    # 交互模式
    print("\n进入交互模式（输入 'quit' 退出）:")
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("再见！")
            break
        
        if user_input:
            try:
                agent.run(user_input)
            except Exception as e:
                print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
