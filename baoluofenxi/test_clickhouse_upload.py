#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClickHouse连接和数据上传测试脚本
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.clickhouse_manager import get_clickhouse_manager
from database_config import db_config

def test_clickhouse_connection():
    """测试ClickHouse连接"""
    print("=== 测试ClickHouse连接 ===")
    
    try:
        # 获取ClickHouse管理器
        ch_manager = get_clickhouse_manager()
        print("✓ ClickHouse连接成功")
        
        # 测试数据库是否存在
        config = db_config.get_clickhouse_config()
        print(f"✓ 使用数据库: {config['database']}")
        
        return ch_manager
        
    except Exception as e:
        print(f"✗ ClickHouse连接失败: {e}")
        return None

def test_table_creation():
    """测试表创建"""
    print("\n=== 测试表创建 ===")
    
    ch_manager = get_clickhouse_manager()
    
    # 测试表参数
    table_name = f"test_exp_{int(datetime.now().timestamp())}"
    time_column = "t"
    data_columns = ["C1", "C2", "C3"]
    
    try:
        # 创建表
        success = ch_manager.create_timeseries_table(table_name, time_column, data_columns)
        
        if success:
            print(f"✓ 表创建成功: {table_name}")
            
            # 检查表是否存在
            exists = ch_manager.table_exists(table_name)
            print(f"✓ 表存在检查: {exists}")
            
            # 获取表信息
            table_info = ch_manager.get_table_info(table_name)
            print(f"✓ 表信息: {table_info.get('row_count', 0)} 行")
            
            return table_name
        else:
            print("✗ 表创建失败")
            return None
            
    except Exception as e:
        print(f"✗ 表创建出错: {e}")
        return None

def test_data_insertion(table_name):
    """测试数据插入"""
    print("\n=== 测试数据插入 ===")
    
    ch_manager = get_clickhouse_manager()
    
    try:
        # 创建测试数据
        n_points = 100
        t = np.linspace(0, 10, n_points)
        rng = np.random.default_rng(42)  # 使用固定种子确保可重复性
        data = {
            't': t,
            'C1': np.sin(t) + rng.normal(0, 0.1, n_points),
            'C2': np.cos(t) + rng.normal(0, 0.1, n_points),
            'C3': np.sin(2 * t) + rng.normal(0, 0.1, n_points)
        }
        
        df = pd.DataFrame(data)
        print(f"✓ 生成测试数据: {len(df)} 行")
        
        # 插入数据
        result = ch_manager.insert_dataframe(df, table_name, 't')
        
        if result['success']:
            print(f"✓ 数据插入成功: {result['message']}")
            print(f"  - 插入行数: {result['row_count']}")
            print(f"  - 表名: {result['table_name']}")
            
            return True
        else:
            print(f"✗ 数据插入失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"✗ 数据插入出错: {e}")
        return False

def test_data_query(table_name):
    """测试数据查询"""
    print("\n=== 测试数据查询 ===")
    
    ch_manager = get_clickhouse_manager()
    
    try:
        # 查询所有数据
        df = ch_manager.query_data(table_name, 't')
        print(f"✓ 查询所有数据: {len(df)} 行")
        print(f"  - 列: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"  - 时间范围: {df['t'].min():.2f} ~ {df['t'].max():.2f}")
            print("  - 前5行:")
            print(df.head().to_string(index=False, float_format='%.3f'))
        
        # 查询特定列
        df_subset = ch_manager.query_data(table_name, 't', columns=['t', 'C1'])
        print(f"✓ 查询特定列: {len(df_subset)} 行, 列: {list(df_subset.columns)}")
        
        # 查询时间范围
        df_range = ch_manager.query_data(table_name, 't', time_range=(2.0, 5.0))
        print(f"✓ 查询时间范围 [2.0, 5.0]: {len(df_range)} 行")
        
        # 限制行数查询
        df_limited = ch_manager.query_data(table_name, 't', limit=10)
        print(f"✓ 限制行数查询: {len(df_limited)} 行")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据查询出错: {e}")
        return False

def test_table_cleanup(table_name):
    """测试表清理"""
    print("\n=== 测试表清理 ===")
    
    ch_manager = get_clickhouse_manager()
    
    try:
        success = ch_manager.drop_table(table_name)
        
        if success:
            print(f"✓ 表删除成功: {table_name}")
            
            # 确认表已删除
            exists = ch_manager.table_exists(table_name)
            print(f"✓ 表删除确认: 存在={exists}")
            
            return True
        else:
            print(f"✗ 表删除失败: {table_name}")
            return False
            
    except Exception as e:
        print(f"✗ 表删除出错: {e}")
        return False

def main():
    """主测试流程"""
    print("ClickHouse数据上传功能测试")
    print("=" * 50)
    
    # 测试连接
    ch_manager = test_clickhouse_connection()
    if not ch_manager:
        return
    
    # 测试表创建
    table_name = test_table_creation()
    if not table_name:
        return
    
    try:
        # 测试数据插入
        if not test_data_insertion(table_name):
            return
        
        # 测试数据查询
        if not test_data_query(table_name):
            return
        
        print("\n=== 所有测试通过! ===")
        print("ClickHouse数据上传功能正常工作")
        
    finally:
        # 清理测试表
        if table_name:
            test_table_cleanup(table_name)

if __name__ == "__main__":
    main()
