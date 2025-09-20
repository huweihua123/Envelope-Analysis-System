# 包络分析系统 API 文档

## 概述
本系统已改为前后端分离架构，所有API接口均以 `/api` 开头，返回JSON格式数据。

## 基础信息
- 基础URL: `http://localhost:5000/api`
- Content-Type: `application/json`
- 支持CORS跨域请求

## API 接口列表

### 1. 实验类型管理

#### 获取所有实验类型
```
GET /api/experiment-types
```

**响应示例:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "温度测试",
            "description": "温度变化实验",
            "time_column": "t",
            "data_columns": ["C1", "C2", "C3"],
            "created_at": "2023-12-01T10:00:00"
        }
    ]
}
```

#### 创建实验类型
```
POST /api/experiment-types
```

**请求体:**
```json
{
    "name": "新实验类型",
    "description": "实验描述",
    "time_column": "t",
    "data_columns": ["C1", "C2", "C3"]
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "试验类型 \"新实验类型\" 创建成功",
    "data": {
        "id": 2,
        "name": "新实验类型",
        "description": "实验描述",
        "time_column": "t",
        "data_columns": ["C1", "C2", "C3"],
        "created_at": "2023-12-01T10:05:00"
    }
}
```

#### 删除实验类型
```
DELETE /api/experiment-types/{type_id}
```

**响应示例:**
```json
{
    "success": true,
    "message": "试验类型 \"温度测试\" 删除成功"
}
```

### 2. 数据上传

#### 上传实验数据
```
POST /api/upload/{experiment_type_id}
```

**请求类型:** `multipart/form-data`

**表单字段:**
- `file`: 数据文件 (CSV/Excel)
- `data_name`: 数据名称

**响应示例:**
```json
{
    "success": true,
    "message": "上传成功",
    "data_id": 123
}
```

#### 预览上传文件
```
POST /api/preview/{experiment_type_id}
```

**请求类型:** `multipart/form-data`

**表单字段:**
- `file`: 要预览的文件

**响应示例:**
```json
{
    "success": true,
    "preview": {
        "file_info": {
            "name": "test_data.csv",
            "rows_preview": 10,
            "total_columns": 4,
            "columns": ["t", "C1", "C2", "C3"]
        },
        "validation": {
            "valid": true,
            "message": "数据格式正确"
        },
        "data_preview": [
            {"t": 0.0, "C1": 10.5, "C2": 12.3, "C3": 8.9},
            {"t": 0.1, "C1": 11.2, "C2": 12.8, "C3": 9.1}
        ]
    }
}
```

### 3. 包络分析

#### 获取包络分析信息
```
GET /api/envelope/{experiment_type_id}/info
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "experiment_type": {
            "id": 1,
            "name": "温度测试",
            "data_columns": ["C1", "C2", "C3"]
        },
        "experiment_data": [
            {
                "id": 1,
                "data_name": "测试数据1",
                "row_count": 1000
            }
        ],
        "envelope_settings": {
            "selected_columns": ["C1", "C3"],
            "time_range_start": 0.0,
            "time_range_end": 10.0
        }
    }
}
```

#### 获取/设置包络配置
```
GET /api/envelope/{experiment_type_id}/settings
POST /api/envelope/{experiment_type_id}/settings
```

**POST请求体:**
```json
{
    "selected_columns": ["C1", "C3"],
    "time_range_start": 0.0,
    "time_range_end": 10.0
}
```

#### 获取包络数据
```
GET /api/envelope/{experiment_type_id}/data
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "time_points": [0.0, 0.1, 0.2, ...],
        "envelopes": {
            "C1": {
                "upper": [11.5, 12.1, 12.8, ...],
                "lower": [9.2, 9.8, 10.1, ...]
            },
            "C3": {
                "upper": [10.5, 11.2, 11.9, ...],
                "lower": [8.1, 8.7, 9.2, ...]
            }
        }
    }
}
```

### 4. 数据管理

#### 获取数据管理信息
```
GET /api/data-management/{experiment_type_id}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "experiment_type": {
            "id": 1,
            "name": "温度测试"
        },
        "experiment_data": [
            {
                "id": 1,
                "data_name": "测试数据1",
                "file_name": "test_data.csv",
                "row_count": 1000,
                "upload_time": "2023-12-01T10:00:00",
                "status": "active"
            }
        ]
    }
}
```

## 错误响应格式

所有API在出错时都会返回统一格式的错误响应：

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

HTTP状态码：
- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## CORS配置

系统已配置CORS支持，允许所有域名的跨域请求。生产环境中建议限制到特定的前端域名。

## 认证

当前版本暂未实现认证机制。如需要，可以考虑实现JWT或其他认证方式。
