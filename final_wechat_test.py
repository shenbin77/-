#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终微信公众号测试
Final WeChat Official Account Test
"""

import time
from datetime import datetime
from template_wechat_sender import TemplateWeChatSender

class FinalWeChatTest:
    """最终微信测试类"""
    
    def __init__(self):
        self.sender = TemplateWeChatSender()
        
        # 测试股票数据
        self.test_stocks = [
            {
                'name': '平安银行',
                'symbol': '000001.SZ',
                'score': 85.2,
                'reason': '技术面强势，短期均线向上排列，成交量放大'
            },
            {
                'name': '万科A',
                'symbol': '000002.SZ',
                'score': 78.9,
                'reason': '基本面稳健，估值合理，行业前景稳定'
            },
            {
                'name': '招商银行',
                'symbol': '600036.SH',
                'score': 76.5,
                'reason': '银行业龙头，ROE稳定，分红收益率高'
            },
            {
                'name': '贵州茅台',
                'symbol': '600519.SH',
                'score': 74.3,
                'reason': '消费升级受益，品牌价值突出，长期投资价值高'
            },
            {
                'name': '宁德时代',
                'symbol': '300750.SZ',
                'score': 72.1,
                'reason': '新能源汽车产业链核心，技术领先，市场份额稳定'
            }
        ]
        
        print("🎯 最终微信公众号测试系统初始化完成")
    
    def test_basic_functionality(self):
        """测试基本功能"""
        print("\n🔧 测试基本功能...")
        
        # 1. 测试access_token获取
        print("1️⃣ 测试access_token获取...")
        token = self.sender.get_access_token()
        if token:
            print(f"✅ access_token获取成功: {token[:20]}...")
        else:
            print("❌ access_token获取失败")
            return False
        
        # 2. 检查模板状态
        print("\n2️⃣ 检查模板状态...")
        template_status = self.sender.check_template_status()
        if "error" not in template_status:
            template_count = template_status.get("count", 0)
            print(f"✅ 模板检查成功，找到 {template_count} 个模板")
        else:
            print(f"⚠️ 模板检查异常: {template_status.get('error', '未知错误')}")
        
        return True
    
    def test_message_sending(self):
        """测试消息发送"""
        print("\n📤 测试消息发送...")
        
        # 发送测试消息
        print("🧪 发送测试消息...")
        test_success = self.sender.send_test_message()
        
        if test_success:
            print("✅ 测试消息发送成功！")
            return True
        else:
            print("❌ 测试消息发送失败")
            print("💡 可能原因:")
            print("   - API调用频率限制")
            print("   - 用户未关注公众号")
            print("   - 网络连接问题")
            return False
    
    def test_stock_report(self):
        """测试股票报告发送"""
        print("\n📊 测试股票报告发送...")
        
        # 发送股票报告
        report_success = self.sender.send_stock_report_text(self.test_stocks)
        
        if report_success:
            print("✅ 股票报告发送成功！")
            print("📱 请检查您的微信是否收到了股票分析报告")
            return True
        else:
            print("❌ 股票报告发送失败")
            return False
    
    def comprehensive_test(self):
        """综合测试"""
        print("🚀 开始综合测试...")
        print("=" * 60)
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 测试结果记录
        results = {
            "basic_functionality": False,
            "message_sending": False,
            "stock_report": False
        }
        
        # 1. 基本功能测试
        results["basic_functionality"] = self.test_basic_functionality()
        
        if not results["basic_functionality"]:
            print("\n❌ 基本功能测试失败，终止测试")
            return results
        
        # 等待一段时间，避免API频率限制
        print("\n⏳ 等待5秒，避免API频率限制...")
        time.sleep(5)
        
        # 2. 消息发送测试
        results["message_sending"] = self.test_message_sending()
        
        if results["message_sending"]:
            # 等待更长时间，避免频率限制
            print("\n⏳ 等待30秒，避免API频率限制...")
            time.sleep(30)
            
            # 3. 股票报告测试
            results["stock_report"] = self.test_stock_report()
        else:
            print("\n⚠️ 消息发送测试失败，跳过股票报告测试")
        
        # 生成测试报告
        self.generate_test_report(results)
        
        return results
    
    def generate_test_report(self, results):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        # 测试结果统计
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📋 测试项目: {total_tests}")
        print(f"✅ 通过项目: {passed_tests}")
        print(f"❌ 失败项目: {total_tests - passed_tests}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        print("\n📝 详细结果:")
        test_names = {
            "basic_functionality": "基本功能测试",
            "message_sending": "消息发送测试",
            "stock_report": "股票报告测试"
        }
        
        for key, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_names[key]}: {status}")
        
        # 总体评估
        print(f"\n🎯 总体评估:")
        if success_rate == 100:
            print("🎉 所有测试通过！微信公众号功能完全正常！")
            print("📱 您可以正常使用股票分析报告推送功能")
        elif success_rate >= 66:
            print("✅ 大部分测试通过，微信公众号基本功能正常")
            print("⚠️ 部分功能可能受到API限制影响")
        elif success_rate >= 33:
            print("⚠️ 部分测试通过，微信公众号功能受限")
            print("💡 建议检查配置或等待API限制解除")
        else:
            print("❌ 大部分测试失败，微信公众号功能异常")
            print("🔧 建议检查配置和网络连接")
        
        # 建议和下一步
        print(f"\n💡 建议和下一步:")
        
        if not results["basic_functionality"]:
            print("   1. 检查微信公众号配置（AppID、AppSecret）")
            print("   2. 确认网络连接正常")
        
        if not results["message_sending"]:
            print("   1. 等待24小时后重试（API频率限制）")
            print("   2. 确认用户已关注公众号")
            print("   3. 检查OpenID是否正确")
        
        if results["basic_functionality"] and results["message_sending"]:
            print("   1. 微信推送功能正常，可以部署到生产环境")
            print("   2. 可以设置定时任务，每日自动推送股票报告")
            print("   3. 考虑添加更多交互功能")
        
        print(f"\n⏰ 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def quick_test(self):
        """快速测试（仅测试基本功能）"""
        print("⚡ 快速测试模式...")
        
        # 只测试基本功能
        basic_ok = self.test_basic_functionality()
        
        if basic_ok:
            print("\n✅ 快速测试通过！微信API基本功能正常")
            print("💡 如需完整测试，请运行 comprehensive_test()")
        else:
            print("\n❌ 快速测试失败！请检查配置")
        
        return basic_ok

def main():
    """主函数"""
    print("🎯 最终微信公众号测试")
    print("=" * 40)
    
    tester = FinalWeChatTest()
    
    # 询问测试模式
    print("\n📋 测试模式选择:")
    print("1. 快速测试（仅基本功能）")
    print("2. 综合测试（包含消息发送）")
    
    try:
        choice = input("\n请选择测试模式 (1/2): ").strip()
        
        if choice == "1":
            tester.quick_test()
        elif choice == "2":
            tester.comprehensive_test()
        else:
            print("❓ 无效选择，执行快速测试...")
            tester.quick_test()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，测试结束")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")

if __name__ == "__main__":
    main()
