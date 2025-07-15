"""
AI分析服务客户端
与TradingAgents-CN API通信，提供股票AI分析功能
"""

import requests
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from app.extensions import db
from app.models.stock_basic import StockBasic
from app.models.stock_daily_basic import StockDailyBasic
from app.models.stock_factor import StockFactor

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """AI分析服务客户端"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        初始化AI分析服务
        
        Args:
            api_base_url: TradingAgents-CN API服务地址
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 300  # 5分钟超时
        
    def check_service_health(self) -> bool:
        """
        检查AI服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        try:
            response = self.session.get(f"{self.api_base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"AI服务健康检查失败: {e}")
            return False
    
    def get_supported_analysts(self) -> List[Dict[str, str]]:
        """
        获取支持的分析师类型
        
        Returns:
            List[Dict]: 分析师类型列表
        """
        try:
            response = self.session.get(f"{self.api_base_url}/api/v1/supported_analysts")
            if response.status_code == 200:
                return response.json().get("analysts", [])
            else:
                logger.error(f"获取分析师类型失败: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取分析师类型异常: {e}")
            return []
    
    def get_supported_models(self) -> Dict[str, Any]:
        """
        获取支持的模型列表
        
        Returns:
            Dict: 模型提供商和模型列表
        """
        try:
            response = self.session.get(f"{self.api_base_url}/api/v1/supported_models")
            if response.status_code == 200:
                return response.json().get("providers", {})
            else:
                logger.error(f"获取模型列表失败: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"获取模型列表异常: {e}")
            return {}
    
    def collect_quantitative_data(self, stock_code: str, trade_date: str = None) -> Dict[str, float]:
        """
        收集股票的量化数据
        
        Args:
            stock_code: 股票代码
            trade_date: 交易日期，默认为最新日期
            
        Returns:
            Dict: 量化数据字典
        """
        quantitative_data = {}
        
        try:
            # 获取基本信息
            stock_basic = StockBasic.query.filter_by(ts_code=stock_code).first()
            if not stock_basic:
                logger.warning(f"未找到股票基本信息: {stock_code}")
                return quantitative_data
            
            # 获取最新的日线基本数据
            daily_basic_query = StockDailyBasic.query.filter_by(ts_code=stock_code)
            if trade_date:
                daily_basic_query = daily_basic_query.filter_by(trade_date=trade_date)
            else:
                daily_basic_query = daily_basic_query.order_by(StockDailyBasic.trade_date.desc())
            
            daily_basic = daily_basic_query.first()
            if daily_basic:
                quantitative_data.update({
                    "pe_ratio": daily_basic.pe,
                    "pb_ratio": daily_basic.pb,
                    "current_price": daily_basic.close,
                    "turnover_rate": daily_basic.turnover_rate,
                    "volume_ratio": daily_basic.volume_ratio,
                })
            
            # 获取最新的因子数据
            factor_query = StockFactor.query.filter_by(ts_code=stock_code)
            if trade_date:
                factor_query = factor_query.filter_by(trade_date=trade_date)
            else:
                factor_query = factor_query.order_by(StockFactor.trade_date.desc())
            
            factor = factor_query.first()
            if factor:
                quantitative_data.update({
                    "roe": factor.roe,
                    "rsi": factor.rsi_14,
                    "macd": factor.macd,
                    "ma5": factor.ma_5,
                    "ma20": factor.ma_20,
                })
            
            logger.info(f"收集到 {stock_code} 的量化数据: {len(quantitative_data)} 个指标")
            
        except Exception as e:
            logger.error(f"收集量化数据失败 {stock_code}: {e}")
        
        return quantitative_data
    
    def analyze_stock(
        self,
        stock_code: str,
        analysts: List[str] = None,
        depth: str = "standard",
        llm_provider: str = "dashscope",
        model: str = "qwen-plus",
        include_quantitative_data: bool = True,
        trade_date: str = None
    ) -> Dict[str, Any]:
        """
        分析股票
        
        Args:
            stock_code: 股票代码
            analysts: 分析师类型列表
            depth: 分析深度 (quick/standard/deep)
            llm_provider: LLM提供商
            model: 模型名称
            include_quantitative_data: 是否包含量化数据
            trade_date: 分析日期
            
        Returns:
            Dict: 分析结果
        """
        if analysts is None:
            analysts = ["market", "fundamentals", "news"]
        
        # 构建请求数据
        request_data = {
            "stock_code": stock_code,
            "market": "A股" if stock_code.endswith(('.SZ', '.SH')) else "海外",
            "analysis_config": {
                "analysts": analysts,
                "depth": depth,
                "llm_provider": llm_provider,
                "model": model,
                "max_debate_rounds": 1 if depth == "quick" else 2 if depth == "standard" else 3,
                "online_tools": True
            }
        }
        
        # 添加分析日期
        if trade_date:
            request_data["analysis_date"] = trade_date
        
        # 收集量化数据
        if include_quantitative_data:
            quantitative_data = self.collect_quantitative_data(stock_code, trade_date)
            if quantitative_data:
                request_data["quantitative_data"] = quantitative_data
        
        try:
            logger.info(f"开始AI分析: {stock_code}, 分析师: {analysts}, 深度: {depth}")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.api_base_url}/api/v1/analyze_stock",
                json=request_data,
                timeout=600  # 10分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"AI分析完成: {stock_code}, 耗时: {duration:.1f}秒")
                    return {
                        "success": True,
                        "data": result["data"],
                        "duration": duration,
                        "request_data": request_data
                    }
                else:
                    error_msg = result.get("error", "未知错误")
                    logger.error(f"AI分析失败: {stock_code}, 错误: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "duration": duration
                    }
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"AI分析请求失败: {stock_code}, {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": duration
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"AI分析超时: {stock_code}")
            return {
                "success": False,
                "error": "分析超时，请稍后重试"
            }
        except Exception as e:
            logger.error(f"AI分析异常: {stock_code}, {e}")
            return {
                "success": False,
                "error": f"分析异常: {str(e)}"
            }
    
    def batch_analyze_stocks(
        self,
        stock_codes: List[str],
        analysts: List[str] = None,
        depth: str = "quick",
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        批量分析股票
        
        Args:
            stock_codes: 股票代码列表
            analysts: 分析师类型列表
            depth: 分析深度
            max_concurrent: 最大并发数
            
        Returns:
            Dict: 批量分析结果
        """
        results = {}
        failed_stocks = []
        
        logger.info(f"开始批量AI分析: {len(stock_codes)} 只股票")
        
        for i, stock_code in enumerate(stock_codes):
            logger.info(f"分析进度: {i+1}/{len(stock_codes)} - {stock_code}")
            
            result = self.analyze_stock(
                stock_code=stock_code,
                analysts=analysts,
                depth=depth
            )
            
            if result["success"]:
                results[stock_code] = result["data"]
            else:
                failed_stocks.append({
                    "stock_code": stock_code,
                    "error": result["error"]
                })
            
            # 简单的延迟，避免过于频繁的请求
            if i < len(stock_codes) - 1:
                time.sleep(1)
        
        logger.info(f"批量分析完成: 成功 {len(results)}, 失败 {len(failed_stocks)}")
        
        return {
            "success_count": len(results),
            "failed_count": len(failed_stocks),
            "results": results,
            "failed_stocks": failed_stocks
        }
    
    def get_analysis_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取分析结果摘要
        
        Args:
            analysis_result: AI分析结果
            
        Returns:
            Dict: 分析摘要
        """
        if not analysis_result.get("success"):
            return {
                "status": "failed",
                "error": analysis_result.get("error", "分析失败")
            }
        
        data = analysis_result["data"]
        
        return {
            "status": "success",
            "stock_code": data["stock_code"],
            "stock_name": data["stock_name"],
            "overall_rating": data["overall_rating"],
            "confidence_score": data["confidence_score"],
            "risk_score": data["risk_score"],
            "target_price": data.get("target_price"),
            "summary": data["summary"],
            "analysis_date": data["analysis_date"],
            "agents_count": len(data.get("agents_opinions", [])),
            "duration": analysis_result.get("duration", 0)
        }

# 创建全局实例
ai_analysis_service = AIAnalysisService()
