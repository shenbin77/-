"""
AI分析结果数据模型
存储TradingAgents-CN的分析结果
"""

from datetime import datetime
from app.extensions import db
import json

class AIAnalysisResult(db.Model):
    """AI分析结果表"""
    __tablename__ = 'ai_analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 股票信息
    stock_code = db.Column(db.String(20), nullable=False, index=True, comment='股票代码')
    stock_name = db.Column(db.String(100), comment='股票名称')
    market = db.Column(db.String(20), default='A股', comment='市场类型')
    
    # 分析配置
    analysts_used = db.Column(db.Text, comment='使用的分析师类型(JSON)')
    analysis_depth = db.Column(db.String(20), default='standard', comment='分析深度')
    llm_provider = db.Column(db.String(50), comment='LLM提供商')
    llm_model = db.Column(db.String(100), comment='使用的模型')
    
    # 分析结果
    overall_rating = db.Column(db.String(20), comment='总体评级')
    confidence_score = db.Column(db.Float, comment='信心指数(0-1)')
    risk_score = db.Column(db.Float, comment='风险评分(0-1)')
    target_price = db.Column(db.Float, comment='目标价格')
    
    # 详细分析内容
    summary = db.Column(db.Text, comment='一句话总结')
    reasoning = db.Column(db.Text, comment='推理过程')
    detailed_analysis = db.Column(db.Text, comment='详细分析结果(JSON)')
    agents_opinions = db.Column(db.Text, comment='智能体观点(JSON)')
    
    # 量化数据
    quantitative_data = db.Column(db.Text, comment='使用的量化数据(JSON)')
    
    # 时间信息
    analysis_date = db.Column(db.Date, comment='分析日期')
    analysis_duration = db.Column(db.Float, comment='分析耗时(秒)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 状态信息
    status = db.Column(db.String(20), default='completed', comment='分析状态')
    error_message = db.Column(db.Text, comment='错误信息')
    
    def __repr__(self):
        return f'<AIAnalysisResult {self.stock_code}: {self.overall_rating}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'market': self.market,
            'analysts_used': json.loads(self.analysts_used) if self.analysts_used else [],
            'analysis_depth': self.analysis_depth,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'overall_rating': self.overall_rating,
            'confidence_score': self.confidence_score,
            'risk_score': self.risk_score,
            'target_price': self.target_price,
            'summary': self.summary,
            'reasoning': self.reasoning,
            'detailed_analysis': json.loads(self.detailed_analysis) if self.detailed_analysis else {},
            'agents_opinions': json.loads(self.agents_opinions) if self.agents_opinions else [],
            'quantitative_data': json.loads(self.quantitative_data) if self.quantitative_data else {},
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'analysis_duration': self.analysis_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_ai_result(cls, ai_result_data, request_config=None):
        """从AI分析结果创建记录"""
        
        # 解析分析日期
        analysis_date = None
        if ai_result_data.get('analysis_date'):
            try:
                analysis_date = datetime.strptime(ai_result_data['analysis_date'], '%Y-%m-%d').date()
            except:
                pass
        
        # 创建记录
        record = cls(
            stock_code=ai_result_data.get('stock_code'),
            stock_name=ai_result_data.get('stock_name'),
            market=ai_result_data.get('market', 'A股'),
            overall_rating=ai_result_data.get('overall_rating'),
            confidence_score=ai_result_data.get('confidence_score'),
            risk_score=ai_result_data.get('risk_score'),
            target_price=ai_result_data.get('target_price'),
            summary=ai_result_data.get('summary'),
            analysis_date=analysis_date,
            detailed_analysis=json.dumps(ai_result_data.get('detailed_analysis', {}), ensure_ascii=False),
            agents_opinions=json.dumps(ai_result_data.get('agents_opinions', []), ensure_ascii=False),
            status='completed'
        )
        
        # 添加请求配置信息
        if request_config:
            record.analysts_used = json.dumps(request_config.get('analysts', []), ensure_ascii=False)
            record.analysis_depth = request_config.get('depth', 'standard')
            record.llm_provider = request_config.get('llm_provider')
            record.llm_model = request_config.get('model')
            record.quantitative_data = json.dumps(request_config.get('quantitative_data', {}), ensure_ascii=False)
        
        # 添加推理过程
        full_decision = ai_result_data.get('full_decision', {})
        if full_decision:
            record.reasoning = full_decision.get('reasoning')
        
        return record
    
    @classmethod
    def get_latest_by_stock(cls, stock_code, limit=10):
        """获取股票的最新分析记录"""
        return cls.query.filter_by(
            stock_code=stock_code,
            status='completed'
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_rating(cls, rating, limit=50):
        """根据评级获取分析记录"""
        return cls.query.filter_by(
            overall_rating=rating,
            status='completed'
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_high_confidence_results(cls, min_confidence=0.8, limit=50):
        """获取高信心度的分析结果"""
        return cls.query.filter(
            cls.confidence_score >= min_confidence,
            cls.status == 'completed'
        ).order_by(cls.confidence_score.desc()).limit(limit).all()
    
    @classmethod
    def get_analysis_statistics(cls):
        """获取分析统计信息"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.count(cls.id).label('total_count'),
            func.avg(cls.confidence_score).label('avg_confidence'),
            func.avg(cls.risk_score).label('avg_risk'),
            func.avg(cls.analysis_duration).label('avg_duration')
        ).filter(cls.status == 'completed').first()
        
        # 按评级统计
        rating_stats = db.session.query(
            cls.overall_rating,
            func.count(cls.id).label('count')
        ).filter(cls.status == 'completed').group_by(cls.overall_rating).all()
        
        # 按提供商统计
        provider_stats = db.session.query(
            cls.llm_provider,
            func.count(cls.id).label('count'),
            func.avg(cls.confidence_score).label('avg_confidence')
        ).filter(cls.status == 'completed').group_by(cls.llm_provider).all()
        
        return {
            'total_analyses': stats.total_count or 0,
            'avg_confidence': round(stats.avg_confidence or 0, 3),
            'avg_risk': round(stats.avg_risk or 0, 3),
            'avg_duration': round(stats.avg_duration or 0, 1),
            'rating_distribution': {rating: count for rating, count in rating_stats},
            'provider_performance': [
                {
                    'provider': provider,
                    'count': count,
                    'avg_confidence': round(avg_conf or 0, 3)
                }
                for provider, count, avg_conf in provider_stats
            ]
        }

class AIModelConfig(db.Model):
    """AI模型配置表"""
    __tablename__ = 'ai_model_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 模型信息
    model_name = db.Column(db.String(100), nullable=False, comment='模型名称')
    llm_provider = db.Column(db.String(50), nullable=False, comment='LLM提供商')
    model_type = db.Column(db.String(50), nullable=False, comment='模型类型')
    
    # 配置信息
    analysts_config = db.Column(db.Text, comment='分析师配置(JSON)')
    analysis_depth = db.Column(db.String(20), default='standard', comment='分析深度')
    max_debate_rounds = db.Column(db.Integer, default=2, comment='最大辩论轮数')
    online_tools = db.Column(db.Boolean, default=True, comment='是否使用在线工具')
    
    # 状态信息
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    description = db.Column(db.Text, comment='模型描述')
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<AIModelConfig {self.model_name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'llm_provider': self.llm_provider,
            'model_type': self.model_type,
            'analysts_config': json.loads(self.analysts_config) if self.analysts_config else [],
            'analysis_depth': self.analysis_depth,
            'max_debate_rounds': self.max_debate_rounds,
            'online_tools': self.online_tools,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_analysis_config(self):
        """获取分析配置"""
        return {
            'analysts': json.loads(self.analysts_config) if self.analysts_config else ['market', 'fundamentals'],
            'depth': self.analysis_depth,
            'llm_provider': self.llm_provider,
            'model': self.model_type,
            'max_debate_rounds': self.max_debate_rounds,
            'online_tools': self.online_tools
        }
