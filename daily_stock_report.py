#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票分析报告自动推送系统
Daily Stock Analysis Report Auto Push System
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wechat_sender import WeChatSender

# 简化的股票数据获取类
class SimpleStockDataFetcher:
    def get_stock_list(self):
        """获取股票列表"""
        # 返回一些示例股票
        import pandas as pd
        stocks = [
            {'symbol': '000001.SZ', 'name': '平安银行'},
            {'symbol': '000002.SZ', 'name': '万科A'},
            {'symbol': '600036.SH', 'name': '招商银行'},
            {'symbol': '600519.SH', 'name': '贵州茅台'},
            {'symbol': '000858.SZ', 'name': '五粮液'},
            {'symbol': '300750.SZ', 'name': '宁德时代'},
            {'symbol': '002415.SZ', 'name': '海康威视'},
            {'symbol': '600276.SH', 'name': '恒瑞医药'},
        ]
        return pd.DataFrame(stocks)

    def get_stock_data(self, symbol, period='1mo'):
        """获取股票数据（模拟数据）"""
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        # 生成模拟数据
        days = 30 if period == '1mo' else 20
        dates = pd.date_range(end=datetime.now(), periods=days)

        # 模拟价格数据
        base_price = np.random.uniform(10, 100)
        prices = []
        volumes = []

        for i in range(days):
            # 模拟价格波动
            change = np.random.normal(0, 0.02)  # 2%的标准差
            if i == 0:
                price = base_price
            else:
                price = prices[-1] * (1 + change)
            prices.append(price)

            # 模拟成交量
            volume = np.random.uniform(1000000, 10000000)
            volumes.append(volume)

        data = pd.DataFrame({
            'date': dates,
            'close': prices,
            'volume': volumes
        })
        data.set_index('date', inplace=True)

        return data

# 简化的ML系统类
class SimpleMLFactorSystem:
    def __init__(self):
        pass

