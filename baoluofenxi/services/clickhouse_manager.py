import clickhouse_connect
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from database_config import db_config

class ClickHouseManager:
    """ClickHouse数据库管理器"""
    
    def __init__(self):
        self.config = db_config.get_clickhouse_config()
        self.client = None
        self.connect()
    
    def connect(self):
        """连接ClickHouse数据库"""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.config['host'],
                port=self.config['http_port'],
                username=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            logging.info("ClickHouse连接成功")
        except Exception as e:
            logging.error(f"ClickHouse连接失败: {e}")
            raise
    
    def ensure_database_exists(self):
        """确保数据库存在"""
        try:
            # 先连接到默认数据库
            temp_client = clickhouse_connect.get_client(
                host=self.config['host'],
                port=self.config['http_port'],
                username=self.config['user'],
                password=self.config['password']
            )
            
            # 创建数据库（如果不存在）
            temp_client.command(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            temp_client.close()
            
            logging.info(f"数据库 {self.config['database']} 创建成功或已存在")
        except Exception as e:
            logging.error(f"创建数据库失败: {e}")
            raise
    
    def sanitize_table_name(self, table_name: str) -> str:
        """清理表名，确保符合ClickHouse命名规范"""
        # 替换非字母数字和下划线的字符为下划线
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        
        # 确保以字母或下划线开头
        if not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = 'exp_' + sanitized
        
        # 限制长度
        if len(sanitized) > 60:
            sanitized = sanitized[:60]
        
        return sanitized
    
    def create_timeseries_table(self, table_name: str, time_column: str, data_columns: List[str]) -> bool:
        """
        创建时序数据表
        
        Args:
            table_name: 表名
            time_column: 时间列名
            data_columns: 数据列名列表
            
        Returns:
            bool: 创建成功返回True
        """
        try:
            # 清理表名
            safe_table_name = self.sanitize_table_name(table_name)
            
            # 构建列定义
            columns = [
                f"`{time_column}` Float64",  # 时间列，通常是浮点数
                "timestamp DateTime DEFAULT now()",  # 插入时间戳
            ]
            
            # 添加数据列
            for col in data_columns:
                columns.append(f"`{col}` Float64")
            
            # 创建表的SQL
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS `{safe_table_name}` (
                {', '.join(columns)}
            ) ENGINE = MergeTree()
            ORDER BY ({time_column})
            PARTITION BY toYYYYMM(timestamp)
            SETTINGS index_granularity = 8192
            """
            
            self.client.command(create_sql)
            logging.info(f"表 {safe_table_name} 创建成功")
            return True
            
        except Exception as e:
            logging.error(f"创建表 {table_name} 失败: {e}")
            return False
    
    def insert_dataframe(self, table_name: str, df: pd.DataFrame, time_column: str) -> Dict[str, Any]:
        """
        将DataFrame数据插入到ClickHouse表中
        
        Args:
            table_name: 表名
            df: 要插入的数据
            time_column: 时间列名
            
        Returns:
            Dict: 插入结果
        """
        try:
            # 清理表名
            safe_table_name = self.sanitize_table_name(table_name)
            
            # 准备数据
            df_copy = df.copy()
            
            # 添加插入时间戳
            df_copy['timestamp'] = datetime.now()
            
            # 确保时间列在最前面
            cols = [time_column] + ['timestamp'] + [col for col in df_copy.columns if col not in [time_column, 'timestamp']]
            df_copy = df_copy[cols]
            
            # 将数据转换为适合ClickHouse的格式
            df_copy = df_copy.fillna(0)  # 填充NaN值为0
            
            # 插入数据
            self.client.insert_df(safe_table_name, df_copy)
            
            row_count = len(df_copy)
            logging.info(f"成功插入 {row_count} 行数据到表 {safe_table_name}")
            
            return {
                'success': True,
                'message': f'成功插入 {row_count} 行数据',
                'row_count': row_count,
                'table_name': safe_table_name
            }
            
        except Exception as e:
            logging.error(f"插入数据到表 {table_name} 失败: {e}")
            return {
                'success': False,
                'message': f'插入数据失败: {str(e)}',
                'row_count': 0,
                'table_name': table_name
            }
    
    def query_data(self, table_name: str, time_column: str, 
                   columns: Optional[List[str]] = None,
                   time_range: Optional[tuple] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """
        查询表数据
        
        Args:
            table_name: 表名
            time_column: 时间列名
            columns: 要查询的列，None表示查询所有列
            time_range: 时间范围 (start, end)
            limit: 限制返回行数
            
        Returns:
            pd.DataFrame: 查询结果
        """
        try:
            safe_table_name = self.sanitize_table_name(table_name)
            
            # 构建查询SQL
            if columns:
                columns_str = ', '.join([f"`{col}`" for col in columns])
            else:
                columns_str = '*'
            
            sql = f"SELECT {columns_str} FROM `{safe_table_name}`"
            
            # 添加时间范围过滤
            conditions = []
            if time_range:
                conditions.append(f"`{time_column}` >= {time_range[0]}")
                conditions.append(f"`{time_column}` <= {time_range[1]}")
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            # 排序
            sql += f" ORDER BY `{time_column}`"
            
            # 限制行数
            if limit:
                sql += f" LIMIT {limit}"
            
            # 执行查询
            df = self.client.query_df(sql)
            logging.info(f"成功查询表 {safe_table_name}，返回 {len(df)} 行数据")
            
            return df
            
        except Exception as e:
            logging.error(f"查询表 {table_name} 失败: {e}")
            return pd.DataFrame()
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            safe_table_name = self.sanitize_table_name(table_name)
            result = self.client.query(
                "SELECT count() FROM system.tables WHERE database = %(database)s AND name = %(table)s",
                {"database": self.config['database'], "table": safe_table_name}
            )
            return result.first_row[0] > 0
        except Exception as e:
            logging.error(f"检查表 {table_name} 是否存在失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息和前10行数据"""
        try:
            safe_table_name = self.sanitize_table_name(table_name)
            
            # 获取表结构 - 修复查询语法
            structure_result = self.client.query(f"DESCRIBE TABLE `{safe_table_name}`")
            
            columns = []
            for row in structure_result.result_rows:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'default_type': row[2],
                    'default_expression': row[3]
                })
            
            # 获取行数
            count_result = self.client.query(f"SELECT count() FROM `{safe_table_name}`")
            row_count = count_result.first_row[0]
            
            # 获取前10行数据
            sample_data = []
            if row_count > 0:
                try:
                    sample_result = self.client.query(f"SELECT * FROM `{safe_table_name}` LIMIT 10")
                    column_names = [col['name'] for col in columns]
                    
                    for row in sample_result.result_rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            if i < len(column_names):
                                row_dict[column_names[i]] = value
                        sample_data.append(row_dict)
                        
                except Exception as e:
                    logging.warning(f"获取表 {table_name} 样本数据失败: {e}")
                    sample_data = []
            
            return {
                'table_name': safe_table_name,
                'columns': columns,
                'row_count': row_count,
                'sample_data': sample_data,
                'exists': True
            }
            
        except Exception as e:
            logging.error(f"获取表 {table_name} 信息失败: {e}")
            return {
                'table_name': table_name,
                'exists': False,
                'error': str(e)
            }
    
    def drop_table(self, table_name: str) -> bool:
        """删除表"""
        try:
            safe_table_name = self.sanitize_table_name(table_name)
            self.client.command(f"DROP TABLE IF EXISTS `{safe_table_name}`")
            logging.info(f"表 {safe_table_name} 删除成功")
            return True
        except Exception as e:
            logging.error(f"删除表 {table_name} 失败: {e}")
            return False
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        执行SQL查询并返回结果
        
        Args:
            query: SQL查询语句
            
        Returns:
            Dict: 包含success, data, message字段的结果
        """
        try:
            # 执行查询
            logging.info(f"执行ClickHouse查询: {query}")
            result = self.client.query(query)
            
            # 调试：打印原始列信息
            logging.info(f"查询结果列信息: {result.column_names}")
            
            # 将结果转换为字典列表
            if result.result_rows:
                # 获取列名 - 直接使用 column_names，不需要额外处理
                columns = result.column_names
                logging.info(f"处理后的列名: {columns}")
                # 转换数据
                data = []
                for row in result.result_rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    data.append(row_dict)
            else:
                data = []
            
            return {
                'success': True,
                'data': data,
                'message': f'查询成功，返回{len(data)}条记录'
            }
            
        except Exception as e:
            logging.error(f"执行查询失败: {e}")
            return {
                'success': False,
                'data': [],
                'message': f'查询失败: {str(e)}'
            }
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logging.info("ClickHouse连接已关闭")

# 全局ClickHouse管理器实例
clickhouse_manager = None

def get_clickhouse_manager():
    """获取ClickHouse管理器单例"""
    global clickhouse_manager
    if clickhouse_manager is None:
        clickhouse_manager = ClickHouseManager()
        clickhouse_manager.ensure_database_exists()
    return clickhouse_manager
