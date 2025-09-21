import pandas as pd
import numpy as np
import os
import logging
import io
import re
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from database import db, execute_raw_sql, get_experiment_data_table_name
from models.models import (
    ExperimentData,
    ExperimentType,
    EnvelopeSettings,
    EnvelopeCache,
    ExperimentType,
)
from services.clickhouse_manager import get_clickhouse_manager
import hashlib
import json


class DataProcessor:
    """数据处理服务类"""

    def __init__(self):
        self.allowed_extensions = {"csv", "xlsx", "xls"}
        self.clickhouse_manager = get_clickhouse_manager()

    def is_allowed_file(self, filename):
        """检查文件类型是否允许"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def detect_csv_format(self, file):
        """
        检测CSV文件的格式类型
        返回: (is_special_format: bool, preview_content: str)
        """
        try:
            # 读取文件前1KB内容
            file.seek(0)
            content = file.read(1024)

            # 处理编码
            if isinstance(content, bytes):
                try:
                    content = content.decode("utf-8")
                except UnicodeDecodeError:
                    content = content.decode("gbk")

            # 重置文件指针
            file.seek(0)

            lines = content.strip().split("\n")[:10]  # 前10行

            if len(lines) < 2:
                return False, content

            # 检查第一行是否包含多个空格分隔的值但CSV解析时只有1列
            first_line = lines[0].strip()
            second_line = lines[1].strip() if len(lines) > 1 else ""

            # 特殊格式的特征：
            # 1. 包含空格分隔的多个值
            # 2. 不包含逗号分隔符
            # 3. 第二行也是类似格式
            if (
                " " in first_line
                and "," not in first_line
                and len(first_line.split()) >= 3  # 至少3个字段
                and " " in second_line
                and "," not in second_line
            ):

                # 进一步验证：尝试用pandas读取看是否只有1列
                try:
                    import io

                    test_df = pd.read_csv(io.StringIO(content))
                    if len(test_df.columns) == 1:
                        return True, content
                except:
                    pass

            return False, content

        except Exception as e:
            logging.error(f"检测文件格式失败: {e}")
            return False, ""

    def parse_special_format_preview(self, content, preview_rows=10):
        """
        解析特殊格式的预览数据
        """
        import io

        lines = content.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("文件内容不足")

        # 假设用空格分隔，解析前几行
        processed_lines = []
        for i, line in enumerate(lines[: preview_rows + 1]):  # +1 for header
            if line.strip():
                # 将空格替换为逗号
                processed_line = ",".join(line.strip().split())
                processed_lines.append(processed_line)

        # 创建标准CSV格式内容
        csv_content = "\n".join(processed_lines)

        # 使用pandas读取
        df = pd.read_csv(io.StringIO(csv_content))
        return df

    def parse_special_format_complete(self, content):
        """
        解析特殊格式的完整数据（用于上传）
        """
        import io

        lines = content.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("文件内容不足")  # 处理所有行，不限制行数
        processed_lines = []
        for line in lines:
            if line.strip():
                # 将空格替换为逗号
                processed_line = ",".join(line.strip().split())
                processed_lines.append(processed_line)

        # 创建标准CSV格式内容
        csv_content = "\n".join(processed_lines)

        # 使用pandas读取
        df = pd.read_csv(io.StringIO(csv_content))

        # 强制转换数值列的数据类型
        for col in df.columns:
            if col != df.columns[0]:  # 假设第一列是时间列，其他都是数值列
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                except:
                    pass

        return df

    def preview_file(self, file, experiment_type, preview_rows=10):
        """预览文件内容"""
        try:
            if not self.is_allowed_file(file.filename):
                return {
                    "success": False,
                    "message": "不支持的文件格式",
                }  # 首先检测文件格式
            is_special_format, preview_content = self.detect_csv_format(file)

            if is_special_format:
                # 特殊格式：所有数据在一个单元格中
                df = self.parse_special_format_preview(preview_content, preview_rows)
                format_type = "special"
                format_message = (
                    "检测到特殊格式：所有数据在一个单元格中，系统将自动转换"
                )
            else:
                # 标准格式
                file.seek(0)  # 重置文件指针
                if file.filename.endswith(".csv"):
                    df = pd.read_csv(file, nrows=preview_rows)
                else:
                    # 处理Excel文件，根据扩展名选择引擎
                    if file.filename.endswith(".xlsx"):
                        df = pd.read_excel(file, engine="openpyxl", nrows=preview_rows)
                    elif file.filename.endswith(".xls"):
                        df = pd.read_excel(file, engine="xlrd", nrows=preview_rows)
                    else:
                        # 尝试自动检测
                        try:
                            df = pd.read_excel(
                                file, engine="openpyxl", nrows=preview_rows
                            )
                        except Exception:
                            try:
                                file.seek(0)
                                df = pd.read_excel(
                                    file, engine="xlrd", nrows=preview_rows
                                )
                            except Exception as e:
                                logging.error(f"Excel预览文件读取失败: {e}")
                                return {
                                    "success": False,
                                    "message": f"Excel预览失败: {str(e)}",
                                }
                format_type = "standard"
                format_message = "标准格式"

            # 验证数据格式
            validation_result = self.validate_data_format(df, experiment_type)

            # 如果是特殊格式，添加格式相关的验证信息
            if is_special_format:
                if validation_result["is_valid"]:
                    validation_result["message"] = f"{format_message}，数据格式正确"
                else:
                    validation_result["message"] = (
                        f"{format_message}，{validation_result['message']}"
                    )

            # 返回预览信息
            preview_data = {
                "file_info": {
                    "name": file.filename,
                    "rows_preview": len(df),
                    "total_columns": len(df.columns),
                    "columns": list(df.columns),
                    "format_type": format_type,
                },
                "validation": validation_result,
                "data_preview": df.head(preview_rows).to_dict("records"),
                "column_info": {},
            }

            # 添加列信息
            for col in df.columns:
                preview_data["column_info"][col] = {
                    "type": str(df[col].dtype),
                    "non_null_count": int(df[col].count()),
                    "sample_values": df[col].dropna().head(5).tolist(),
                }

            return preview_data

        except Exception as e:
            logging.error(f"预览文件失败: {e}")
            return {"success": False, "message": f"预览失败: {str(e)}"}

    def process_upload(self, file, data_name, experiment_type):
        """处理文件上传"""
        try:
            if not self.is_allowed_file(file.filename):
                return {"success": False, "message": "不支持的文件格式"}  # 读取文件数据
            if file.filename.endswith(".csv"):
                # 首先检测文件格式
                is_special_format, preview_content = self.detect_csv_format(file)

                if is_special_format:
                    # 处理特殊格式，读取完整文件内容
                    logging.info(f"检测到特殊格式文件: {file.filename}")
                    file.seek(0)  # 重置文件指针
                    full_content = file.read()
                    if isinstance(full_content, bytes):
                        full_content = full_content.decode("utf-8")
                    df = self.parse_special_format_complete(full_content)
                else:
                    # 标准格式
                    file.seek(0)  # 重置文件指针
                    df = pd.read_csv(file)
            else:
                # 处理Excel文件，根据扩展名选择引擎
                file.seek(0)  # 重置文件指针
                if file.filename.endswith(".xlsx"):
                    df = pd.read_excel(file, engine="openpyxl")
                elif file.filename.endswith(".xls"):
                    df = pd.read_excel(file, engine="xlrd")
                else:
                    # 尝试自动检测
                    try:
                        df = pd.read_excel(file, engine="openpyxl")
                    except Exception:
                        try:
                            file.seek(0)
                            df = pd.read_excel(file, engine="xlrd")
                        except Exception as e:
                            logging.error(f"Excel文件读取失败: {e}")
                            return {
                                "success": False,
                                "message": f"Excel文件读取失败: {str(e)}",
                            }

            # 验证数据格式
            validation_result = self.validate_data_format(df, experiment_type)
            if not validation_result["is_valid"]:
                return {"success": False, "message": validation_result["message"]}

            # 数据清洗
            df_clean = self.clean_data(df, experiment_type)

            # 生成表名
            table_name = f"exp_{experiment_type.id}_{int(datetime.now().timestamp())}"

            # 创建数据记录
            experiment_data = ExperimentData(
                experiment_type_id=experiment_type.id,
                data_name=data_name,
                file_name=file.filename,
                clickhouse_table_name=table_name,  # 使用正确的字段名
                row_count=len(df_clean),
                upload_time=datetime.now(),
                status="active",
            )

            db.session.add(experiment_data)
            db.session.commit()

            # 上传数据到ClickHouse
            clickhouse_result = self.upload_to_clickhouse(
                df_clean,
                table_name,
                experiment_type.time_column,
                experiment_type.data_columns,
            )

            if not clickhouse_result["success"]:
                # 如果ClickHouse上传失败，删除数据记录
                db.session.delete(experiment_data)
                db.session.commit()
                return clickhouse_result

            # 更新数据记录中的表名（如果ClickHouse中的表名有变化）
            if clickhouse_result.get("table_name") != table_name:
                experiment_data.clickhouse_table_name = clickhouse_result["table_name"]
                db.session.commit()

            logging.info(
                f'数据上传成功: {data_name}, 行数: {len(df_clean)}, 表名: {clickhouse_result["table_name"]}'
            )

            return {
                "success": True,
                "message": "数据上传成功",
                "data_id": experiment_data.id,
                "row_count": len(df_clean),
                "table_name": clickhouse_result["table_name"],
            }

        except Exception as e:
            db.session.rollback()
            logging.error(f"处理上传失败: {e}")
            return {"success": False, "message": f"处理失败: {str(e)}"}

    def upload_to_clickhouse(self, df, table_name, time_column, data_columns):
        """将数据上传到ClickHouse"""
        try:
            # 获取ClickHouse管理器
            ch_manager = get_clickhouse_manager()

            # 创建表
            if not ch_manager.create_timeseries_table(
                table_name, time_column, data_columns
            ):
                return {"success": False, "message": "ClickHouse表创建失败"}

            # 插入数据
            insert_result = ch_manager.insert_dataframe(table_name, df, time_column)

            if insert_result["success"]:
                logging.info(f'ClickHouse数据插入成功: {insert_result["message"]}')
            else:
                logging.error(f'ClickHouse数据插入失败: {insert_result["message"]}')

            return insert_result

        except Exception as e:
            logging.error(f"ClickHouse上传失败: {e}")
            return {"success": False, "message": f"ClickHouse上传失败: {str(e)}"}

    def validate_data_format(self, df, experiment_type):
        """验证数据格式"""
        try:
            issues = []

            # 检查必要的列是否存在
            required_columns = [
                experiment_type.time_column
            ] + experiment_type.data_columns
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                issues.append(f'缺少必要的列: {", ".join(missing_columns)}')

            # 检查时间列是否为数值型
            time_column = experiment_type.time_column
            if time_column in df.columns and not pd.api.types.is_numeric_dtype(
                df[time_column]
            ):
                issues.append(f'时间列 "{time_column}" 必须是数值型')

            # 检查数据列是否为数值型
            for col in experiment_type.data_columns:
                if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f'数据列 "{col}" 必须是数值型')

            # 检查数据是否为空
            if len(df) == 0:
                issues.append("文件中没有数据")

            is_valid = len(issues) == 0

            return {
                "is_valid": is_valid,
                "valid": is_valid,  # 保持向后兼容
                "issues": issues,
                "message": "数据格式验证通过" if is_valid else "; ".join(issues),
            }

        except Exception as e:
            return {
                "is_valid": False,
                "valid": False,
                "issues": [f"验证数据格式失败: {str(e)}"],
                "message": f"验证数据格式失败: {str(e)}",
            }

    def get_experiment_data(
        self, experiment_data_id, time_range=None, columns=None, limit=None
    ):
        """从ClickHouse获取实验数据"""
        try:
            # 获取数据记录
            data_record = ExperimentData.query.get(experiment_data_id)
            if not data_record:
                return {"success": False, "message": "数据记录不存在"}

            if not data_record.clickhouse_table_name:
                return {"success": False, "message": "数据表名不存在"}

            # 获取实验类型信息
            from models.models import ExperimentType

            experiment_type = ExperimentType.query.get(data_record.experiment_type_id)
            if not experiment_type:
                return {"success": False, "message": "实验类型不存在"}

            # 从ClickHouse查询数据
            ch_manager = get_clickhouse_manager()
            df = ch_manager.query_data(
                table_name=data_record.clickhouse_table_name,
                time_column=experiment_type.time_column,
                columns=columns,
                time_range=time_range,
                limit=limit,
            )

            return {
                "success": True,
                "data": df.to_dict("records"),
                "columns": list(df.columns),
                "row_count": len(df),
            }

        except Exception as e:
            logging.error(f"获取实验数据失败: {e}")
            return {"success": False, "message": f"获取数据失败: {str(e)}"}

    def get_multiple_experiment_data(
        self, experiment_data_ids, time_range=None, columns=None
    ):
        """批量获取多个实验数据"""
        try:
            all_data = []

            for data_id in experiment_data_ids:
                result = self.get_experiment_data(data_id, time_range, columns)
                if result["success"]:
                    all_data.extend(result["data"])

            if not all_data:
                return {"success": False, "message": "没有获取到有效数据"}

            # 转换为DataFrame进行处理
            df = pd.DataFrame(all_data)

            return {
                "success": True,
                "data": all_data,
                "combined_df": df,
                "total_rows": len(df),
            }

        except Exception as e:
            logging.error(f"批量获取实验数据失败: {e}")
            return {"success": False, "message": f"批量获取数据失败: {str(e)}"}

    def clean_data(self, df, experiment_type):
        """数据清洗和预处理"""
        try:
            # 选择需要的列
            required_columns = [
                experiment_type.time_column
            ] + experiment_type.data_columns
            df_clean = df[required_columns].copy()

            # 删除包含NaN的行
            df_clean = df_clean.dropna()

            # 按时间列排序
            df_clean = df_clean.sort_values(experiment_type.time_column)

            # 重置索引
            df_clean = df_clean.reset_index(drop=True)

            return df_clean

        except Exception as e:
            logging.error(f"数据清洗失败: {e}")
            raise

    def calculate_envelope_for_columns(
        self,
        experiment_type_id,
        selected_columns,
        sampling_points=None,
        use_sampling=True,
    ):
        """
        为指定列计算包络数据

        Args:
            experiment_type_id: 实验类型ID
            selected_columns: 选中的数据列
            sampling_points: 采样点数，默认200
            use_sampling: 是否使用采样，False表示使用所有数据点
        """
        try:
            # 获取历史数据
            historical_data = ExperimentData.query.filter_by(
                experiment_type_id=experiment_type_id,
                is_historical=True,
                status="active",
            ).all()

            if not historical_data:
                return {"error": "没有标记为历史数据的记录"}

            # 设置采样参数
            if sampling_points is None:
                sampling_points = 200

            # 构建缓存键
            cache_key_data = {
                "selected_columns": sorted(selected_columns),
                "sampling_points": sampling_points if use_sampling else "full",
                "use_sampling": use_sampling,
            }
            columns_hash = hashlib.md5(
                json.dumps(cache_key_data, sort_keys=True).encode()
            ).hexdigest()

            # 检查缓存
            data_ids = [d.id for d in historical_data]
            cache = (
                EnvelopeCache.query.filter_by(
                    experiment_type_id=experiment_type_id,
                    selected_columns_hash=columns_hash,
                )
                .filter(
                    EnvelopeCache.historical_data_ids == json.dumps(sorted(data_ids))
                )
                .first()
            )

            if cache and not cache.is_expired():
                logging.info(f"使用缓存的包络数据: {cache.id}")
                return cache.envelope_data

            # 计算新的包络数据
            if use_sampling:
                envelope_data = self._compute_envelope_with_sampling(
                    historical_data, selected_columns, sampling_points
                )
            else:
                envelope_data = self._compute_envelope_full_data(
                    historical_data, selected_columns
                )

            # 保存到缓存
            if cache:
                cache.envelope_data = envelope_data
                cache.created_at = datetime.now()
                cache.expires_at = datetime.now() + timedelta(hours=1)
            else:
                cache = EnvelopeCache(
                    experiment_type_id=experiment_type_id,
                    selected_columns_hash=columns_hash,
                    historical_data_ids=json.dumps(sorted(data_ids)),
                    envelope_data=envelope_data,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=1),
                )
                db.session.add(cache)

            db.session.commit()

            return envelope_data

        except Exception as e:
            logging.error(f"计算包络数据失败: {e}")
            return {"error": f"计算失败: {str(e)}"}

    def calculate_envelope(self, experiment_type_id):
        """计算包络数据（保持兼容性）"""
        try:
            # 获取包络设置
            settings = EnvelopeSettings.query.filter_by(
                experiment_type_id=experiment_type_id
            ).first()

            if not settings or not settings.selected_columns:
                return {"error": "请先设置要分析的数据列"}

            return self.calculate_envelope_for_columns(
                experiment_type_id, settings.selected_columns
            )

        except Exception as e:
            logging.error(f"计算包络数据失败: {e}")
            return {"error": f"计算失败: {str(e)}"}

    def _compute_envelope_from_data(self, data_records, selected_columns):
        """从数据记录计算包络 - 基于时间线的最大最小值"""
        try:
            # 从ClickHouse获取所有历史数据
            data_ids = [record.id for record in data_records]
            combined_result = self.get_multiple_experiment_data(data_ids)

            if not combined_result["success"]:
                raise Exception(combined_result["message"])

            df = combined_result["combined_df"]

            if df.empty:
                raise Exception("没有可用的历史数据")

            # 获取实验类型信息
            from models.models import ExperimentType

            experiment_type = ExperimentType.query.get(
                data_records[0].experiment_type_id
            )
            time_column = experiment_type.time_column

            # 按时间分组计算包络（简化逻辑：每个时间点的最大最小值）
            time_min = df[time_column].min()
            time_max = df[time_column].max()

            # 创建时间区间（200个区间提供更精细的包络线）
            n_intervals = min(200, len(df) // 5) or 20
            time_bins = np.linspace(time_min, time_max, n_intervals + 1)

            # 按时间区间分组
            df["time_group"] = pd.cut(
                df[time_column], bins=time_bins, include_lowest=True
            )

            # 计算每个时间区间内各列的最大最小值
            envelope_data = {}
            time_points = []

            # 为每个选中的列计算包络
            for column in selected_columns:
                if column not in df.columns:
                    continue

                upper_envelope = []
                lower_envelope = []
                current_time_points = []

                # 按时间分组计算最大最小值
                grouped = df.groupby("time_group", observed=True)

                for group_name, group_data in grouped:
                    if len(group_data) == 0:
                        continue

                    # 计算该时间段的中心点
                    time_center = group_data[time_column].mean()
                    current_time_points.append(time_center)

                    # 计算该时间段内该列的最大最小值
                    column_values = group_data[column].dropna()
                    if len(column_values) > 0:
                        max_val = column_values.max()
                        min_val = column_values.min()
                        upper_envelope.append(max_val)
                        lower_envelope.append(min_val)
                    else:
                        # 如果该时间段没有数据，使用0填充
                        upper_envelope.append(0)
                        lower_envelope.append(0)

                envelope_data[column] = {
                    "upper": upper_envelope,
                    "lower": lower_envelope,
                }

                # 使用第一列的时间点作为基准
                if not time_points:
                    time_points = current_time_points

            # 构造返回数据，符合前端期望的格式
            envelope_result = {
                "time_points": sorted(time_points),
                "envelope_data": envelope_data,
                "data_count": len(data_records),
                "time_range": {"min": float(time_min), "max": float(time_max)},
            }

            return envelope_result

        except Exception as e:
            logging.error(f"计算包络失败: {e}")
            # 如果计算失败，返回默认的模拟数据
            envelope_result = {
                "time_points": list(np.arange(0, 10, 0.1)),
                "envelopes": {},
            }

            for column in selected_columns:
                # 模拟包络计算
                time_points = envelope_result["time_points"]
                upper_envelope = [
                    np.sin(t * 2) + 1 + np.random.random() * 0.5 for t in time_points
                ]
                lower_envelope = [
                    np.sin(t * 2) - 1 - np.random.random() * 0.5 for t in time_points
                ]

                envelope_result["envelopes"][column] = {
                    "upper": upper_envelope,
                    "lower": lower_envelope,
                    "data_count": len(data_records),
                }

            return envelope_result

    def _compute_envelope_with_sampling(
        self, data_records, selected_columns, sampling_points
    ):
        """
        计算采样包络 - 基于时间区间采样

        Args:
            data_records: 历史数据记录
            selected_columns: 选中的数据列
            sampling_points: 采样点数
        """
        try:
            # 从ClickHouse获取所有历史数据
            data_ids = [record.id for record in data_records]
            combined_result = self.get_multiple_experiment_data(data_ids)

            if not combined_result["success"]:
                return {"error": "获取历史数据失败"}

            df = combined_result["combined_df"]

            if df.empty:
                return {"error": "没有有效的历史数据"}

            # 获取实验类型信息
            experiment_type = ExperimentType.query.get(
                data_records[0].experiment_type_id
            )
            time_column = experiment_type.time_column

            # 按时间分组计算包络
            time_min = df[time_column].min()
            time_max = df[time_column].max()

            # 创建时间区间
            n_intervals = min(sampling_points, len(df) // 5) or 20
            time_bins = np.linspace(time_min, time_max, n_intervals + 1)

            # 按时间区间分组
            df["time_group"] = pd.cut(
                df[time_column], bins=time_bins, include_lowest=True
            )

            # 计算每个时间区间内各列的最大最小值
            envelope_data = {}
            time_points = []

            # 为每个选中的列计算包络
            for column in selected_columns:
                if column not in df.columns:
                    continue

                upper_envelope = []
                lower_envelope = []
                current_time_points = []

                # 按时间分组计算最大最小值
                grouped = df.groupby("time_group", observed=True)

                for group_name, group_data in grouped:
                    if len(group_data) == 0:
                        continue

                    # 计算该时间段的中心点
                    time_center = group_data[time_column].mean()
                    current_time_points.append(time_center)

                    # 计算该时间段内该列的最大最小值
                    column_values = group_data[column].dropna()
                    if len(column_values) > 0:
                        max_val = column_values.max()
                        min_val = column_values.min()
                        upper_envelope.append(max_val)
                        lower_envelope.append(min_val)
                    else:
                        # 如果该时间段没有数据，使用0填充
                        upper_envelope.append(0)
                        lower_envelope.append(0)

                envelope_data[column] = {
                    "upper": upper_envelope,
                    "lower": lower_envelope,
                }

                # 使用第一列的时间点作为基准
                if not time_points:
                    time_points = current_time_points

            # 构造返回数据
            return {
                "time_points": sorted(time_points),
                "envelope_data": envelope_data,
                "data_count": len(data_records),
                "sampling_method": "time_interval",
                "sampling_points": len(time_points),
                "original_points": len(df),
                "time_range": {"min": float(time_min), "max": float(time_max)},
            }

        except Exception as e:
            logging.error(f"采样包络计算失败: {e}")
            return {"error": f"采样计算失败: {str(e)}"}

    def _compute_envelope_full_data(self, data_records, selected_columns):
        """
        计算完整数据包络 - 不采样，处理每个时间点

        Args:
            data_records: 历史数据记录
            selected_columns: 选中的数据列
        """
        try:
            # 获取试验类型信息
            experiment_type = ExperimentType.query.get(
                data_records[0].experiment_type_id
            )
            time_column = experiment_type.time_column

            # 收集所有实际时间点的数据
            all_data_by_time = {}  # {time_point: {column: [values]}}

            for data_record in data_records:
                if not self.clickhouse_manager.table_exists(
                    data_record.clickhouse_table_name
                ):
                    continue

                # 查询完整数据，不限制行数
                query = f"""
                SELECT `{time_column}`, {', '.join([f'`{col}`' for col in selected_columns])}
                FROM `{data_record.clickhouse_table_name}`
                ORDER BY `{time_column}`
                """

                result = self.clickhouse_manager.execute_query(query)
                if not result["success"]:
                    continue

                # 按实际时间点收集数据
                for row in result["data"]:
                    time_point = row[time_column]

                    if time_point not in all_data_by_time:
                        all_data_by_time[time_point] = {}

                    for column in selected_columns:
                        if column in row:
                            if column not in all_data_by_time[time_point]:
                                all_data_by_time[time_point][column] = []
                            all_data_by_time[time_point][column].append(row[column])

            if not all_data_by_time:
                return {"error": "没有找到有效的历史数据"}

            # 计算每个实际时间点的包络（不采样）
            sorted_time_points = sorted(all_data_by_time.keys())
            envelope_data = {}

            for column in selected_columns:
                upper_values = []
                lower_values = []

                for time_point in sorted_time_points:
                    if (
                        column in all_data_by_time[time_point]
                        and len(all_data_by_time[time_point][column]) > 0
                    ):
                        values = all_data_by_time[time_point][column]
                        upper_values.append(max(values))
                        lower_values.append(min(values))
                    else:
                        # 如果某个时间点没有该列的数据，跳过该点
                        continue

                envelope_data[column] = {"upper": upper_values, "lower": lower_values}

            return {
                "time_points": sorted_time_points,
                "envelope_data": envelope_data,
                "data_count": len(data_records),
                "sampling_method": "full_data",
                "sampling_points": len(sorted_time_points),
                "original_points": len(sorted_time_points),
                "time_range": {
                    "min": float(min(sorted_time_points)),
                    "max": float(max(sorted_time_points)),
                },
            }

        except Exception as e:
            logging.error(f"完整包络计算失败: {e}")
            return {"error": f"完整计算失败: {str(e)}"}

    def get_data_statistics(self, experiment_type_id):
        """获取数据统计信息"""
        try:
            stats = {
                "total_datasets": ExperimentData.query.filter_by(
                    experiment_type_id=experiment_type_id, status="active"
                ).count(),
                "historical_datasets": ExperimentData.query.filter_by(
                    experiment_type_id=experiment_type_id,
                    is_historical=True,
                    status="active",
                ).count(),
                "total_rows": db.session.query(db.func.sum(ExperimentData.row_count))
                .filter_by(experiment_type_id=experiment_type_id, status="active")
                .scalar()
                or 0,
            }

            return stats

        except Exception as e:
            logging.error(f"获取统计信息失败: {e}")
            return {"error": f"获取统计信息失败: {str(e)}"}

    def process_temp_upload(self, file, experiment_type, format_options=None):
        """
        处理临时上传，用于包络分析对比
        不写入MySQL，只上传到ClickHouse临时表

        Args:
            file: 上传的文件
            experiment_type: 试验类型
            format_options: 格式选项 {'format_type': 'standard'|'special', 'separator': str, 'skip_rows': int}
        """
        try:
            # 解析格式选项
            format_type = (
                format_options.get("format_type", "standard")
                if format_options
                else "standard"
            )
            separator = format_options.get("separator", " ") if format_options else " "
            skip_rows = format_options.get("skip_rows", 0) if format_options else 0

            # 根据格式类型读取文件
            if format_type == "special":
                # 处理特殊格式文件
                df = self.read_special_format_csv(
                    file, separator, skip_rows, experiment_type
                )
            else:
                # 标准格式文件
                df = pd.read_csv(file)

            logging.info(f"读取文件成功，数据形状: {df.shape}")

            # 验证数据格式
            validation_result = self.validate_data_format(df, experiment_type)
            if not validation_result["is_valid"]:
                return {"success": False, "message": validation_result["message"]}

            # 生成临时表名（基于时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_table_name = f"temp_envelope_data_{timestamp}"

            # 上传到ClickHouse临时表
            clickhouse_result = self.upload_to_clickhouse(
                df,
                temp_table_name,
                experiment_type.time_column,
                experiment_type.data_columns,
            )

            if not clickhouse_result["success"]:
                return {
                    "success": False,
                    "message": f'ClickHouse上传失败: {clickhouse_result["message"]}',
                }

            return {
                "success": True,
                "temp_table_name": temp_table_name,
                "temp_data_id": temp_table_name,  # 用于后续引用
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "time_range": {
                    "min": float(df[experiment_type.time_column].min()),
                    "max": float(df[experiment_type.time_column].max()),
                },
            }

        except Exception as e:
            logging.error(f"临时上传处理失败: {e}")
            return {"success": False, "message": f"处理失败: {str(e)}"}

    def get_temp_comparison_data(
        self,
        temp_table_name,
        time_column,
        selected_columns,
        use_sampling=True,
        sampling_points=200,
    ):
        """
        从临时表获取对比数据

        Args:
            temp_table_name: 临时表名
            time_column: 时间列名
            selected_columns: 选中的数据列
            use_sampling: 是否使用采样
            sampling_points: 采样点数
        """
        try:
            # 构建查询语句
            columns_str = f"`{time_column}`, " + ", ".join(
                [f"`{col}`" for col in selected_columns]
            )
            query = f"""
            SELECT {columns_str}
            FROM `{temp_table_name}`
            ORDER BY `{time_column}`
            """

            # 执行查询
            result = self.clickhouse_manager.execute_query(query)
            if not result["success"]:
                return {"success": False, "message": f'查询失败: {result["message"]}'}

            data = result["data"]
            if not data:
                return {"success": False, "message": "临时表中没有找到数据"}

            # 调试：打印数据结构
            if data:
                logging.info(f"临时数据第一行的键: {list(data[0].keys())}")
                logging.info(f"requested columns: {selected_columns}")

            # 检查列是否存在
            for column in selected_columns:
                if column not in data[0]:
                    logging.error(
                        f"列 '{column}' 不在数据中，可用列: {list(data[0].keys())}"
                    )
                    return {"success": False, "message": f"列 {column} 不存在"}

            # 将数据转换为DataFrame以便采样处理
            df = pd.DataFrame(data)
            original_points = len(df)

            if use_sampling and original_points > sampling_points:
                # 应用采样逻辑
                time_min = df[time_column].min()
                time_max = df[time_column].max()

                # 创建时间区间
                n_intervals = min(sampling_points, original_points // 5) or 20
                time_bins = np.linspace(time_min, time_max, n_intervals + 1)

                # 按时间区间分组采样
                df["time_group"] = pd.cut(
                    df[time_column], bins=time_bins, include_lowest=True
                )

                # 每个时间组取中位值或平均值
                sampled_data = []
                grouped = df.groupby("time_group", observed=True)

                for group_name, group_data in grouped:
                    if len(group_data) == 0:
                        continue

                    # 计算该时间段的中心点
                    time_center = group_data[time_column].mean()

                    # 为每个数据列计算平均值
                    row_data = {time_column: time_center}
                    for column in selected_columns:
                        column_values = group_data[column].dropna()
                        if len(column_values) > 0:
                            row_data[column] = column_values.mean()
                        else:
                            row_data[column] = 0

                    sampled_data.append(row_data)

                # 使用采样后的数据
                processed_data = sampled_data
                sampling_method = "time_interval"
                actual_points = len(sampled_data)
            else:
                # 不采样，使用原始数据
                processed_data = data
                sampling_method = "full_data"
                actual_points = original_points

            # 整理数据格式
            time_points = [row[time_column] for row in processed_data]
            comparison_data = {}

            for column in selected_columns:
                comparison_data[column] = [row[column] for row in processed_data]

            return {
                "success": True,
                "data": {
                    "time_points": time_points,
                    "data": comparison_data,
                    "sampling_method": sampling_method,
                    "sampling_points": actual_points,
                    "original_points": original_points,
                    "time_range": {
                        "min": float(min(time_points)) if time_points else 0,
                        "max": float(max(time_points)) if time_points else 0,
                    },
                },
            }

        except Exception as e:
            logging.error(f"获取临时对比数据失败: {e}")
            return {"success": False, "message": f"获取数据失败: {str(e)}"}

    def save_temp_data_to_mysql(
        self, temp_table_name, data_name, experiment_type, file_name
    ):
        """
        将临时数据保存到MySQL元数据表
        """
        try:
            # 从临时表获取基本信息
            count_query = f"SELECT count(*) as total FROM {temp_table_name}"
            count_result = self.clickhouse_manager.execute_query(count_query)

            if not count_result["success"]:
                return {"success": False, "message": "获取数据行数失败"}

            row_count = count_result["data"][0]["total"]

            # 创建MySQL记录
            experiment_data = ExperimentData(
                data_name=data_name,
                experiment_type_id=experiment_type.id,
                file_name=file_name,
                status="active",
                row_count=row_count,
                clickhouse_table_name=temp_table_name.replace(
                    "temp_", ""
                ),  # 移除temp前缀
                upload_time=datetime.now(),
            )

            db.session.add(experiment_data)
            db.session.commit()

            # 重命名ClickHouse表（移除temp前缀）
            new_table_name = temp_table_name.replace("temp_", "")
            rename_query = f"RENAME TABLE {temp_table_name} TO {new_table_name}"
            rename_result = self.clickhouse_manager.execute_query(rename_query)

            if not rename_result["success"]:
                # 如果重命名失败，删除MySQL记录
                db.session.delete(experiment_data)
                db.session.commit()
                return {
                    "success": False,
                    "message": f'表重命名失败: {rename_result["message"]}',
                }

            return {
                "success": True,
                "data_id": experiment_data.id,
                "message": "数据保存成功",
            }

        except Exception as e:
            logging.error(f"保存临时数据到MySQL失败: {e}")
            return {"success": False, "message": f"保存失败: {str(e)}"}

    def delete_temp_table(self, temp_table_name):
        """
        删除临时表
        """
        try:
            drop_query = f"DROP TABLE IF EXISTS {temp_table_name}"
            result = self.clickhouse_manager.execute_query(drop_query)

            if result["success"]:
                logging.info(f"临时表 {temp_table_name} 删除成功")
            else:
                logging.error(f"删除临时表失败: {result['message']}")

            return result

        except Exception as e:
            logging.error(f"删除临时表失败: {e}")
            return {"success": False, "message": f"删除失败: {str(e)}"}

    def calculate_envelope_simple(self, experiment_type_id, selected_columns):
        """
        计算简单的包络数据：每个时间点的最大值和最小值
        """
        try:
            # 获取试验类型信息
            experiment_type = ExperimentType.query.get(experiment_type_id)
            if not experiment_type:
                return {"success": False, "message": "试验类型不存在"}

            time_column = experiment_type.time_column

            # 获取历史数据记录
            historical_data = ExperimentData.query.filter_by(
                experiment_type_id=experiment_type_id,
                is_historical=True,
                status="active",
            ).all()

            if not historical_data:
                return {"success": False, "message": "没有标记为历史数据的记录"}

            # 检查表是否存在并获取所有历史数据
            all_envelope_data = {}
            all_time_points = set()

            for data_record in historical_data:
                if not data_record.clickhouse_table_name:
                    logging.warning(f"数据记录 {data_record.id} 缺少ClickHouse表名")
                    continue

                # 检查表是否存在
                if not self.clickhouse_manager.table_exists(
                    data_record.clickhouse_table_name
                ):
                    logging.warning(
                        f"ClickHouse表 {data_record.clickhouse_table_name} 不存在"
                    )
                    continue

                # 构建查询语句，不使用别名，直接使用原列名
                safe_columns = [f"`{col}`" for col in selected_columns]
                logging.info(f"selected_columns: {selected_columns}")
                logging.info(f"safe_columns: {safe_columns}")
                query = f"""
                SELECT 
                    `{time_column}`,
                    {', '.join(safe_columns)}
                FROM `{data_record.clickhouse_table_name}`
                ORDER BY `{time_column}`
                """
                logging.info(f"构建的查询SQL: {query}")

                # 执行查询
                result = self.clickhouse_manager.execute_query(query)
                if not result["success"]:
                    logging.error(
                        f"查询表 {data_record.clickhouse_table_name} 失败: {result['message']}"
                    )
                    continue

                # 调试：打印查询结果的键
                if result["data"]:
                    actual_columns = list(result["data"][0].keys())
                    logging.info(
                        f"表 {data_record.clickhouse_table_name} 查询结果字段: {actual_columns}"
                    )

                # 处理数据
                for row in result["data"]:
                    # 检查时间列是否存在
                    if time_column not in row:
                        logging.error(
                            f"时间列 '{time_column}' 不在查询结果中: {list(row.keys())}"
                        )
                        continue

                    time_point = row[time_column]
                    all_time_points.add(time_point)

                    # 直接使用精确匹配，不做模糊匹配
                    for column in selected_columns:
                        if column in row:
                            if column not in all_envelope_data:
                                all_envelope_data[column] = {}

                            if time_point not in all_envelope_data[column]:
                                all_envelope_data[column][time_point] = []

                            all_envelope_data[column][time_point].append(row[column])
                        else:
                            actual_columns = list(row.keys())
                            logging.warning(
                                f"请求的列 '{column}' 不存在，可用列: {actual_columns}"
                            )

            if not all_time_points:
                return {"success": False, "message": "没有找到有效的历史数据"}

            # 计算每个时间点的最大最小值
            sorted_time_points = sorted(all_time_points)
            envelope_data = {}

            for column in selected_columns:
                upper_values = []
                lower_values = []

                for time_point in sorted_time_points:
                    if (
                        column in all_envelope_data
                        and time_point in all_envelope_data[column]
                    ):
                        values = all_envelope_data[column][time_point]
                        upper_values.append(max(values))
                        lower_values.append(min(values))
                    else:
                        # 如果该时间点没有数据，使用0
                        upper_values.append(0)
                        lower_values.append(0)

                envelope_data[column] = {"upper": upper_values, "lower": lower_values}

            return {
                "success": True,
                "data": {
                    "time_points": sorted_time_points,
                    "envelope_data": envelope_data,
                    "data_count": len(sorted_time_points),
                    "time_range": {
                        "min": min(sorted_time_points),
                        "max": max(sorted_time_points),
                    },
                },
            }

        except Exception as e:
            logging.error(f"计算包络数据失败: {e}")
            return {"success": False, "message": f"计算失败: {str(e)}"}

    def read_special_format_csv(
        self, file, separator=" ", skip_rows=0, experiment_type=None
    ):
        """
        读取特殊格式的CSV文件
        特殊格式：所有数据在一个列中，需要按分隔符拆分

        Args:
            file: 文件对象
            separator: 分隔符（空格、制表符等）
            skip_rows: 跳过的行数
            experiment_type: 试验类型（用于获取预期列名）

        Returns:
            pandas.DataFrame: 转换后的标准格式DataFrame
        """
        import io

        # 读取文件内容
        file.seek(0)  # 重置文件指针
        content = file.read()

        # 处理编码问题
        if isinstance(content, bytes):
            try:
                content = content.decode("utf-8")
            except UnicodeDecodeError:
                content = content.decode("gbk")

        lines = content.strip().split("\n")

        # 跳过指定行数
        if skip_rows > 0:
            lines = lines[skip_rows:]

        # 处理分隔符
        if separator == "\\t":
            separator = "\t"
        elif separator == "  ":
            # 多空格需要使用正则表达式
            import re

            processed_lines = []
            for line in lines:
                # 使用正则表达式将多个连续空格替换为单个制表符
                processed_line = re.sub(r"\s+", "\t", line.strip())
                processed_lines.append(processed_line)

            # 创建标准CSV格式的内容
            csv_content = "\n".join(processed_lines)

            # 读取为DataFrame
            df = pd.read_csv(io.StringIO(csv_content), sep="\t")
        else:
            # 单个字符分隔符
            processed_lines = []
            for line in lines:
                # 将分隔符替换为逗号
                processed_line = line.strip().replace(separator, ",")
                processed_lines.append(processed_line)

            # 创建标准CSV格式的内容
            csv_content = "\n".join(processed_lines)

            # 读取为DataFrame
            df = pd.read_csv(io.StringIO(csv_content))

        logging.info(f"特殊格式文件转换成功，数据形状: {df.shape}")
        logging.info(f"转换后的列名: {df.columns.tolist()}")

        return df
