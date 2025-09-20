from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql
import logging

# 初始化SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """初始化数据库连接"""
    db.init_app(app)
    
    # 创建数据库（如果不存在）
    create_database_if_not_exists(app.config)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 初始化基础数据
        init_base_data()

def create_database_if_not_exists(config):
    """创建数据库（如果不存在）"""
    try:
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=config['MYSQL_HOST'],
            port=config['MYSQL_PORT'],
            user=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['MYSQL_DATABASE']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
            
        connection.close()
        logging.info(f"数据库 {config['MYSQL_DATABASE']} 创建成功或已存在")
        
    except Exception as e:
        logging.error(f"创建数据库时出错: {e}")
        raise

def init_base_data():
    """初始化基础数据"""
    from models.models import ExperimentType
    
    # 检查是否已有数据
    if ExperimentType.query.count() == 0:
        # 创建默认试验类型
        default_type = ExperimentType(
            name='默认试验类型',
            description='系统默认创建的试验类型，可用于快速开始',
            time_column='t',
            data_columns=['C1', 'C2', 'C3']
        )
        
        db.session.add(default_type)
        db.session.commit()
        logging.info("初始化基础数据完成")

def execute_raw_sql(sql, params=None):
    """执行原生SQL查询"""
    try:
        result = db.session.execute(text(sql), params or {})
        return result
    except Exception as e:
        logging.error(f"执行SQL时出错: {e}")
        db.session.rollback()
        raise

def get_experiment_data_table_name(experiment_type_id):
    """获取试验数据表名"""
    return f'experiment_data_{experiment_type_id}'

def create_experiment_data_table(experiment_type_id, columns):
    """为试验类型创建对应的数据表"""
    table_name = get_experiment_data_table_name(experiment_type_id)
    
    # 构建创建表的SQL
    columns_sql = ['data_id INT NOT NULL', 't DOUBLE NOT NULL']
    columns_sql.extend([f'{col} DOUBLE' for col in columns])
    columns_sql.append('PRIMARY KEY (data_id, t)')
    columns_sql.append('INDEX idx_data_id (data_id)')
    columns_sql.append('INDEX idx_time (t)')
    
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns_sql)}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    try:
        execute_raw_sql(sql)
        db.session.commit()
        logging.info(f"数据表 {table_name} 创建成功")
    except Exception as e:
        logging.error(f"创建数据表 {table_name} 失败: {e}")
        raise