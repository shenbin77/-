"""
AI分析API接口
提供股票AI分析的REST API服务
"""

import logging
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from app.extensions import db
from app.models.ai_analysis_result import AIAnalysisResult, AIModelConfig
from app.services.ai_analysis_service import ai_analysis_service

logger = logging.getLogger(__name__)

# 创建蓝图
ai_analysis_bp = Blueprint('ai_analysis', __name__, url_prefix='/api/ai-analysis')

@ai_analysis_bp.route('/health', methods=['GET'])
def check_ai_service_health():
    """检查AI服务健康状态"""
    try:
        is_healthy = ai_analysis_service.check_service_health()
        return jsonify({
            'success': True,
            'healthy': is_healthy,
            'message': 'AI服务正常' if is_healthy else 'AI服务不可用'
        })
    except Exception as e:
        logger.error(f"检查AI服务健康状态失败: {e}")
        return jsonify({
            'success': False,
            'healthy': False,
            'message': f'检查失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/supported-analysts', methods=['GET'])
def get_supported_analysts():
    """获取支持的分析师类型"""
    try:
        analysts = ai_analysis_service.get_supported_analysts()
        return jsonify({
            'success': True,
            'data': analysts
        })
    except Exception as e:
        logger.error(f"获取分析师类型失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/supported-models', methods=['GET'])
def get_supported_models():
    """获取支持的模型列表"""
    try:
        models = ai_analysis_service.get_supported_models()
        return jsonify({
            'success': True,
            'data': models
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/analyze', methods=['POST'])
def analyze_stock():
    """分析股票"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        if not data or 'stock_code' not in data:
            return jsonify({
                'success': False,
                'message': '缺少股票代码参数'
            }), 400
        
        stock_code = data['stock_code']
        
        # 解析分析配置
        config = data.get('config', {})
        analysts = config.get('analysts', ['market', 'fundamentals', 'news'])
        depth = config.get('depth', 'standard')
        llm_provider = config.get('llm_provider', 'dashscope')
        model = config.get('model', 'qwen-plus')
        include_quantitative = config.get('include_quantitative_data', True)
        trade_date = data.get('trade_date')
        
        # 执行AI分析
        result = ai_analysis_service.analyze_stock(
            stock_code=stock_code,
            analysts=analysts,
            depth=depth,
            llm_provider=llm_provider,
            model=model,
            include_quantitative_data=include_quantitative,
            trade_date=trade_date
        )
        
        if result['success']:
            # 保存分析结果到数据库
            try:
                ai_record = AIAnalysisResult.from_ai_result(
                    result['data'],
                    {
                        'analysts': analysts,
                        'depth': depth,
                        'llm_provider': llm_provider,
                        'model': model,
                        'quantitative_data': data.get('quantitative_data', {})
                    }
                )
                ai_record.analysis_duration = result.get('duration')
                
                db.session.add(ai_record)
                db.session.commit()
                
                logger.info(f"AI分析结果已保存: {stock_code}, ID: {ai_record.id}")
                
                # 添加记录ID到返回结果
                result['data']['record_id'] = ai_record.id
                
            except Exception as e:
                logger.error(f"保存AI分析结果失败: {e}")
                # 不影响分析结果返回
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"股票AI分析失败: {e}")
        return jsonify({
            'success': False,
            'message': f'分析失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze_stocks():
    """批量分析股票"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        if not data or 'stock_codes' not in data:
            return jsonify({
                'success': False,
                'message': '缺少股票代码列表参数'
            }), 400
        
        stock_codes = data['stock_codes']
        if not isinstance(stock_codes, list) or len(stock_codes) == 0:
            return jsonify({
                'success': False,
                'message': '股票代码列表不能为空'
            }), 400
        
        # 限制批量分析数量
        if len(stock_codes) > 20:
            return jsonify({
                'success': False,
                'message': '批量分析最多支持20只股票'
            }), 400
        
        # 解析分析配置
        config = data.get('config', {})
        analysts = config.get('analysts', ['market', 'fundamentals'])
        depth = config.get('depth', 'quick')  # 批量分析默认使用快速模式
        
        # 执行批量分析
        result = ai_analysis_service.batch_analyze_stocks(
            stock_codes=stock_codes,
            analysts=analysts,
            depth=depth
        )
        
        # 保存成功的分析结果
        saved_count = 0
        for stock_code, analysis_data in result['results'].items():
            try:
                ai_record = AIAnalysisResult.from_ai_result(
                    analysis_data,
                    {
                        'analysts': analysts,
                        'depth': depth,
                        'llm_provider': config.get('llm_provider', 'dashscope'),
                        'model': config.get('model', 'qwen-turbo')
                    }
                )
                
                db.session.add(ai_record)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存批量分析结果失败 {stock_code}: {e}")
        
        if saved_count > 0:
            db.session.commit()
            logger.info(f"批量分析结果已保存: {saved_count} 条记录")
        
        return jsonify({
            'success': True,
            'data': result,
            'saved_count': saved_count
        })
        
    except Exception as e:
        logger.error(f"批量股票AI分析失败: {e}")
        return jsonify({
            'success': False,
            'message': f'批量分析失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/history/<stock_code>', methods=['GET'])
def get_analysis_history(stock_code):
    """获取股票的AI分析历史"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # 最多返回50条记录
        
        records = AIAnalysisResult.get_latest_by_stock(stock_code, limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records],
            'count': len(records)
        })
        
    except Exception as e:
        logger.error(f"获取AI分析历史失败 {stock_code}: {e}")
        return jsonify({
            'success': False,
            'message': f'获取历史失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/results/by-rating/<rating>', methods=['GET'])
def get_results_by_rating(rating):
    """根据评级获取分析结果"""
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)
        
        records = AIAnalysisResult.get_by_rating(rating.upper(), limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records],
            'count': len(records)
        })
        
    except Exception as e:
        logger.error(f"根据评级获取分析结果失败 {rating}: {e}")
        return jsonify({
            'success': False,
            'message': f'获取结果失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/results/high-confidence', methods=['GET'])
def get_high_confidence_results():
    """获取高信心度的分析结果"""
    try:
        min_confidence = request.args.get('min_confidence', 0.8, type=float)
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)
        
        records = AIAnalysisResult.get_high_confidence_results(min_confidence, limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records],
            'count': len(records),
            'min_confidence': min_confidence
        })
        
    except Exception as e:
        logger.error(f"获取高信心度分析结果失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取结果失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/statistics', methods=['GET'])
def get_analysis_statistics():
    """获取AI分析统计信息"""
    try:
        stats = AIAnalysisResult.get_analysis_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取AI分析统计失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/model-configs', methods=['GET'])
def get_model_configs():
    """获取AI模型配置列表"""
    try:
        configs = AIModelConfig.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        })
        
    except Exception as e:
        logger.error(f"获取模型配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500

@ai_analysis_bp.route('/model-configs', methods=['POST'])
def create_model_config():
    """创建AI模型配置"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['model_name', 'llm_provider', 'model_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需参数: {field}'
                }), 400
        
        # 创建配置
        config = AIModelConfig(
            model_name=data['model_name'],
            llm_provider=data['llm_provider'],
            model_type=data['model_type'],
            analysts_config=data.get('analysts_config', '["market", "fundamentals"]'),
            analysis_depth=data.get('analysis_depth', 'standard'),
            max_debate_rounds=data.get('max_debate_rounds', 2),
            online_tools=data.get('online_tools', True),
            description=data.get('description', '')
        )
        
        db.session.add(config)
        db.session.commit()
        
        logger.info(f"AI模型配置已创建: {config.model_name}")
        
        return jsonify({
            'success': True,
            'data': config.to_dict(),
            'message': '模型配置创建成功'
        })
        
    except Exception as e:
        logger.error(f"创建AI模型配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 500
