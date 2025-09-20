#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_extreme_data(extreme_type, duration_hours=1, sample_rate=10):
    """
    生成极端值温度测试模拟数据
    
    参数:
    - extreme_type: 极端类型 ('min' 或 'max')
    - duration_hours: 测试持续时间（小时）
    - sample_rate: 采样频率（Hz）
    """
    
    # 设置随机数生成器
    rng = np.random.default_rng(seed=42)
    
    # 计算采样点数
    total_samples = int(duration_hours * 3600 * sample_rate)
    
    # 生成时间序列（秒）
    t = np.linspace(0, duration_hours * 3600, total_samples)
    
    if extreme_type == 'min':
        # 最小值数据：基本为0，加入少量噪声
        base_value = 0.0
        noise_amplitude = 0.1  # 很小的噪声幅度
        
        C1 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C2 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C3 = base_value + rng.normal(0, noise_amplitude, total_samples)
        
        # 确保所有值都大于等于0
        C1 = np.maximum(C1, 0.0)
        C2 = np.maximum(C2, 0.0)
        C3 = np.maximum(C3, 0.0)
        
    elif extreme_type == 'max':
        # 最大值数据：基本为10000，加入少量噪声
        base_value = 10000.0
        noise_amplitude = 10.0  # 相对较小的噪声幅度
        
        C1 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C2 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C3 = base_value + rng.normal(0, noise_amplitude, total_samples)
        
        # 确保所有值都小于等于10000
        C1 = np.minimum(C1, 10000.0)
        C2 = np.minimum(C2, 10000.0)
        C3 = np.minimum(C3, 10000.0)
        
    else:
        raise ValueError("extreme_type 必须是 'min' 或 'max'")
    
    # 创建DataFrame
    data = {
        't': t,
        'C1': C1,
        'C2': C2,
        'C3': C3
    }
    
    df = pd.DataFrame(data)
    
    # 对数据进行四舍五入，保留2位小数
    df['t'] = df['t'].round(2)
    df['C1'] = df['C1'].round(2)
    df['C2'] = df['C2'].round(2)
    df['C3'] = df['C3'].round(2)
    
    return df

def main():
    """主函数：生成极端值温度测试CSV文件"""
    
    # 确保uploads目录存在
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"创建目录: {uploads_dir}")
    
    # 生成极端值数据
    extreme_types = [
        ("min", "最小值极端测试", 0.0),
        ("max", "最大值极端测试", 10000.0)
    ]
    
    print("开始生成极端值温度测试模拟数据...")
    print("=" * 50)
    
    for i, (extreme_type, description, expected_value) in enumerate(extreme_types, 1):
        print(f"正在生成文件 {i}/2: {description}...")
        
        # 生成数据
        df = generate_extreme_data(extreme_type, duration_hours=1, sample_rate=10)
        
        # 文件名
        filename = f"temperature_test_extreme_{extreme_type}_{expected_value:.0f}.csv"
        filepath = os.path.join(uploads_dir, filename)
        
        # 保存为CSV文件
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        # 显示文件信息
        print(f"  ✓ 文件: {filename}")
        print(f"  ✓ 路径: {filepath}")
        print(f"  ✓ 数据点数: {len(df):,}")
        print(f"  ✓ 时间范围: {df['t'].min():.2f}s - {df['t'].max():.2f}s")
        print(f"  ✓ C1温度范围: {df['C1'].min():.2f}°C - {df['C1'].max():.2f}°C")
        print(f"  ✓ C2温度范围: {df['C2'].min():.2f}°C - {df['C2'].max():.2f}°C")
        print(f"  ✓ C3温度范围: {df['C3'].min():.2f}°C - {df['C3'].max():.2f}°C")
        print(f"  ✓ 期望值: {expected_value:.0f}°C")
        print()
    
    print("=" * 50)
    print("✅ 所有极端值温度测试数据文件生成完成！")
    print(f"📁 文件保存位置: {os.path.abspath(uploads_dir)}")
    print("\n数据文件说明:")
    print("  文件 1: 最小值极端测试 (接近0°C)")
    print("  文件 2: 最大值极端测试 (接近10000°C)")
    
    print("\n数据格式说明:")
    print("  - 时间列: t (秒)")
    print("  - 数据列: C1, C2, C3 (温度传感器，单位：°C)")
    print("  - 采样频率: 10 Hz")
    print("  - 测试时长: 1 小时")
    print("  - 数据点数: 36,000 点/文件")
    print("  - 最小值: 0°C (带微小噪声)")
    print("  - 最大值: 10000°C (带小幅噪声)")

