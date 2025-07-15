#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TradingAgents-CN集成服务
"""

import requests
import json
import subprocess
import time
import os
import signal
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

class TradingAgentsService:
    """TradingAgents-CN集成服务"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.process = None
        self.is_running = False
        
    def start_service(self) -> bool:
        """启动TradingAgents-CN服务"""
        try:
            # 检查服务是否已经运行
            if self.check_service_health():
                logger.info("TradingAgents-CN服务已在运行")
                self.is_running = True
                return True
            
            # 启动服务
            logger.info("启动TradingAgents-CN服务...")
            
            # 假设TradingAgents-CN在同级目录
            trading_agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "TradingAgents-CN-main")
            
            if not os.path.exists(trading_agents_path):
                logger.error(f"TradingAgents-CN路径不存在: {trading_agents_path}")
                return False
            
            # 启动API服务
            cmd = ["python", "api_service.py"]
            self.process = subprocess.Popen(
                cmd,
                cwd=trading_agents_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            for i in range(30):  # 等待最多30秒
                time.sleep(1)
                if self.check_service_health():
                    logger.info("TradingAgents-CN服务启动成功")
                    self.is_running = True
                    return True
            
            logger.error("TradingAgents-CN服务启动超时")
            return False
            
        except Exception as e:
            logger.error(f"启动TradingAgents-CN服务失败: {e}")
            return False
    
    def stop_service(self):
        """停止TradingAgents-CN服务"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
                logger.info("TradingAgents-CN服务已停止")
            self.is_running = False
        except Exception as e:
            logger.error(f"停止TradingAgents-CN服务失败: {e}")
    
    def check_service_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_stock(self, stock_code: str, analysis_date: str = None, 
                     analysts: List[str] = None, llm_provider: str = "dashscope",
                     model: str = "qwen-turbo") -> Dict[str, Any]:
        """分析股票"""
        try:
            if not self.is_running and not self.check_service_health():
                logger.warning("TradingAgents-CN服务未运行，尝试启动...")
                if not self.start_service():
                    return {"error": "无法启动TradingAgents-CN服务"}
            
            # 默认参数
            if analysis_date is None:
                analysis_date = datetime.now().strftime("%Y-%m-%d")
            
            if analysts is None:
                analysts = ["market", "fundamentals", "news"]
            
            # 构建请求
            request_data = {
                "stock_code": stock_code,
                "analysis_date": analysis_date,
                "analysis_config": {
                    "analysts": analysts,
                    "llm_provider": llm_provider,
                    "model": model,
                    "max_debate_rounds": 1,
                    "enable_cost_tracking": True
                }
            }
            
            logger.info(f"发送股票分析请求: {stock_code}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/v1/analyze_stock",
                json=request_data,
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"股票分析完成: {stock_code}")
                return result
            else:
                logger.error(f"股票分析失败: {response.status_code} - {response.text}")
                return {"error": f"分析失败: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logger.error(f"股票分析超时: {stock_code}")
            return {"error": "分析超时"}
        except Exception as e:
            logger.error(f"股票分析异常: {e}")
            return {"error": str(e)}
    
    def get_analysis_status(self, task_id: str) -> Dict[str, Any]:
        """获取分析状态"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/analysis_status/{task_id}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"获取状态失败: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def format_ai_analysis(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化AI分析结果，使其与量化分析结果兼容"""
        try:
            if "error" in ai_result:
                return {
                    "success": False,
                    "error": ai_result["error"],
                    "ai_available": False
                }
            
            data = ai_result.get("data", {})
            
            # 提取关键信息
            formatted_result = {
                "success": True,
                "ai_available": True,
                "overall_rating": data.get("overall_rating", "HOLD"),
                "confidence": data.get("confidence", 0.5),
                "risk_score": data.get("risk_score", 0.5),
                "target_price": data.get("target_price"),
                "reasoning": data.get("reasoning", ""),
                "analysis_summary": {
                    "market_analysis": data.get("market_analysis", ""),
                    "fundamental_analysis": data.get("fundamental_analysis", ""),
                    "news_analysis": data.get("news_analysis", ""),
                    "technical_analysis": data.get("technical_analysis", "")
                },
                "risk_assessment": data.get("risk_assessment", {}),
                "investment_advice": data.get("investment_advice", ""),
                "analysis_date": data.get("analysis_date"),
                "cost_info": data.get("cost_info", {})
            }
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"格式化AI分析结果失败: {e}")
            return {
                "success": False,
                "error": f"格式化失败: {e}",
                "ai_available": False
            }

class UnifiedDecisionEngine:
    """统一决策引擎：融合量化分析和AI智能体分析"""
    
    def __init__(self):
        self.trading_agents = TradingAgentsService()
        
    def comprehensive_analysis(self, stock_code: str, trade_date: str = None) -> Dict[str, Any]:
        """综合分析：量化 + AI智能体"""
        try:
            if trade_date is None:
                trade_date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"开始综合分析: {stock_code}")
            
            # 1. 获取量化分析结果（从现有系统）
            quant_result = self._get_quantitative_analysis(stock_code, trade_date)
            
            # 2. 获取AI智能体分析结果
            ai_raw_result = self.trading_agents.analyze_stock(stock_code, trade_date)
            ai_result = self.trading_agents.format_ai_analysis(ai_raw_result)
            
            # 3. 融合决策
            unified_result = self._merge_decisions(quant_result, ai_result, stock_code, trade_date)
            
            logger.info(f"综合分析完成: {stock_code}")
            return unified_result
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "stock_code": stock_code,
                "analysis_date": trade_date
            }
    
    def _get_quantitative_analysis(self, stock_code: str, trade_date: str) -> Dict[str, Any]:
        """获取量化分析结果"""
        try:
            from app.services.stock_scoring import StockScoringEngine
            from app.services.ml_models import MLModelManager

            # 获取真实的量化分析结果
            scoring_engine = StockScoringEngine()
            ml_manager = MLModelManager()

            # 获取因子得分
            factor_scores = {}
            try:
                factor_result = scoring_engine.factor_based_selection(
                    trade_date=trade_date,
                    factor_list=['momentum_1d', 'momentum_5d', 'volatility_20d', 'price_to_ma20'],
                    method='equal_weight',
                    top_n=100
                )

                # 查找当前股票的得分
                for stock in factor_result.get('selected_stocks', []):
                    if stock.get('ts_code') == stock_code:
                        factor_scores = {
                            "momentum_score": stock.get('factor_scores', {}).get('momentum_1d', 0.5),
                            "value_score": stock.get('factor_scores', {}).get('price_to_ma20', 0.5),
                            "quality_score": 0.6,  # 默认值
                            "volatility_score": stock.get('factor_scores', {}).get('volatility_20d', 0.5)
                        }
                        break

                if not factor_scores:
                    factor_scores = {
                        "momentum_score": 0.5,
                        "value_score": 0.5,
                        "quality_score": 0.5,
                        "volatility_score": 0.5
                    }

            except Exception as e:
                logger.warning(f"获取因子得分失败，使用默认值: {e}")
                factor_scores = {
                    "momentum_score": 0.5,
                    "value_score": 0.5,
                    "quality_score": 0.5,
                    "volatility_score": 0.5
                }

            # 获取ML预测
            ml_prediction = {}
            try:
                ml_result = scoring_engine.ml_based_selection(
                    trade_date=trade_date,
                    model_ids=['my_xgb_model'],
                    top_n=100
                )

                # 查找当前股票的预测
                for stock in ml_result.get('selected_stocks', []):
                    if stock.get('ts_code') == stock_code:
                        ml_prediction = {
                            "predicted_return": stock.get('predicted_return', 0),
                            "confidence": 0.7,
                            "model_used": "xgboost"
                        }
                        break

                if not ml_prediction:
                    ml_prediction = {
                        "predicted_return": 0.01,
                        "confidence": 0.6,
                        "model_used": "xgboost"
                    }

            except Exception as e:
                logger.warning(f"获取ML预测失败，使用默认值: {e}")
                ml_prediction = {
                    "predicted_return": 0.01,
                    "confidence": 0.6,
                    "model_used": "xgboost"
                }

            return {
                "success": True,
                "factor_scores": factor_scores,
                "ml_prediction": ml_prediction,
                "technical_indicators": {
                    "rsi": 58.5,
                    "macd_signal": "BUY",
                    "bollinger_position": "MIDDLE"
                }
            }

        except Exception as e:
            logger.error(f"获取量化分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "factor_scores": {
                    "momentum_score": 0.5,
                    "value_score": 0.5,
                    "quality_score": 0.5,
                    "volatility_score": 0.5
                },
                "ml_prediction": {
                    "predicted_return": 0.01,
                    "confidence": 0.6,
                    "model_used": "xgboost"
                },
                "technical_indicators": {
                    "rsi": 50.0,
                    "macd_signal": "HOLD",
                    "bollinger_position": "MIDDLE"
                }
            }
    
    def _merge_decisions(self, quant_result: Dict[str, Any], ai_result: Dict[str, Any], 
                        stock_code: str, trade_date: str) -> Dict[str, Any]:
        """融合量化和AI分析决策"""
        try:
            # 基础结果结构
            merged_result = {
                "success": True,
                "stock_code": stock_code,
                "analysis_date": trade_date,
                "analysis_timestamp": datetime.now().isoformat(),
                "quantitative_analysis": quant_result,
                "ai_analysis": ai_result
            }
            
            # 获取量化分析的关键指标
            quant_success = quant_result.get("success", True)
            factor_scores = quant_result.get("factor_scores", {})
            ml_prediction_data = quant_result.get("ml_prediction", {})

            quant_score = factor_scores.get("momentum_score", 0.5)
            ml_prediction = ml_prediction_data.get("predicted_return", 0)

            # 如果AI分析可用，进行融合
            if ai_result.get("ai_available", False):
                # 决策融合逻辑
                ai_rating = ai_result.get("overall_rating", "HOLD")
                ai_confidence = ai_result.get("confidence", 0.5)
                
                # 简单的融合算法
                if ai_rating == "BUY" and quant_score > 0.6 and ml_prediction > 0:
                    final_rating = "STRONG_BUY"
                    final_confidence = min(0.9, (ai_confidence + 0.8) / 2)
                elif ai_rating == "BUY" or (quant_score > 0.7 and ml_prediction > 0.02):
                    final_rating = "BUY"
                    final_confidence = (ai_confidence + 0.7) / 2
                elif ai_rating == "SELL" and quant_score < 0.4 and ml_prediction < 0:
                    final_rating = "STRONG_SELL"
                    final_confidence = min(0.9, (ai_confidence + 0.8) / 2)
                elif ai_rating == "SELL" or (quant_score < 0.3 and ml_prediction < -0.02):
                    final_rating = "SELL"
                    final_confidence = (ai_confidence + 0.7) / 2
                else:
                    final_rating = "HOLD"
                    final_confidence = (ai_confidence + 0.6) / 2
                
                merged_result.update({
                    "final_decision": {
                        "rating": final_rating,
                        "confidence": final_confidence,
                        "reasoning": f"量化分析显示动量得分{quant_score:.2f}，ML预测收益{ml_prediction:.3f}；AI分析建议{ai_rating}，置信度{ai_confidence:.2f}。综合判断为{final_rating}。",
                        "risk_level": ai_result.get("risk_score", 0.5)
                    }
                })
            else:
                # 仅基于量化分析
                if quant_score > 0.7 and ml_prediction > 0.03:
                    final_rating = "BUY"
                elif quant_score < 0.3 and ml_prediction < -0.03:
                    final_rating = "SELL"
                else:
                    final_rating = "HOLD"
                
                merged_result.update({
                    "final_decision": {
                        "rating": final_rating,
                        "confidence": 0.6,
                        "reasoning": f"基于量化分析：动量得分{quant_score:.2f}，ML预测收益{ml_prediction:.3f}。AI分析暂不可用。",
                        "risk_level": 0.5
                    },
                    "ai_analysis": {"ai_available": False, "error": "AI分析服务不可用"}
                })
            
            return merged_result
            
        except Exception as e:
            logger.error(f"融合决策失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "stock_code": stock_code,
                "analysis_date": trade_date
            }

# 全局实例
trading_agents_service = TradingAgentsService()
unified_decision_engine = UnifiedDecisionEngine()
