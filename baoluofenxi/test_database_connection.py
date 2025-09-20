#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClickHouse连接测试脚本
测试与ClickHouse数据库的连接是否正常
"""

import sys
import traceback
from database_config import db_config

def test_clickhouse_connection():
    """测试ClickHouse连接"""
    print("=" * 60)
    print("测试ClickHouse连接")
    print("=" * 60)
    
    try:
        # 获取ClickHouse配置
        ch_config = db_config.get_clickhouse_config()
        print(f"ClickHouse配置:")
        print(f"  主机: {ch_config['host']}")
        print(f"  HTTP端口: {ch_config['http_port']}")
        print(f"  TCP端口: {ch_config['tcp_port']}")
        print(f"  用户名: {ch_config['user']}")
        print(f"  数据库: {ch_config['database']}")
        print()
        
        # 尝试导入clickhouse_driver
        try:
            from clickhouse_driver import Client
            print("✓ clickhouse_driver 模块导入成功")
        except ImportError:
            print("✗ clickhouse_driver 模块未安装")
            print("请运行: pip install clickhouse-driver")
            return False
            
        # 创建ClickHouse客户端连接
        print("正在连接ClickHouse...")
        client = Client(
            host=ch_config['host'],
            port=ch_config['tcp_port'],
            user=ch_config['user'],
            password=ch_config['password'],
            database=ch_config['database'],
            send_receive_timeout=ch_config['send_receive_timeout'],
            sync_request_timeout=ch_config['sync_request_timeout']
        )
        
        # 测试查询
        result = client.execute('SELECT version()')
        print(f"✓ ClickHouse连接成功!")
        print(f"  版本: {result[0][0]}")
        
        # 测试数据库权限
        result = client.execute('SHOW DATABASES')
        databases = [row[0] for row in result]
        print(f"  可访问的数据库: {', '.join(databases)}")
        
        # 测试当前数据库的表
        result = client.execute('SHOW TABLES')
        tables = [row[0] for row in result]
        print(f"  当前数据库中的表: {', '.join(tables) if tables else '无'}")
        
        return True
        
    except Exception as e:
        print(f"✗ ClickHouse连接失败: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

def test_mysql_connection():
    """测试MySQL连接"""
    print("=" * 60)
    print("测试MySQL连接")
    print("=" * 60)
    
    try:
        # 获取MySQL配置
        mysql_config = db_config.get_mysql_config()
        print(f"MySQL配置:")
        print(f"  主机: {mysql_config['host']}")
        print(f"  端口: {mysql_config['port']}")
        print(f"  用户名: {mysql_config['user']}")
        print(f"  数据库: {mysql_config['database']}")
        print()
        
        # 尝试导入pymysql
        try:
            import pymysql
            print("✓ pymysql 模块导入成功")
        except ImportError:
            print("✗ pymysql 模块未安装")
            print("请运行: pip install pymysql")
            return False
            
        # 创建MySQL连接
        print("正在连接MySQL...")
        connection = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            charset=mysql_config['charset']
        )
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            result = cursor.fetchone()
            print(f"✓ MySQL连接成功!")
            print(f"  版本: {result[0]}")
            
            # 显示数据库中的表
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            print(f"  数据库中的表: {', '.join(table_names) if table_names else '无'}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL连接失败: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("包络分析系统 - 数据库连接测试")
    print("=" * 60)
    print()
    
    # 测试MySQL连接
    mysql_ok = test_mysql_connection()
    print()
    
    # 测试ClickHouse连接
    clickhouse_ok = test_clickhouse_connection()
    print()
    
    # 总结
    print("=" * 60)
    print("测试结果总结:")
    print(f"  MySQL连接: {'✓ 正常' if mysql_ok else '✗ 失败'}")
    print(f"  ClickHouse连接: {'✓ 正常' if clickhouse_ok else '✗ 失败'}")
    print("=" * 60)
    
    if mysql_ok and clickhouse_ok:
        print("🎉 所有数据库连接测试通过！")
        return 0
    else:
        print("⚠️  存在数据库连接问题，请检查配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