def generate_specific_extreme_data(extreme_type, file_number, duration_hours=1, sample_rate=10):
    """
    生成特定编号的极端值数据
    
    参数:
    - extreme_type: 'min' 或 'max'
    - file_number: 文件编号 (6-7)
    - duration_hours: 测试持续时间（小时）
    - sample_rate: 采样频率（Hz）
    """
    
    # 设置随机数生成器
    rng = np.random.default_rng(seed=42 + file_number)
    
    # 计算采样点数
    total_samples = int(duration_hours * 3600 * sample_rate)
    
    # 生成时间序列（秒）
    t = np.linspace(0, duration_hours * 3600, total_samples)
    
    if extreme_type == 'min':
        # 最小值数据：基本为0
        base_value = 0.0
        noise_amplitude = 0.05  # 极小的噪声
        
        C1 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C2 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C3 = base_value + rng.normal(0, noise_amplitude, total_samples)
        
        # 确保所有值都大于等于0
        C1 = np.maximum(C1, 0.0)
        C2 = np.maximum(C2, 0.0)
        C3 = np.maximum(C3, 0.0)
        
    else:  # max
        # 最大值数据：基本为10000
        base_value = 10000.0
        noise_amplitude = 5.0  # 较小的噪声
        
        C1 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C2 = base_value + rng.normal(0, noise_amplitude, total_samples)
        C3 = base_value + rng.normal(0, noise_amplitude, total_samples)
        
        # 确保所有值都小于等于10000
        C1 = np.minimum(C1, 10000.0)
        C2 = np.minimum(C2, 10000.0)
        C3 = np.minimum(C3, 10000.0)
    
    # 创建DataFrame
    data = {
        't': t,
        'C1': C1,
        'C2': C2,
        'C3': C3
    }
    
    df = pd.DataFrame(data)
    
    # 对数据进行四舍五入，保留2位小数
    df['t'] = df['t'].round(2)
    df['C1'] = df['C1'].round(2)
    df['C2'] = df['C2'].round(2)
    df['C3'] = df['C3'].round(2)
    
    return df

def generate_additional_extreme_files():
    """生成额外的编号极端值文件（6和7）"""
    
    # 确保uploads目录存在
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"创建目录: {uploads_dir}")
    
    # 生成文件6和7
    extreme_configs = [
        (6, 'min', '最小值极端测试'),
        (7, 'max', '最大值极端测试')
    ]
    
    print("开始生成编号极端值温度测试数据...")
    print("=" * 50)
    
    for file_num, extreme_type, description in extreme_configs:
        print(f"正在生成文件 {file_num}: {description}...")
        
        # 生成数据
        df = generate_specific_extreme_data(extreme_type, file_num, duration_hours=1, sample_rate=10)
        
        # 文件名
        expected_value = 0 if extreme_type == 'min' else 10000
        filename = f"temperature_test_{file_num:02d}_{description.replace(' ', '_')}.csv"
        filepath = os.path.join(uploads_dir, filename)
        
        # 保存为CSV文件
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        # 显示文件信息
        print(f"  ✓ 文件: {filename}")
        print(f"  ✓ 路径: {filepath}")
        print(f"  ✓ 数据点数: {len(df):,}")
        print(f"  ✓ 时间范围: {df['t'].min():.2f}s - {df['t'].max():.2f}s")
        print(f"  ✓ C1温度范围: {df['C1'].min():.2f}°C - {df['C1'].max():.2f}°C")
        print(f"  ✓ C2温度范围: {df['C2'].min():.2f}°C - {df['C2'].max():.2f}°C")
        print(f"  ✓ C3温度范围: {df['C3'].min():.2f}°C - {df['C3'].max():.2f}°C")
        print()
    
    print("=" * 50)
    print("✅ 编号极端值温度测试数据文件生成完成！")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--numbered':
        # 生成编号文件
        generate_additional_extreme_files()
    else:
        # 生成常规极端值文件
        main()
