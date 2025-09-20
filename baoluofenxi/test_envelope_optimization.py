#!/usr/bin/env python3
"""
包络计算优化测试脚本
测试新的采样配置功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_processor import DataProcessor

def test_envelope_calculation():
    """测试包络计算的采样和完整数据模式"""
    print("=== 包络计算优化测试 ===")
    
    processor = DataProcessor()
    
    # 测试参数
    experiment_type_id = 1
    selected_columns = ['temperature', 'pressure']
    
    # 测试1: 采样模式 (200点)
    print("\n测试1: 采样模式 (200点)")
    try:
        result_sampled = processor.calculate_envelope_for_columns(
            experiment_type_id, 
            selected_columns, 
            sampling_points=200, 
            use_sampling=True
        )
        
        if 'error' in result_sampled:
            print(f"采样模式测试失败: {result_sampled['error']}")
        else:
            print(f"采样模式测试成功:")
            print(f"- 数据点数: {result_sampled.get('sampling_points', 0)}")
            print(f"- 原始点数: {result_sampled.get('original_points', 0)}")
            print(f"- 处理模式: {result_sampled.get('sampling_method', 'unknown')}")
            print(f"- 数据集数量: {result_sampled.get('data_count', 0)}")
            
    except Exception as e:
        print(f"采样模式测试异常: {e}")
    
    # 测试2: 完整数据模式
    print("\n测试2: 完整数据模式")
    try:
        result_full = processor.calculate_envelope_for_columns(
            experiment_type_id, 
            selected_columns, 
            use_sampling=False
        )
        
        if 'error' in result_full:
            print(f"完整数据模式测试失败: {result_full['error']}")
        else:
            print(f"完整数据模式测试成功:")
            print(f"- 数据点数: {result_full.get('sampling_points', 0)}")
            print(f"- 原始点数: {result_full.get('original_points', 0)}")
            print(f"- 处理模式: {result_full.get('sampling_method', 'unknown')}")
            print(f"- 数据集数量: {result_full.get('data_count', 0)}")
            
    except Exception as e:
        print(f"完整数据模式测试异常: {e}")
    
    # 测试3: 不同采样点数
    print("\n测试3: 不同采样点数 (50点)")
    try:
        result_small = processor.calculate_envelope_for_columns(
            experiment_type_id, 
            selected_columns, 
            sampling_points=50, 
            use_sampling=True
        )
        
        if 'error' in result_small:
            print(f"小采样测试失败: {result_small['error']}")
        else:
            print(f"小采样测试成功:")
            print(f"- 数据点数: {result_small.get('sampling_points', 0)}")
            print(f"- 原始点数: {result_small.get('original_points', 0)}")
            print(f"- 处理模式: {result_small.get('sampling_method', 'unknown')}")
            
    except Exception as e:
        print(f"小采样测试异常: {e}")

def test_api_compatibility():
    """测试API兼容性"""
    print("\n=== API兼容性测试 ===")
    
    processor = DataProcessor()
    
    # 测试旧API兼容性
    experiment_type_id = 1
    
    try:
        result = processor.calculate_envelope(experiment_type_id)
        if 'error' in result:
            print(f"旧API兼容性测试失败: {result['error']}")
        else:
            print("旧API兼容性测试通过")
    except Exception as e:
        print(f"旧API兼容性测试异常: {e}")

if __name__ == "__main__":
    test_envelope_calculation()
    test_api_compatibility()
    print("\n=== 测试完成 ===")
