# GitHub Secrets 配置指南
# GitHub Secrets Setup Guide

## 🔐 配置GitHub Secrets

为了让GitHub Actions能够自动推送微信消息，您需要在GitHub仓库中配置以下Secrets：

### 📝 第一步：进入GitHub仓库设置

1. 打开您的GitHub仓库：`https://github.com/shenbin77/-.git`
2. 点击 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables**
4. 点击 **Actions**

### 🔑 第二步：添加以下Secrets

点击 **New repository secret** 按钮，依次添加：

#### 1. WECHAT_APP_ID
- **Name**: `WECHAT_APP_ID`
- **Secret**: `wxf030257b07285d5a`

#### 2. WECHAT_APP_SECRET  
- **Name**: `WECHAT_APP_SECRET`
- **Secret**: `31ceaff31dc2a2e13a215e1f1b948998`

#### 3. WECHAT_OPENID
- **Name**: `WECHAT_OPENID`
- **Secret**: `o3tOfvssF1ThFelhSLLX3P2Gfkvk`

### ⚙️ 第三步：启用GitHub Actions

1. 在仓库中点击 **Actions** 标签
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**
3. 确保Actions已启用

### 🕐 第四步：工作流时间安排

当前配置的自动运行时间：
- **早上推送**: 每天8:30 AM (北京时间)
- **晚上推送**: 每天6:30 PM (北京时间)

### 🧪 第五步：手动测试

1. 进入 **Actions** 标签
2. 选择 **每日股票分析推送** 工作流
3. 点击 **Run workflow** 按钮
4. 选择 `test` 类型
5. 点击 **Run workflow** 开始测试

### 📱 第六步：验证推送

运行后检查您的微信是否收到了股票分析报告。

## 🔧 故障排除

### 如果没有收到微信消息：

1. **检查Secrets配置**：确保所有三个Secrets都正确配置
2. **检查OpenID**：确保您的微信还关注着测试号
3. **检查48小时规则**：如果超过48小时没有与公众号互动，请发送一条消息
4. **查看Actions日志**：在GitHub Actions中查看详细的运行日志

### 如果Actions运行失败：

1. 检查仓库的Actions权限设置
2. 确保有足够的GitHub Actions使用额度
3. 查看具体的错误日志

## 📊 功能特性

✅ **自动化分析**：每天自动运行股票分析
✅ **微信推送**：分析结果自动推送到您的微信
✅ **报告存档**：分析报告自动保存到仓库
✅ **手动触发**：支持手动运行分析
✅ **多时段推送**：早晚两次推送

## 🚀 下一步

配置完成后，您的股票分析系统将：

1. **每天自动运行**股票分析
2. **自动推送结果**到您的微信
3. **保存分析报告**到GitHub仓库
4. **提供历史记录**供回顾

现在您拥有了一个完全自动化的AI股票分析+微信推送系统！🎉
