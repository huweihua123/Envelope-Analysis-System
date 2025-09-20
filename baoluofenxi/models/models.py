from datetime import datetime
from database import db
import json

class ExperimentType(db.Model):
    """试验类型表"""
    __tablename__ = 'experiment_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    time_column = db.Column(db.String(50), nullable=False, default='t')  # 时间列名称
    data_columns = db.Column(db.JSON, nullable=False)  # 数据列配置 ["C1", "C2", "C3"]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 移除关系定义，因为不使用外键约束
    
    def __repr__(self):
        return f'<ExperimentType {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time_column': self.time_column,
            'data_columns': self.data_columns,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExperimentData(db.Model):
    """试验数据表"""
    __tablename__ = 'experiment_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_type_id = db.Column(db.Integer, nullable=True)  # 移除外键约束
    data_name = db.Column(db.String(255), nullable=True)  # 用户自定义的数据名称
    file_name = db.Column(db.String(255), nullable=True)  # 原始文件名
    clickhouse_table_name = db.Column(db.String(255), nullable=True)  # ClickHouse表名
    row_count = db.Column(db.Integer, default=0)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_historical = db.Column(db.Boolean, default=False)  # 是否加入历史数据集
    status = db.Column(db.String(20), default='active')  # active, deleted
    
    def __repr__(self):
        return f'<ExperimentData {self.data_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_type_id': self.experiment_type_id,
            'data_name': self.data_name,
            'file_name': self.file_name,
            'clickhouse_table_name': self.clickhouse_table_name,
            'row_count': self.row_count,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'is_historical': self.is_historical,
            'status': self.status
        }

class EnvelopeSettings(db.Model):
    """包络配置表（用户选择要分析的列）"""
    __tablename__ = 'envelope_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_type_id = db.Column(db.Integer, nullable=True)  # 移除外键约束
    selected_columns = db.Column(db.JSON, nullable=True)  # 用户选择的要显示包络的列 ["C1", "C3"]
    time_range_start = db.Column(db.Float)
    time_range_end = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnvelopeSettings for ExperimentType {self.experiment_type_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_type_id': self.experiment_type_id,
            'selected_columns': self.selected_columns,
            'time_range_start': self.time_range_start,
            'time_range_end': self.time_range_end,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EnvelopeCache(db.Model):
    """包络缓存表（用于缓存计算结果）"""
    __tablename__ = 'envelope_cache'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_type_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    selected_columns_hash = db.Column(db.String(64), nullable=False)  # 选中列的hash值
    historical_data_ids = db.Column(db.JSON, nullable=False)  # 历史数据ID列表
    envelope_data = db.Column(db.JSON, nullable=False)  # 包络数据（上下边界）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<EnvelopeCache for ExperimentType {self.experiment_type_id}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_type_id': self.experiment_type_id,
            'envelope_data': self.envelope_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }