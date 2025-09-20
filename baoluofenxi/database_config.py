import configparser
import os
from typing import Dict, Any

class DatabaseConfigManager:
    """数据库配置管理器"""
    
    def __init__(self, config_file: str = "database_config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 如果配置文件不存在，创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        self.config.add_section('mysql')
        self.config.set('mysql', 'host', 'localhost')
        self.config.set('mysql', 'port', '3306')
        self.config.set('mysql', 'user', 'root')
        self.config.set('mysql', 'password', '')
        self.config.set('mysql', 'database', 'baoluo')
        self.config.set('mysql', 'charset', 'utf8mb4')
        
        self.config.add_section('clickhouse')
        self.config.set('clickhouse', 'host', 'localhost')
        self.config.set('clickhouse', 'http_port', '8123')
        self.config.set('clickhouse', 'tcp_port', '9000')
        self.config.set('clickhouse', 'user', 'root')
        self.config.set('clickhouse', 'password', '123456')
        self.config.set('clickhouse', 'database', 'baoluo')
        
        self.config.add_section('app')
        self.config.set('app', 'use_clickhouse', 'true')
        self.config.set('app', 'max_file_size', '16777216')
        
        # 保存配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """获取MySQL配置"""
        return {
            'host': self.config.get('mysql', 'host'),
            'port': self.config.getint('mysql', 'port'),
            'user': self.config.get('mysql', 'user'),
            'password': self.config.get('mysql', 'password'),
            'database': self.config.get('mysql', 'database'),
            'charset': self.config.get('mysql', 'charset', fallback='utf8mb4'),
            'pool_size': self.config.getint('mysql', 'pool_size', fallback=10),
            'max_overflow': self.config.getint('mysql', 'max_overflow', fallback=20),
            'pool_recycle': self.config.getint('mysql', 'pool_recycle', fallback=3600)
        }
    
    def get_clickhouse_config(self) -> Dict[str, Any]:
        """获取ClickHouse配置"""
        return {
            'host': self.config.get('clickhouse', 'host'),
            'http_port': self.config.getint('clickhouse', 'http_port'),
            'tcp_port': self.config.getint('clickhouse', 'tcp_port'),
            'user': self.config.get('clickhouse', 'user'),
            'password': self.config.get('clickhouse', 'password'),
            'database': self.config.get('clickhouse', 'database'),
            'send_receive_timeout': self.config.getint('clickhouse', 'send_receive_timeout', fallback=60),
            'sync_request_timeout': self.config.getint('clickhouse', 'sync_request_timeout', fallback=60),
            'compress_block_size': self.config.getint('clickhouse', 'compress_block_size', fallback=1048576),
            'max_memory_usage': self.config.getint('clickhouse', 'max_memory_usage', fallback=1073741824)
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return {
            'use_clickhouse': self.config.getboolean('app', 'use_clickhouse', fallback=True),
            'max_file_size': self.config.getint('app', 'max_file_size', fallback=16777216),
            'allowed_extensions': self.config.get('app', 'allowed_extensions', fallback='csv,xlsx,xls').split(','),
            'default_time_column': self.config.get('app', 'default_time_column', fallback='t'),
            'max_data_points': self.config.getint('app', 'max_data_points', fallback=10000),
            'envelope_cache_timeout': self.config.getint('app', 'envelope_cache_timeout', fallback=3600),
            'batch_size': self.config.getint('app', 'batch_size', fallback=10000)
        }
    
    def get_mysql_uri(self) -> str:
        """获取MySQL连接URI"""
        mysql_config = self.get_mysql_config()
        return f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset={mysql_config['charset']}"
    
    def get_clickhouse_connection_params(self) -> Dict[str, Any]:
        """获取ClickHouse连接参数"""
        ch_config = self.get_clickhouse_config()
        return {
            'host': ch_config['host'],
            'port': ch_config['http_port'],
            'user': ch_config['user'],
            'password': ch_config['password'],
            'database': ch_config['database'],
            'send_receive_timeout': ch_config['send_receive_timeout'],
            'sync_request_timeout': ch_config['sync_request_timeout'],
            'compress_block_size': ch_config['compress_block_size']
        }
    
    def is_clickhouse_enabled(self) -> bool:
        """检查是否启用ClickHouse"""
        return self.get_app_config()['use_clickhouse']
    
    def update_config(self, section: str, key: str, value: str):
        """更新配置项"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        
        # 保存配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def test_connections(self) -> Dict[str, bool]:
        """测试数据库连接"""
        results = {}
        
        # 测试MySQL连接
        try:
            import pymysql
            mysql_config = self.get_mysql_config()
            conn = pymysql.connect(
                host=mysql_config['host'],
                port=mysql_config['port'],
                user=mysql_config['user'],
                password=mysql_config['password'],
                database=mysql_config['database'],
                charset=mysql_config['charset']
            )
            conn.close()
            results['mysql'] = True
        except Exception as e:
            print(f"MySQL连接测试失败: {e}")
            results['mysql'] = False
        
        # 测试ClickHouse连接
        if self.is_clickhouse_enabled():
            try:
                import requests
                ch_config = self.get_clickhouse_config()
                response = requests.get(
                    f"http://{ch_config['host']}:{ch_config['http_port']}/ping",
                    auth=(ch_config['user'], ch_config['password']),
                    timeout=5
                )
                results['clickhouse'] = response.text.strip() == "Ok."
            except Exception as e:
                print(f"ClickHouse连接测试失败: {e}")
                results['clickhouse'] = False
        else:
            results['clickhouse'] = None  # 未启用
            
        return results

# 全局配置管理器实例
db_config = DatabaseConfigManager()

if __name__ == "__main__":
    # 测试配置管理器
    print("数据库配置管理器测试")
    print("=" * 40)
    
    print("MySQL配置:")
    mysql_config = db_config.get_mysql_config()
    for key, value in mysql_config.items():
        if key == 'password' and value:
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    print("\nClickHouse配置:")
    ch_config = db_config.get_clickhouse_config()
    for key, value in ch_config.items():
        if key == 'password' and value:
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    print("\n应用配置:")
    app_config = db_config.get_app_config()
    for key, value in app_config.items():
        print(f"  {key}: {value}")
    
    print(f"\nMySQL URI: {db_config.get_mysql_uri()}")
    print(f"是否启用ClickHouse: {db_config.is_clickhouse_enabled()}")
    
    print("\n测试数据库连接:")
    connections = db_config.test_connections()
    for db, status in connections.items():
        if status is None:
            print(f"  {db}: 未启用")
        elif status:
            print(f"  {db}: ✅ 连接成功")
        else:
            print(f"  {db}: ❌ 连接失败")
