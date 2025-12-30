"""检查数据库内容"""
import sqlite3

conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

# 查看错误日志
cursor.execute("SELECT id, container_name, error_content, analysis FROM error_logs LIMIT 5")
rows = cursor.fetchall()

print("数据库中的错误日志：")
print("=" * 80)
for row in rows:
    print(f"\nID: {row[0]}")
    print(f"容器: {row[1]}")
    print(f"错误内容: {row[2][:200]}...")
    print(f"AI分析: {row[3][:200] if row[3] else '无'}...")
    print("-" * 80)

conn.close()
