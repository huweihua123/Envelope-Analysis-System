# 包络分析系统 (Envelope Analysis System)

<div align="center">
  <h3>专业的实验数据包络分析平台</h3>
  <p>基于 Flask + Vue.js 的全栈数据分析解决方案</p>
  
  ![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
  ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green)
  ![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
  ![License](https://img.shields.io/badge/License-MIT-yellow)
</div>

## 📋 项目概述

包络分析系统是一个专门用于实验数据分析的Web应用平台，支持时间序列数据的包络计算、可视化展示和对比分析。系统采用前后端分离架构，提供了完整的数据管理和分析工具链。

### 🎯 主要功能

- **实验类型管理**: 创建和管理不同类型的实验配置
- **数据上传与预览**: 支持CSV/Excel文件上传，实时数据预览
- **包络分析**: 自动计算数据包络，支持多种采样策略
- **数据对比**: 临时数据与历史数据的包络对比分析
- **可视化图表**: 基于ECharts的交互式数据可视化
- **数据管理**: 历史数据标记、软删除等数据管理功能

## 🏗️ 系统架构

```
├── baoluofenxi/                 # 后端Flask API
│   ├── app.py                   # 主应用入口
│   ├── models/                  # 数据模型
│   ├── services/                # 业务逻辑服务
│   └── config.py               # 配置文件
├── baoluofenxi-frontend/        # 前端Vue.js应用
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API接口
│   │   └── components/         # 公共组件
└── uploads/                     # 文件上传目录
```

## 🛠️ 技术栈

### 后端技术
- **Python 3.8+** - 核心开发语言
- **Flask 2.3.3** - Web应用框架
- **SQLAlchemy** - ORM数据库映射
- **MySQL** - 主数据库存储
- **ClickHouse** - 时序数据分析存储
- **Pandas/NumPy** - 数据处理与科学计算

### 前端技术
- **Vue.js 3.x** - 渐进式前端框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue 3组件库
- **ECharts** - 数据可视化图表库
- **Vue Router** - 前端路由管理
- **Axios** - HTTP客户端

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- ClickHouse (可选，用于大数据量处理)

### 后端安装

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd baoluofenxi
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   cd baoluofenxi
   pip install -r requirements.txt
   ```

4. **配置数据库**
   ```bash
   # 复制配置文件模板
   cp database_config.ini.example database_config.ini
   
   # 编辑配置文件，填入你的数据库连接信息
   # 初始化数据库
   python init_database.py
   ```

5. **启动后端服务**
   ```bash
   python app.py
   ```
   后端服务将在 `http://localhost:5005` 启动

### 前端安装

1. **进入前端目录**
   ```bash
   cd baoluofenxi-frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   # 或使用 yarn
   yarn install
   ```

3. **启动开发服务**
   ```bash
   npm run dev
   # 或
   yarn dev
   ```
   前端应用将在 `http://localhost:5173` 启动

## 🔧 配置说明

### 数据库配置

在 `baoluofenxi/database_config.ini` 中配置数据库连接：

```ini
[mysql]
host = localhost
port = 3306
user = your_username
password = your_password
database = envelope_analysis

[clickhouse]
host = localhost
port = 9000
user = default
password = 
database = envelope_analysis
```

### 应用配置

在 `baoluofenxi/config.py` 中可以修改应用配置：

```python
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## 📊 API 文档

系统提供完整的RESTful API，所有接口以 `/api` 开头：

### 实验类型管理
- `GET /api/experiment-types` - 获取所有实验类型
- `POST /api/experiment-types` - 创建新的实验类型
- `DELETE /api/experiment-types/{id}` - 删除实验类型

### 数据管理
- `POST /api/upload/{experiment_type_id}` - 上传实验数据
- `GET /api/experiment-data/{experiment_type_id}` - 获取实验数据列表
- `DELETE /api/experiment-data/{data_id}` - 删除实验数据

### 包络分析
- `POST /api/envelope/{experiment_type_id}/envelope` - 获取包络数据
- `POST /api/envelope/{experiment_type_id}/compare` - 包络对比分析
- `POST /api/envelope/{experiment_type_id}/temp-upload` - 上传临时对比数据

详细的API文档请参考：[API_DOCUMENTATION.md](baoluofenxi/API_DOCUMENTATION.md)

## 📁 项目结构

```
baoluofenxi/
├── app.py                      # Flask应用主文件
├── config.py                   # 应用配置
├── database.py                 # 数据库初始化和工具
├── database_config.py          # 数据库配置管理
├── init_database.py            # 数据库初始化脚本
├── create_tables.sql           # 数据库表结构
├── requirements.txt            # Python依赖
├── models/
│   └── models.py              # 数据模型定义
├── services/
│   ├── clickhouse_manager.py  # ClickHouse管理服务
│   └── data_processor.py      # 数据处理服务
└── uploads/                    # 文件上传目录

baoluofenxi-frontend/
├── index.html                  # HTML入口文件
├── package.json               # NPM包配置
├── vite.config.ts             # Vite构建配置
├── src/
│   ├── App.vue                # 根组件
│   ├── main.ts                # 应用入口
│   ├── api/                   # API接口定义
│   │   ├── index.ts
│   │   ├── experimentType.ts
│   │   ├── data.ts
│   │   └── envelope.ts
│   ├── views/                 # 页面组件
│   │   ├── CreateExperimentType.vue
│   │   ├── DataManagement.vue
│   │   └── ...
│   ├── router/                # 路由配置
│   │   └── index.ts
│   └── types/                 # TypeScript类型定义
│       └── index.ts
└── public/
    └── icon.png
```

## 🎮 使用指南

### 1. 创建实验类型
1. 访问系统首页，点击"创建实验类型"
2. 填写实验类型名称、描述
3. 配置时间列名称（如：t, time, timestamp）
4. 添加数据列名称（如：C1, C2, C3）

### 2. 上传实验数据
1. 选择已创建的实验类型
2. 上传CSV或Excel格式的数据文件
3. 预览数据格式，确认列映射正确
4. 保存数据到系统

### 3. 包络分析
1. 进入包络分析页面
2. 选择要分析的数据列
3. 配置采样设置（可选）
4. 查看生成的包络图表

### 4. 数据对比
1. 上传临时对比数据
2. 选择对比的数据列
3. 系统自动计算并展示包络对比结果
4. 可将满意的对比数据保存为历史数据

## 🔍 数据格式要求

### 支持的文件格式
- CSV文件 (.csv)
- Excel文件 (.xlsx, .xls)

### 数据格式示例
```csv
t,C1,C2,C3
0.0,10.5,12.3,8.9
0.1,10.7,12.1,9.2
0.2,10.9,11.8,9.5
...
```

### 数据要求
- 必须包含时间列（列名可配置）
- 数据列必须为数值类型
- 时间列应为递增序列
- 支持的数据量：建议单文件不超过100万行

## 🐛 故障排除

### 常见问题

**1. 数据库连接失败**
```bash
# 检查MySQL服务是否启动
systemctl status mysql  # Linux
brew services list | grep mysql  # Mac

# 验证数据库配置
python test_database_connection.py
```

**2. ClickHouse连接问题**
```bash
# 启动ClickHouse服务
./start_clickhouse.sh  # Linux/Mac
./start_clickhouse.ps1 # Windows

# 测试连接
python test_clickhouse_auth.py
```

**3. 前端API调用失败**
- 检查后端服务是否正常启动 (端口5005)
- 确认CORS配置正确
- 查看浏览器控制台错误信息

**4. 文件上传失败**
- 检查文件大小是否超过限制(16MB)
- 确认文件格式正确
- 检查uploads目录权限

## 🧪 测试

### 后端测试
```bash
cd baoluofenxi

# 数据库连接测试
python test_database_connection.py

# ClickHouse连接测试  
python test_clickhouse_auth.py

# 文件上传测试
python test_clickhouse_upload.py
```

### 前端测试
```bash
cd baoluofenxi-frontend

# 运行单元测试（如果有）
npm test

# 构建测试
npm run build
```

## 📈 性能优化

### 数据处理优化
- 大数据量使用ClickHouse存储
- 采用数据采样减少前端渲染压力
- 异步处理文件上传和数据计算

### 前端性能
- 路由懒加载
- 图表数据虚拟化
- 组件按需导入

## 🚢 部署

### Docker部署 (推荐)
```bash
# TODO: 添加Docker配置文件
docker-compose up -d
```

### 传统部署
```bash
# 后端部署
cd baoluofenxi
gunicorn -w 4 -b 0.0.0.0:5005 app:app

# 前端构建
cd baoluofenxi-frontend
npm run build
# 将dist目录部署到Web服务器
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请联系：
- 邮箱：[your-email@example.com]
- 项目地址：[GitHub Repository URL]

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)
- [ClickHouse](https://clickhouse.com/)

---

<div align="center">
  <p>⭐ 如果这个项目对您有帮助，请给我们一个 Star!</p>
  <p>Made with ❤️ by 包络分析系统团队</p>
</div>