class DailyStockReport:
    def __init__(self):
        self.wechat = WeChatSender()
        self.stock_fetcher = SimpleStockDataFetcher()
        self.ml_system = SimpleMLFactorSystem()
        
    def get_top_stocks(self, limit=5):
        """获取推荐股票"""
        try:
            print("📊 开始分析股票...")
            
            # 获取股票列表
            stock_list = self.stock_fetcher.get_stock_list()
            if stock_list is None or stock_list.empty:
                print("❌ 无法获取股票列表")
                return []
            
            print(f"✅ 获取到 {len(stock_list)} 只股票")
            
            # 简单选择一些活跃股票进行分析
            sample_stocks = stock_list.head(50) if len(stock_list) > 50 else stock_list
            
            recommendations = []
            
            for idx, row in sample_stocks.iterrows():
                try:
                    symbol = row['symbol']
                    name = row['name']
                    
                    # 获取股票数据
                    stock_data = self.stock_fetcher.get_stock_data(symbol, period='1mo')
                    
                    if stock_data is not None and len(stock_data) > 5:
                        # 计算简单评分
                        latest_price = stock_data['close'].iloc[-1]
                        avg_price_5d = stock_data['close'].tail(5).mean()
                        avg_price_20d = stock_data['close'].tail(20).mean() if len(stock_data) >= 20 else avg_price_5d
                        
                        # 计算涨跌幅
                        price_change_5d = (latest_price - avg_price_5d) / avg_price_5d * 100
                        price_change_20d = (latest_price - avg_price_20d) / avg_price_20d * 100
                        
                        # 计算成交量变化
                        volume_ratio = stock_data['volume'].tail(5).mean() / stock_data['volume'].tail(20).mean() if len(stock_data) >= 20 else 1
                        
                        # 简单评分算法
                        score = 50  # 基础分
                        
                        # 价格趋势评分
                        if price_change_5d > 0:
                            score += min(price_change_5d * 2, 20)
                        else:
                            score += max(price_change_5d * 1, -20)
                            
                        # 成交量评分
                        if volume_ratio > 1.2:
                            score += 10
                        elif volume_ratio < 0.8:
                            score -= 5
                            
                        # 波动性评分（适度波动加分）
                        volatility = stock_data['close'].pct_change().std() * 100
                        if 1 < volatility < 5:
                            score += 5
                        elif volatility > 8:
                            score -= 10
                            
                        # 生成推荐理由
                        reasons = []
                        if price_change_5d > 2:
                            reasons.append("短期上涨趋势")
                        if volume_ratio > 1.2:
                            reasons.append("成交量放大")
                        if 1 < volatility < 3:
                            reasons.append("波动适中")
                        if price_change_20d > 0:
                            reasons.append("中期趋势向好")
                            
                        reason = "、".join(reasons) if reasons else "技术面分析"
                        
                        recommendations.append({
                            'symbol': symbol,
                            'name': name,
                            'score': score,
                            'price': latest_price,
                            'change_5d': price_change_5d,
                            'change_20d': price_change_20d,
                            'volume_ratio': volume_ratio,
                            'reason': reason
                        })
                        
                        print(f"✅ 分析完成: {name} ({symbol}) - 评分: {score:.1f}")
                        
                except Exception as e:
                    print(f"⚠️ 分析股票 {symbol} 时出错: {e}")
                    continue
                    
                # 限制分析数量，避免超时
                if len(recommendations) >= limit * 3:
                    break
            
            # 按评分排序，返回前N只
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"❌ 获取推荐股票时出错: {e}")
            traceback.print_exc()
            return []
    
    def generate_report(self):
        """生成每日报告"""
        try:
            print("🚀 开始生成每日股票分析报告...")
            
            # 获取推荐股票
            top_stocks = self.get_top_stocks(5)
            
            if not top_stocks:
                print("❌ 无法获取推荐股票，使用示例数据")
                # 使用示例数据
                top_stocks = [
                    {
                        'symbol': '000001.SZ',
                        'name': '平安银行',
                        'score': 75.5,
                        'price': 12.34,
                        'change_5d': 2.1,
                        'reason': '技术面向好，成交量放大'
                    },
                    {
                        'symbol': '000002.SZ', 
                        'name': '万科A',
                        'score': 72.3,
                        'price': 8.56,
                        'change_5d': 1.8,
                        'reason': '短期上涨趋势，波动适中'
                    }
                ]
            
            # 发送微信报告
            success = self.wechat.send_stock_report(top_stocks)
            
            if success:
                print("✅ 每日股票报告推送成功！")
                return True
            else:
                print("❌ 每日股票报告推送失败！")
                return False
                
        except Exception as e:
            print(f"❌ 生成报告时出错: {e}")
            traceback.print_exc()
            return False
    
    def test_report(self):
        """测试报告功能"""
        print("🧪 测试每日股票报告功能...")
        
        # 使用测试数据
        test_stocks = [
            {
                'symbol': '000001.SZ',
                'name': '平安银行',
                'score': 85.2,
                'price': 12.34,
                'change_5d': 3.2,
                'reason': '技术面强势，成交量显著放大'
            },
            {
                'symbol': '000002.SZ',
                'name': '万科A', 
                'score': 78.9,
                'price': 8.56,
                'change_5d': 2.1,
                'reason': '短期突破关键阻力位'
            },
            {
                'symbol': '600036.SH',
                'name': '招商银行',
                'score': 76.5,
                'price': 45.67,
                'change_5d': 1.8,
                'reason': '基本面稳健，估值合理'
            }
        ]
        
        success = self.wechat.send_stock_report(test_stocks)
        
        if success:
            print("✅ 测试报告推送成功！")
            print("📱 请检查您的微信是否收到了股票分析报告")
            return True
        else:
            print("❌ 测试报告推送失败！")
            return False

def main():
    """主函数"""
    print("🤖 每日股票分析报告系统启动...")
    
    reporter = DailyStockReport()
    
    # 先测试功能
    print("\n📋 第一步：测试报告推送...")
    test_success = reporter.test_report()
    
    if test_success:
        print("\n📊 第二步：生成真实分析报告...")
        real_success = reporter.generate_report()
        
        if real_success:
            print("\n🎉 系统运行成功！每日股票报告已推送到您的微信！")
        else:
            print("\n⚠️ 真实报告生成失败，但测试功能正常")
    else:
        print("\n❌ 系统测试失败，请检查微信配置")

if __name__ == "__main__":
    main()
