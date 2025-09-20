#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClickHouse认证测试脚本
测试不同的用户名和密码组合
"""

import requests
import json
from database_config import db_config

def test_clickhouse_auth():
    """测试ClickHouse认证"""
    print("=" * 60)
    print("测试ClickHouse认证")
    print("=" * 60)
    
    # 获取配置
    ch_config = db_config.get_clickhouse_config()
    host = ch_config['host']
    http_port = ch_config['http_port']
    
    base_url = f"http://{host}:{http_port}"
    
    print(f"测试服务器: {base_url}")
    print()
    
    # 测试场景
    test_cases = [
        {"user": "default", "password": "", "name": "默认用户无密码"},
        {"user": "default", "password": "123456", "name": "默认用户有密码"},
        {"user": "admin", "password": "pWSkms4JkBGF", "name": "当前配置的admin用户"},
        {"user": "root", "password": "123456", "name": "root用户"},
        {"user": "", "password": "", "name": "无认证"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. 测试 {case['name']}")
        print(f"   用户名: '{case['user']}', 密码: '{case['password']}'")
        
        try:
            # 准备认证参数
            auth_params = {}
            if case['user'] or case['password']:
                auth_params['user'] = case['user']
                auth_params['password'] = case['password']
            
            # 测试简单查询
            response = requests.get(
                f"{base_url}/",
                params={**auth_params, 'query': 'SELECT version()'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✓ 认证成功! 服务器响应: {response.text.strip()}")
                
                # 如果成功，测试更多信息
                try:
                    # 获取当前用户信息
                    user_response = requests.get(
                        f"{base_url}/",
                        params={**auth_params, 'query': 'SELECT user()'},
                        timeout=10
                    )
                    if user_response.status_code == 200:
                        print(f"   当前用户: {user_response.text.strip()}")
                        
                    # 获取数据库列表
                    db_response = requests.get(
                        f"{base_url}/",
                        params={**auth_params, 'query': 'SHOW DATABASES'},
                        timeout=10
                    )
                    if db_response.status_code == 200:
                        databases = db_response.text.strip().split('\n')
                        print(f"   可用数据库: {', '.join(databases)}")
                        
                except Exception as e:
                    print(f"   获取详细信息失败: {e}")
                
                print()
                return case  # 返回成功的配置
                
            else:
                print(f"   ✗ 认证失败! HTTP状态: {response.status_code}")
                if response.text:
                    print(f"   错误信息: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 连接失败: {e}")
        except Exception as e:
            print(f"   ✗ 未知错误: {e}")
            
        print()
    
    print("所有认证方式都失败了")
    return None

def test_with_curl_equivalent():
    """使用类似curl的方式测试"""
    print("=" * 60)
    print("使用HTTP直接测试")
    print("=" * 60)
    
    ch_config = db_config.get_clickhouse_config()
    host = ch_config['host']
    http_port = ch_config['http_port']
    
    base_url = f"http://{host}:{http_port}"
    
    print(f"测试URL: {base_url}")
    
    # 无认证测试
    print("1. 无认证测试:")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   /ping 响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   /ping 失败: {e}")
        
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   / 响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   / 失败: {e}")

if __name__ == "__main__":
    print("开始ClickHouse认证诊断...")
    print()
    
    # 首先测试HTTP直连
    test_with_curl_equivalent()
    print()
    
    # 测试认证
    success_config = test_clickhouse_auth()
    
    if success_config:
        print("=" * 60)
        print("建议更新配置:")
        print("=" * 60)
        print(f"用户名: {success_config['user']}")
        print(f"密码: {success_config['password']}")
        print()
        print("请更新 database_config.ini 文件中的 [clickhouse] 部分")
    else:
        print("=" * 60)
        print("建议检查项:")
        print("=" * 60)
        print("1. 确认ClickHouse服务正在运行")
        print("2. 检查防火墙设置")
        print("3. 检查ClickHouse用户配置")
        print("4. 查看ClickHouse服务日志")
