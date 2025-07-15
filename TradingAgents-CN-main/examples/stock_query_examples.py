#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询示例（增强版）
演示如何使用新的股票数据服务，支持完整的降级机制
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from tradingagents.api.stock_api import (
        get_stock_info, get_all_stocks, get_stock_data,
        search_stocks, get_market_summary, check_service_status
    )
    API_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 新API不可用，使用传统方式: {e}")
    API_AVAILABLE = False
    # 回退到传统方式
    from tradingagents.dataflows.database_manager import get_database_manager

from datetime import datetime, timedelta
import pandas as pd

def demo_service_status():
    """
    演示服务状态检查
    """
    print("\n=== 服务状态检查 ===")
    
    if not API_AVAILABLE:
        print("❌ 新API不可用，跳过状态检查")
        return
    
    status = check_service_status()
    print("📊 当前服务状态:")
    
    for key, value in status.items():
        if key == 'service_available':
            icon = "✅" if value else "❌"
            print(f"  {icon} 服务可用性: {value}")
        elif key == 'mongodb_status':
            icon = "✅" if value == 'connected' else "⚠️" if value == 'disconnected' else "❌"
            print(f"  {icon} MongoDB状态: {value}")
        elif key == 'tdx_api_status':
            icon = "✅" if value == 'available' else "⚠️" if value == 'limited' else "❌"
            print(f"  {icon} 通达信API状态: {value}")
        else:
            print(f"  📋 {key}: {value}")

def demo_single_stock_query():
    """
    演示单个股票查询（带降级机制）
    """
    print("\n=== 单个股票查询示例 ===")
    
    stock_codes = ['000001', '000002', '600000', '300001']
    
    for stock_code in stock_codes:
        print(f"\n🔍 查询股票 {stock_code}:")
        
        if API_AVAILABLE:
            # 使用新API
            stock_info = get_stock_info(stock_code)
            
            if 'error' in stock_info:
                print(f"  ❌ {stock_info['error']}")
                if 'suggestion' in stock_info:
                    print(f"  💡 {stock_info['suggestion']}")
            else:
                print(f"  ✅ 代码: {stock_info.get('code')}")
                print(f"  📝 名称: {stock_info.get('name')}")
                print(f"  🏢 市场: {stock_info.get('market')}")
                print(f"  📊 类别: {stock_info.get('category')}")
                print(f"  🔗 数据源: {stock_info.get('source')}")
                print(f"  🕒 更新时间: {stock_info.get('updated_at', 'N/A')[:19]}")
        else:
            # 使用传统方式
            print(f"  ⚠️ 使用传统查询方式")
            db_manager = get_database_manager()
            if db_manager.is_mongodb_available():
                try:
                    collection = db_manager.mongodb_db['stock_basic_info']
                    stock = collection.find_one({"code": stock_code})
                    if stock:
                        print(f"  ✅ 找到: {stock.get('name')}")
                    else:
                        print(f"  ❌ 未找到股票信息")
                except Exception as e:
                    print(f"  ❌ 查询失败: {e}")
            else:
                print(f"  ❌ 数据库连接失败")

def demo_stock_search():
    """
    演示股票搜索功能
    """
    print("\n=== 股票搜索示例 ===")
    
    if not API_AVAILABLE:
        print("❌ 新API不可用，跳过搜索演示")
        return
    
    keywords = ['平安', '银行', '科技', '000001']
    
    for keyword in keywords:
        print(f"\n🔍 搜索关键词: '{keyword}'")
        
        results = search_stocks(keyword)
        
        if not results or (len(results) == 1 and 'error' in results[0]):
            print(f"  ❌ 未找到匹配的股票")
            if results and 'error' in results[0]:
                print(f"  💡 {results[0].get('suggestion', '')}")
        else:
            print(f"  ✅ 找到 {len(results)} 只匹配的股票:")
            for i, stock in enumerate(results[:5], 1):  # 只显示前5个
                if 'error' not in stock:
                    print(f"    {i}. {stock.get('code'):6s} - {stock.get('name'):15s} [{stock.get('market')}]")

def demo_market_overview():
    """
    演示市场概览功能
    """
    print("\n=== 市场概览示例 ===")
    
    if not API_AVAILABLE:
        print("❌ 新API不可用，跳过市场概览")
        return
    
    summary = get_market_summary()
    
    if 'error' in summary:
        print(f"❌ {summary['error']}")
        if 'suggestion' in summary:
            print(f"💡 {summary['suggestion']}")
    else:
        print("📊 市场统计信息:")
        print(f"  📈 总股票数: {summary.get('total_count', 0):,}")
        print(f"  🏢 沪市股票: {summary.get('shanghai_count', 0):,}")
        print(f"  🏢 深市股票: {summary.get('shenzhen_count', 0):,}")
        print(f"  🔗 数据源: {summary.get('data_source', 'unknown')}")
        
        # 显示类别统计
        category_stats = summary.get('category_stats', {})
        if category_stats:
            print("\n📋 按类别统计:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count:,} 只")

def demo_stock_data_query():
    """
    演示股票历史数据查询（带降级机制）
    """
    print("\n=== 股票历史数据查询示例 ===")
    
    if not API_AVAILABLE:
        print("❌ 新API不可用，跳过历史数据查询")
        return
    
    stock_code = '000001'
    print(f"📊 获取股票 {stock_code} 的历史数据...")
    
    # 获取最近30天的数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    result = get_stock_data(stock_code, start_date, end_date)
    
    # 显示结果（截取前500个字符以避免输出过长）
    if len(result) > 500:
        print(f"📋 数据获取结果（前500字符）:")
        print(result[:500] + "...")
    else:
        print(f"📋 数据获取结果:")
        print(result)

def demo_fallback_mechanism():
    """
    演示降级机制
    """
    print("\n=== 降级机制演示 ===")
    
    if not API_AVAILABLE:
        print("❌ 新API不可用，无法演示降级机制")
        return
    
    print("🔄 降级机制说明:")
    print("  1. 优先从MongoDB获取数据")
    print("  2. MongoDB不可用时，降级到通达信API")
    print("  3. 通达信API不可用时，提供基础的降级数据")
    print("  4. 获取到的数据会自动缓存到MongoDB（如果可用）")
    
    # 测试一个可能不存在的股票代码
    test_code = '999999'
    print(f"\n🧪 测试不存在的股票代码 {test_code}:")
    
    result = get_stock_info(test_code)
    if 'error' in result:
        print(f"  ❌ 预期的错误: {result['error']}")
    else:
        print(f"  ✅ 意外获得数据: {result.get('name')}")



def main():
    """
    主函数
    """
    print("🚀 股票查询示例程序（增强版）")
    print("=" * 60)
    
    if API_AVAILABLE:
        print("✅ 使用新的股票数据API（支持降级机制）")
    else:
        print("⚠️ 新API不可用，使用传统查询方式")
    
    try:
        # 执行各种查询示例
        demo_service_status()
        demo_single_stock_query()
        demo_stock_search()
        demo_market_overview()
        demo_stock_data_query()
        demo_fallback_mechanism()
        
        print("\n" + "=" * 60)
        print("✅ 所有查询示例执行完成")
        print("\n💡 使用建议:")
        print("  1. 确保MongoDB已正确配置以获得最佳性能")
        print("  2. 网络连接正常时可以使用通达信API作为备选")
        print("  3. 定期运行数据同步脚本更新股票信息")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()