from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from config import config
from database import init_db, db
from models.models import ExperimentType, ExperimentData, EnvelopeSettings
from services.data_processor import DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 启用CORS支持前后端分离
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": "*"
        }
    })
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    init_db(app)
    
    # 注册API路由
    register_api_routes(app)
    
    return app

def register_api_routes(app):
    """注册所有API路由"""
    
    @app.route('/api/experiment-types', methods=['GET'])
    def get_experiment_types():
        """获取所有试验类型"""
        try:
            experiment_types = ExperimentType.query.all()
            return jsonify({
                'success': True,
                'data': [et.to_dict() for et in experiment_types]
            })
        except Exception as e:
            logging.error(f'获取试验类型失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-types', methods=['POST'])
    def create_experiment_type():
        """创建试验类型"""
        try:
            data = request.json
            name = data.get('name')
            description = data.get('description', '')
            time_column = data.get('time_column', 't')
            data_columns = data.get('data_columns', [])
            
            if not name or not data_columns:
                return jsonify({'success': False, 'message': '名称和数据列不能为空'}), 400
            
            # 创建试验类型
            experiment_type = ExperimentType(
                name=name,
                description=description,
                time_column=time_column,
                data_columns=data_columns
            )
            
            db.session.add(experiment_type)
            db.session.commit()
            
            # 创建对应的数据表
            from database import create_experiment_data_table
            create_experiment_data_table(experiment_type.id, data_columns)
            
            return jsonify({
                'success': True, 
                'message': f'试验类型 "{name}" 创建成功',
                'data': experiment_type.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'创建试验类型失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-types/<int:type_id>', methods=['DELETE'])
    def delete_experiment_type(type_id):
        """删除试验类型"""
        try:
            experiment_type = ExperimentType.query.get_or_404(type_id)
            
            # 检查是否有关联的数据
            related_data = ExperimentData.query.filter_by(experiment_type_id=type_id).first()
            if related_data:
                return jsonify({'success': False, 'message': '无法删除：该试验类型还有关联的数据'}), 400
            
            db.session.delete(experiment_type)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'试验类型 "{experiment_type.name}" 删除成功'
            })
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'删除试验类型失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/upload/<int:experiment_type_id>', methods=['POST'])
    def upload_data(experiment_type_id):
        """处理数据上传"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': '没有选择文件'}), 400
            
            file = request.files['file']
            data_name = request.form.get('data_name', '')
            
            if file.filename == '':
                return jsonify({'success': False, 'message': '没有选择文件'}), 400
            
            if not data_name:
                return jsonify({'success': False, 'message': '请输入数据名称'}), 400
            
            # 处理文件上传
            processor = DataProcessor()
            result = processor.process_upload(file, data_name, experiment_type)
            
            if result['success']:
                return jsonify({
                    'success': True, 
                    'message': '上传成功',
                    'data_id': result['data_id']
                })
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
                
        except Exception as e:
            logging.error(f'上传数据失败: {e}')
            return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500
    
    @app.route('/api/preview/<int:experiment_type_id>', methods=['POST'])
    def preview_data(experiment_type_id):
        """预览上传的文件数据"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': '没有选择文件'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': '没有选择文件'})
            
            # 使用数据处理器预览文件
            from services.data_processor import DataProcessor
            processor = DataProcessor()
            
            preview_result = processor.preview_file(file, experiment_type)
            
            return jsonify({
                'success': True,
                'preview': preview_result
            })
            
        except Exception as e:
            logging.error(f'预览文件失败: {e}')
            return jsonify({'success': False, 'message': f'预览失败: {str(e)}'})
    
    @app.route('/api/envelope/<int:experiment_type_id>/info', methods=['GET'])
    def get_envelope_info(experiment_type_id):
        """获取包络分析信息"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            experiment_data = ExperimentData.query.filter_by(
                experiment_type_id=experiment_type_id,
                status='active'
            ).all()
            
            # 获取当前包络设置
            envelope_settings = EnvelopeSettings.query.filter_by(
                experiment_type_id=experiment_type_id
            ).first()
            
            return jsonify({
                'success': True,
                'data': {
                    'experiment_type': experiment_type.to_dict(),
                    'experiment_data': [ed.to_dict() for ed in experiment_data],
                    'envelope_settings': envelope_settings.to_dict() if envelope_settings else None
                }
            })
            
        except Exception as e:
            logging.error(f'获取包络分析信息失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-data/<int:experiment_type_id>', methods=['GET'])
    def get_experiment_data_list(experiment_type_id):
        """获取试验类型下的所有试验数据"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            
            # 获取所有试验数据
            experiment_data = ExperimentData.query.filter_by(
                experiment_type_id=experiment_type_id,
                status='active'
            ).order_by(ExperimentData.upload_time.desc()).all()
            
            data_list = []
            for data in experiment_data:
                data_dict = data.to_dict()
                # 添加一些额外的统计信息
                data_dict['upload_time_formatted'] = data.upload_time.strftime('%Y-%m-%d %H:%M:%S') if data.upload_time else ''
                data_list.append(data_dict)
            
            # 获取统计信息
            total_count = len(experiment_data)
            historical_count = sum(1 for data in experiment_data if data.is_historical)
            total_rows = sum(data.row_count for data in experiment_data if data.row_count)
            
            return jsonify({
                'success': True,
                'data': {
                    'experiment_type': experiment_type.to_dict(),
                    'experiment_data': data_list,
                    'statistics': {
                        'total_count': total_count,
                        'historical_count': historical_count,
                        'active_count': total_count - historical_count,
                        'total_rows': total_rows
                    }
                }
            })
            
        except Exception as e:
            logging.error(f'获取试验数据列表失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-data/<int:data_id>/historical', methods=['POST'])
    def update_historical_status(data_id):
        """更新试验数据的历史数据标记"""
        try:
            experiment_data = ExperimentData.query.get_or_404(data_id)
            
            data = request.json
            is_historical = data.get('is_historical', False)
            
            experiment_data.is_historical = is_historical
            db.session.commit()
            
            status_text = "历史数据" if is_historical else "活跃数据"
            
            return jsonify({
                'success': True,
                'message': f'数据 "{experiment_data.data_name}" 已标记为{status_text}',
                'data': experiment_data.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'更新历史数据标记失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-data/<int:data_id>', methods=['DELETE'])
    def delete_experiment_data(data_id):
        """删除试验数据"""
        try:
            experiment_data = ExperimentData.query.get_or_404(data_id)
            
            # 软删除，只修改状态
            experiment_data.status = 'deleted'
            db.session.commit()
            
            # TODO: 可以考虑同时删除ClickHouse中的表
            # 但为了数据安全，暂时只做软删除
            
            return jsonify({
                'success': True,
                'message': f'数据 "{experiment_data.data_name}" 删除成功'
            })
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'删除试验数据失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/experiment-data/<int:data_id>/info', methods=['GET'])
    def get_experiment_data_info(data_id):
        """获取试验数据详细信息"""
        try:
            experiment_data = ExperimentData.query.get_or_404(data_id)
            
            data_info = experiment_data.to_dict()
            
            # 如果有ClickHouse表名，获取表信息
            if experiment_data.clickhouse_table_name:
                try:
                    from services.clickhouse_manager import get_clickhouse_manager
                    ch_manager = get_clickhouse_manager()
                    table_info = ch_manager.get_table_info(experiment_data.clickhouse_table_name)
                    data_info['clickhouse_info'] = table_info
                except Exception as e:
                    logging.warning(f'获取ClickHouse表信息失败: {e}')
                    data_info['clickhouse_info'] = {'error': str(e)}
            
            return jsonify({
                'success': True,
                'data': data_info
            })
            
        except Exception as e:
            logging.error(f'获取试验数据信息失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/envelope/<int:experiment_type_id>/settings', methods=['GET', 'POST'])
    def envelope_settings_api(experiment_type_id):
        """包络设置API"""
        if request.method == 'POST':
            try:
                data = request.json
                selected_columns = data.get('selected_columns', [])
                
                # 更新或创建包络设置
                settings = EnvelopeSettings.query.filter_by(
                    experiment_type_id=experiment_type_id
                ).first()
                
                if settings:
                    settings.selected_columns = selected_columns
                    settings.updated_at = datetime.now()
                else:
                    settings = EnvelopeSettings(
                        experiment_type_id=experiment_type_id,
                        selected_columns=selected_columns
                    )
                    db.session.add(settings)
                
                db.session.commit()
                
                return jsonify({'success': True, 'message': '设置保存成功'})
                
            except Exception as e:
                db.session.rollback()
                logging.error(f'保存包络设置失败: {e}')
                return jsonify({'success': False, 'message': str(e)})
        
        else:
            settings = EnvelopeSettings.query.filter_by(
                experiment_type_id=experiment_type_id
            ).first()
            
            return jsonify(settings.to_dict() if settings else {})
    
    @app.route('/api/envelope/<int:experiment_type_id>/envelope', methods=['POST'])
    def get_envelope_data(experiment_type_id):
        """获取包络数据API"""
        try:
            data = request.get_json()
            selected_columns = data.get('selected_columns', [])
            
            # 新增参数：采样配置
            use_sampling = data.get('use_sampling', True)
            sampling_points = data.get('sampling_points', 200)
            
            if not selected_columns:
                return jsonify({
                    'success': False,
                    'message': '请选择要分析的数据列'
                }), 400
            
            processor = DataProcessor()
            envelope_data = processor.calculate_envelope_for_columns(
                experiment_type_id, 
                selected_columns,
                sampling_points=sampling_points,
                use_sampling=use_sampling
            )
            
            if 'error' in envelope_data:
                return jsonify({
                    'success': False,
                    'message': envelope_data['error']
                }), 400
            
            return jsonify({
                'success': True,
                'data': envelope_data
            })
            
        except Exception as e:
            logging.error(f'获取包络数据失败: {e}')
            return jsonify({
                'success': False,
                'message': f'获取包络数据失败: {str(e)}'
            }), 500
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    # 包络分析相关接口
    @app.route('/api/envelope/<int:experiment_type_id>/temp-upload', methods=['POST'])
    def upload_temp_comparison_data(experiment_type_id):
        """上传临时对比数据到ClickHouse"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': '没有选择文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': '没有选择文件'}), 400
            
            processor = DataProcessor()
            result = processor.process_temp_upload(file, experiment_type)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': '临时数据上传成功',
                    'data': {
                        'temp_data_id': result['temp_data_id'],
                        'row_count': result['row_count'],
                        'columns': result['columns'],
                        'time_range': result['time_range']
                    }
                })
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
                
        except Exception as e:
            logging.error(f'上传临时数据失败: {e}')
            return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500
    
    @app.route('/api/envelope/<int:experiment_type_id>/compare', methods=['POST'])
    def compare_envelope_data(experiment_type_id):
        """获取包络对比数据"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            data = request.json
            
            selected_columns = data.get('selected_columns', [])
            temp_data_id = data.get('temp_data_id')
            
            # 新增：对比数据采样配置
            use_sampling = data.get('use_sampling', True)
            sampling_points = data.get('sampling_points', 200)
            
            if not selected_columns:
                return jsonify({'success': False, 'message': '请选择要对比的数据列'}), 400
            
            if not temp_data_id:
                return jsonify({'success': False, 'message': '缺少临时数据ID'}), 400
            
            processor = DataProcessor()
            
            # 获取历史包络数据（使用之前设置的采样配置）
            envelope_result = processor.calculate_envelope_simple(experiment_type_id, selected_columns)
            if not envelope_result['success']:
                return jsonify({'success': False, 'message': f'获取历史包络失败: {envelope_result["message"]}'}), 400
            
            # 获取临时对比数据（应用采样配置）
            comparison_result = processor.get_temp_comparison_data(
                temp_data_id, 
                experiment_type.time_column, 
                selected_columns,
                use_sampling=use_sampling,
                sampling_points=sampling_points
            )
            if not comparison_result['success']:
                return jsonify({'success': False, 'message': f'获取对比数据失败: {comparison_result["message"]}'}), 400
            
            return jsonify({
                'success': True,
                'data': {
                    'envelope_data': envelope_result['data'],
                    'comparison_data': comparison_result['data'],
                    'comparison_sampling_info': {
                        'use_sampling': use_sampling,
                        'sampling_points': comparison_result['data'].get('sampling_points', 0),
                        'original_points': comparison_result['data'].get('original_points', 0),
                        'sampling_method': comparison_result['data'].get('sampling_method', 'unknown')
                    }
                }
            })
            
        except Exception as e:
            logging.error(f'包络对比失败: {e}')
            return jsonify({'success': False, 'message': f'对比失败: {str(e)}'}), 500
    
    @app.route('/api/envelope/<int:experiment_type_id>/save-temp', methods=['POST'])
    def save_temp_data(experiment_type_id):
        """保存临时数据到MySQL"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            data = request.json
            
            temp_data_id = data.get('temp_data_id')
            data_name = data.get('data_name')
            file_name = data.get('file_name', 'comparison_data.csv')
            
            if not temp_data_id or not data_name:
                return jsonify({'success': False, 'message': '缺少必要参数'}), 400
            
            processor = DataProcessor()
            result = processor.save_temp_data_to_mysql(temp_data_id, data_name, experiment_type, file_name)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'data_id': result['data_id']
                })
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
                
        except Exception as e:
            logging.error(f'保存临时数据失败: {e}')
            return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500
    
    @app.route('/api/envelope/<int:experiment_type_id>/delete-temp', methods=['POST'])
    def delete_temp_data(experiment_type_id):
        """删除临时数据"""
        try:
            data = request.json
            temp_data_id = data.get('temp_data_id')
            
            if not temp_data_id:
                return jsonify({'success': False, 'message': '缺少临时数据ID'}), 400
            
            processor = DataProcessor()
            result = processor.delete_temp_table(temp_data_id)
            
            if result['success']:
                return jsonify({'success': True, 'message': '临时数据删除成功'})
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
                
        except Exception as e:
            logging.error(f'删除临时数据失败: {e}')
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
    
    @app.route('/api/data-management/<int:experiment_type_id>')
    def get_data_management_info(experiment_type_id):
        """获取数据管理信息"""
        try:
            experiment_type = ExperimentType.query.get_or_404(experiment_type_id)
            experiment_data = ExperimentData.query.filter_by(
                experiment_type_id=experiment_type_id,
                status='active'
            ).all()
            
            return jsonify({
                'success': True,
                'data': {
                    'experiment_type': experiment_type.to_dict(),
                    'experiment_data': [ed.to_dict() for ed in experiment_data]
                }
            })
            
        except Exception as e:
            logging.error(f'获取数据管理信息失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'API endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)