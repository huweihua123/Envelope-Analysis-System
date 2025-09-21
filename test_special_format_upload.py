#!/usr/bin/env python3
"""
测试特殊格式文件上传功能
"""
import requests
import sys
import os


def test_special_format_upload():
    """测试特殊格式文件上传"""

    # 服务器配置
    base_url = "http://127.0.0.1:5000"
    experiment_type_id = 1  # 假设试验类型ID为1

    # 测试文件路径
    test_file_path = "/Users/huweihua/baoluofenxi/uploads/temperature_test_merged_01_稳定升温过程.csv"

    if not os.path.exists(test_file_path):
        print(f"测试文件不存在: {test_file_path}")
        return False

    # 构建上传请求
    url = f"{base_url}/api/envelope/{experiment_type_id}/temp-upload"

    # 准备文件和参数
    with open(test_file_path, "rb") as f:
        files = {"file": f}
        data = {"format_type": "special", "separator": " ", "skip_rows": "0"}

        print(f"正在测试特殊格式上传...")
        print(f"文件: {test_file_path}")
        print(f"参数: {data}")

        try:
            response = requests.post(url, files=files, data=data, timeout=30)

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ 特殊格式上传成功!")
                    print(f"临时数据ID: {result['data']['temp_data_id']}")
                    print(f"数据行数: {result['data']['row_count']}")
                    print(f"列名: {result['data']['columns']}")
                    print(f"时间范围: {result['data']['time_range']}")
                    return True
                else:
                    print(f"❌ 上传失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False


def test_standard_format_upload():
    """测试标准格式文件上传（作为对比）"""

    base_url = "http://127.0.0.1:5000"
    experiment_type_id = 1
    test_file_path = "/Users/huweihua/baoluofenxi/uploads/temperature_test_merged_01_稳定升温过程.csv"

    if not os.path.exists(test_file_path):
        print(f"测试文件不存在: {test_file_path}")
        return False

    url = f"{base_url}/api/envelope/{experiment_type_id}/temp-upload"

    with open(test_file_path, "rb") as f:
        files = {"file": f}
        # 不传任何格式参数，应该按标准格式处理

        print(f"正在测试标准格式上传...")
        print(f"文件: {test_file_path}")

        try:
            response = requests.post(url, files=files, timeout=30)

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ 标准格式上传成功!")
                    return True
                else:
                    print(f"❌ 上传失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False


if __name__ == "__main__":
    print("开始测试特殊格式文件上传功能...")
    print("=" * 50)

    # 先测试标准格式（预期会失败，因为这是特殊格式文件）
    print("\n1. 测试标准格式处理（预期失败）:")
    test_standard_format_upload()

    print("\n" + "=" * 50)

    # 再测试特殊格式（预期成功）
    print("\n2. 测试特殊格式处理（预期成功）:")
    test_special_format_upload()

    print("\n测试完成!")
