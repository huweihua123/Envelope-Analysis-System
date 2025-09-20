#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_temperature_data(file_number, duration_hours=1, sample_rate=10):
    """
    生成温度测试模拟数据
    
    参数:
    - file_number: 文件编号 (1-5)
    - duration_hours: 测试持续时间（小时）
    - sample_rate: 采样频率（Hz）
    """
    
    # 设置随机数生成器
    rng = np.random.default_rng(seed=42 + file_number)
    
    # 计算采样点数
    total_samples = int(duration_hours * 3600 * sample_rate)
    
    # 生成时间序列（秒）
    t = np.linspace(0, duration_hours * 3600, total_samples)
    
    # 为每个文件设置不同的温度特性
    if file_number == 1:
        # 文件1：稳定升温过程
        base_temp = 20.0
        temp_rise = 15.0  # 15度升温
        C1 = base_temp + (temp_rise * t / (duration_hours * 3600)) + rng.normal(0, 0.2, total_samples)
        C2 = base_temp + (temp_rise * t / (duration_hours * 3600)) + rng.normal(0, 0.15, total_samples) + 2.0
        C3 = base_temp + (temp_rise * t / (duration_hours * 3600)) + rng.normal(0, 0.25, total_samples) - 1.5
        
    elif file_number == 2:
        # 文件2：周期性温度变化
        base_temp = 25.0
        amplitude = 10.0
        period = duration_hours * 3600 / 3  # 3个周期
        C1 = base_temp + amplitude * np.sin(2 * np.pi * t / period) + rng.normal(0, 0.3, total_samples)
        C2 = base_temp + amplitude * np.sin(2 * np.pi * t / period + np.pi/4) + rng.normal(0, 0.25, total_samples)
        C3 = base_temp + amplitude * np.sin(2 * np.pi * t / period + np.pi/2) + rng.normal(0, 0.2, total_samples)
        
    elif file_number == 3:
        # 文件3：阶跃响应
        base_temp = 22.0
        target_temp = 40.0
        step_time = duration_hours * 3600 * 0.3  # 30%时刻发生阶跃
        
        C1 = np.where(t < step_time, 
                     base_temp + rng.normal(0, 0.2, total_samples),
                     target_temp * (1 - np.exp(-(t - step_time) / 300)) + base_temp + rng.normal(0, 0.3, total_samples))
        
        C2 = np.where(t < step_time,
                     base_temp + 1.5 + rng.normal(0, 0.18, total_samples),
                     (target_temp + 1.5) * (1 - np.exp(-(t - step_time) / 350)) + base_temp + rng.normal(0, 0.28, total_samples))
        
        C3 = np.where(t < step_time,
                     base_temp - 0.8 + rng.normal(0, 0.22, total_samples),
                     (target_temp - 0.8) * (1 - np.exp(-(t - step_time) / 280)) + base_temp + rng.normal(0, 0.32, total_samples))
        
    elif file_number == 4:
        # 文件4：冷却过程
        initial_temp = 60.0
        ambient_temp = 18.0
        cooling_constant = 800.0  # 冷却时间常数
        
        C1 = ambient_temp + (initial_temp - ambient_temp) * np.exp(-t / cooling_constant) + rng.normal(0, 0.4, total_samples)
        C2 = ambient_temp + (initial_temp - 2.0 - ambient_temp) * np.exp(-t / (cooling_constant * 1.1)) + rng.normal(0, 0.35, total_samples)
        C3 = ambient_temp + (initial_temp + 1.5 - ambient_temp) * np.exp(-t / (cooling_constant * 0.9)) + rng.normal(0, 0.45, total_samples)
        
    else:  # file_number == 5
        # 文件5：复杂的多段温度变化
        base_temp = 30.0
        
        # 第一段：升温
        segment1 = t <= duration_hours * 3600 * 0.4
        temp1 = base_temp + 20 * (t / (duration_hours * 3600 * 0.4))
        
        # 第二段：保温
        segment2 = (t > duration_hours * 3600 * 0.4) & (t <= duration_hours * 3600 * 0.7)
        temp2 = base_temp + 20
        
        # 第三段：降温
        temp3 = (base_temp + 20) - 15 * ((t - duration_hours * 3600 * 0.7) / (duration_hours * 3600 * 0.3))
        
        base_profile = np.where(segment1, temp1, np.where(segment2, temp2, temp3))
        
        C1 = base_profile + rng.normal(0, 0.5, total_samples)
        C2 = base_profile + 2.5 + rng.normal(0, 0.4, total_samples)
        C3 = base_profile - 1.8 + rng.normal(0, 0.6, total_samples)
    
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
    """主函数：生成5个温度测试CSV文件"""
    
    # 确保uploads目录存在
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"创建目录: {uploads_dir}")
    
    # 生成5个不同的温度测试数据文件
    file_descriptions = [
        "稳定升温过程",
        "周期性温度变化",
        "阶跃响应测试",
        "冷却过程测试",
        "多段温度变化"
    ]
    
    print("开始生成温度测试模拟数据...")
    print("=" * 50)
    
    for i in range(1, 6):
        print(f"正在生成文件 {i}/5: {file_descriptions[i-1]}...")
        
        # 生成数据
        df = generate_temperature_data(i, duration_hours=1, sample_rate=10)
        
        # 文件名
        filename = f"temperature_test_{i:02d}_{file_descriptions[i-1].replace('/', '_')}.csv"
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
    print("✅ 所有温度测试数据文件生成完成！")
    print(f"📁 文件保存位置: {os.path.abspath(uploads_dir)}")
    print("\n数据文件说明:")
    for i, desc in enumerate(file_descriptions, 1):
        print(f"  文件 {i}: {desc}")
    
    print("\n数据格式说明:")
    print("  - 时间列: t (秒)")
    print("  - 数据列: C1, C2, C3 (温度传感器，单位：°C)")
    print("  - 采样频率: 10 Hz")
    print("  - 测试时长: 1 小时")
    print("  - 数据点数: 36,000 点/文件")

if __name__ == "__main__":
    main()
