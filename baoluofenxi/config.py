import os
from database_config import db_config

class Config:
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # 从配置文件获取数据库配置
    _mysql_config = db_config.get_mysql_config()
    _clickhouse_config = db_config.get_clickhouse_config()
    _app_config = db_config.get_app_config()
    
    # MySQL数据库配置（存储元数据）
    MYSQL_HOST = _mysql_config['host']
    MYSQL_PORT = _mysql_config['port']
    MYSQL_USER = _mysql_config['user']
    MYSQL_PASSWORD = _mysql_config['password']
    MYSQL_DATABASE = _mysql_config['database']
    
    # MySQL连接字符串
    SQLALCHEMY_DATABASE_URI = db_config.get_mysql_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': _mysql_config['pool_recycle'],
        'pool_size': _mysql_config['pool_size'],
        'max_overflow': _mysql_config['max_overflow'],
    }
    
    # ClickHouse数据库配置（存储时序数据）
    CLICKHOUSE_HOST = _clickhouse_config['host']
    CLICKHOUSE_HTTP_PORT = _clickhouse_config['http_port']
    CLICKHOUSE_TCP_PORT = _clickhouse_config['tcp_port']
    CLICKHOUSE_USER = _clickhouse_config['user']
    CLICKHOUSE_PASSWORD = _clickhouse_config['password']
    CLICKHOUSE_DATABASE = _clickhouse_config['database']
    
    # ClickHouse连接配置
    CLICKHOUSE_SETTINGS = db_config.get_clickhouse_connection_params()
    
    # 数据库选择策略
    USE_CLICKHOUSE = _app_config['use_clickhouse']
    USE_MYSQL_ONLY = not USE_CLICKHOUSE
    
    # API配置
    API_VERSION = 'v1'
    JSON_AS_ASCII = False  # 支持中文JSON响应
    
    # 文件上传配置（用于API上传）
    MAX_CONTENT_LENGTH = _app_config['max_file_size']
    ALLOWED_EXTENSIONS = set(_app_config['allowed_extensions'])
    
    # 包络分析配置
    DEFAULT_TIME_COLUMN = _app_config['default_time_column']
    MAX_DATA_POINTS = _app_config['max_data_points']
    ENVELOPE_CACHE_TIMEOUT = _app_config['envelope_cache_timeout']
    
    # 数据处理配置
    BATCH_SIZE = _app_config['batch_size']
    MAX_MEMORY_USAGE = 1024 * 1024 * 1024  # 1GB 最大内存使用
    
    # 缓存配置
    CACHE_TYPE = 'simple'  # 可以改为 'redis' 如果需要
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}