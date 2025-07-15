# 微信公众号配置
# WeChat Official Account Configuration

# 测试号信息 (Test Account Information)
WECHAT_APP_ID = "wxf030257b07285d5a"
WECHAT_APP_SECRET = "31ceaff31dc2a2e13a215e1f1b948998"

# 消息模板配置 (Message Template Configuration)
# 这些需要在微信测试号后台配置后填入
TEMPLATE_ID_DAILY_REPORT = ""  # 日报模板ID
TEMPLATE_ID_STOCK_ALERT = ""   # 股票提醒模板ID

# 用户OpenID列表 (User OpenID List)
# 关注测试号后会自动获取
SUBSCRIBER_OPENIDS = ["o3tOfvssF1ThFelhSLLX3P2Gfkvk"]

print("微信配置已创建！")
print("WeChat configuration created!")
print(f"App ID: {WECHAT_APP_ID}")
print("请扫描测试号二维码关注，然后我们继续配置...")
print("Please scan the QR code to follow the test account, then we'll continue configuration...")
