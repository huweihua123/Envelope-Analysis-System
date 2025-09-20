#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import pymysql
from database_config import DatabaseConfig
import os

def init_database():
    """初始化数据库表结构"""
    config = DatabaseConfig()
    mysql_config = config.get_mysql_config()
    
    try:
        # 连接到MySQL数据库
        connection = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            charset='utf8mb4'
        )
        
        print(f"已连接到MySQL数据库: {mysql_config['host']}:{mysql_config['port']}")
        
        # 读取SQL文件
        sql_file_path = os.path.join(os.path.dirname(__file__), 'create_tables.sql')
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL脚本
        cursor = connection.cursor()
        
        # 分割SQL语句并逐个执行
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for stmt in sql_statements:
            if stmt and not stmt.startswith('--'):
                try:
                    cursor.execute(stmt)
                    print(f"执行成功: {stmt[:50]}..." if len(stmt) > 50 else f"执行成功: {stmt}")
                except Exception as e:
                    print(f"执行失败: {stmt[:50]}...")
                    print(f"错误信息: {e}")
        
        # 提交事务
        connection.commit()
        print("\n数据库初始化完成！")
        
        # 验证表是否创建成功
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n创建的表: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise
    
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    init_database()
