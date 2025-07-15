# 🌿 分支管理快速指南

## 🚀 快速开始

### 常用命令

```bash
# 查看所有分支
python scripts/branch_manager.py list

# 创建功能分支
python scripts/branch_manager.py create feature 分支名称 -d "功能描述"

# 创建中文增强分支
python scripts/branch_manager.py create enhancement 分支名称 -d "增强描述"

# 切换分支
python scripts/branch_manager.py switch 分支名称

# 删除分支
python scripts/branch_manager.py delete 分支名称

# 清理已合并分支
python scripts/branch_manager.py cleanup
```

## 🏗️ 分支架构

```
main (生产分支) ← 稳定版本，受保护
├── develop (开发主分支) ← 集成所有开发
├── feature/* (功能开发) ← 新功能开发
├── enhancement/* (中文增强) ← 本地化功能
├── hotfix/* (紧急修复) ← Bug修复
└── release/* (发布准备) ← 版本发布
```

## 📋 推荐开发工作流

### 1. 功能开发流程 ⭐

#### 完整开发周期
```bash
# 第1步: 准备工作
git checkout develop
git pull origin develop

# 第2步: 创建功能分支
python scripts/branch_manager.py create feature portfolio-optimization -d "投资组合优化功能"

# 第3步: 开发功能
# 编写核心代码
git add tradingagents/portfolio/optimizer.py
git commit -m "feat: 添加投资组合优化算法"

# 编写测试用例
git add tests/test_portfolio_optimizer.py
git commit -m "test: 添加投资组合优化测试"

# 更新文档
git add docs/features/portfolio-optimization.md
git commit -m "docs: 添加投资组合优化文档"

# 第4步: 定期同步develop
git fetch origin
git merge origin/develop  # 保持与主线同步

# 第5步: 推送到远程
git push origin feature/portfolio-optimization

# 第6步: 创建Pull Request
# 在GitHub上创建PR: feature/portfolio-optimization -> develop
# 使用PR模板，详细描述功能和测试情况

# 第7步: 代码审查和修改
# 根据审查意见修改代码，推送更新

# 第8步: 合并和清理
# PR合并后，清理本地分支
python scripts/branch_manager.py delete feature/portfolio-optimization
```

#### 功能开发检查清单 ✅
- [ ] 功能需求明确，有设计文档
- [ ] 编写了完整的单元测试
- [ ] 代码通过了所有自动化测试
- [ ] 更新了相关文档和示例
- [ ] 进行了代码审查
- [ ] 测试了向后兼容性

### 2. 中文增强流程 🇨🇳

#### 本地化开发周期
```bash
# 第1步: 创建增强分支
python scripts/branch_manager.py create enhancement tushare-integration -d "集成Tushare A股数据源"

# 第2步: 开发中文功能
# 添加数据源适配器
git add tradingagents/data/tushare_source.py
git commit -m "enhance(data): 添加Tushare数据源适配器"

# 添加中文配置
git add config/chinese_markets.yaml
git commit -m "enhance(config): 添加A股市场配置"

# 第3步: 更新中文文档
git add docs/data/tushare-integration.md
git commit -m "docs: 添加Tushare集成使用指南"

# 第4步: 中文功能测试
python -m pytest tests/test_tushare_integration.py
git add tests/test_tushare_integration.py
git commit -m "test: 添加Tushare集成测试用例"

# 第5步: 推送和合并
git push origin enhancement/tushare-integration
# 创建PR到develop分支
```

#### 中文增强检查清单 ✅
- [ ] 适配中国金融市场特点
- [ ] 添加完整的中文文档
- [ ] 支持中文金融术语
- [ ] 兼容现有国际化功能
- [ ] 测试中文数据处理

### 3. 紧急修复流程 🚨

#### 生产Bug快速修复
```bash
# 第1步: 从main创建修复分支
git checkout main
git pull origin main
python scripts/branch_manager.py create hotfix api-timeout-fix -d "修复API请求超时问题"

# 第2步: 快速定位和修复
# 分析问题，实施最小化修复
git add tradingagents/api/client.py
git commit -m "fix: 增加API请求超时重试机制"

# 第3步: 紧急测试
python -m pytest tests/test_api_client.py -v
# 手动测试关键功能

# 第4步: 立即部署
git push origin hotfix/api-timeout-fix
# 创建紧急PR到main

# 第5步: 同步到develop
git checkout develop
git merge main
git push origin develop
```

### 4. 版本发布流程 📦

#### 正式版本发布
```bash
# 第1步: 创建发布分支
python scripts/branch_manager.py create release v1.1.0-cn -d "v1.1.0中文增强版"

# 第2步: 版本准备
# 更新版本号
echo "1.1.0-cn" > VERSION
git add VERSION
git commit -m "bump: 版本更新到v1.1.0-cn"

# 更新变更日志
git add CHANGELOG.md
git commit -m "docs: 更新v1.1.0-cn变更日志"

# 第3步: 最终测试
python -m pytest tests/ --cov=tradingagents
python examples/full_integration_test.py

# 第4步: 合并到main
git checkout main
git merge release/v1.1.0-cn
git tag v1.1.0-cn
git push origin main --tags

# 第5步: 同步到develop
git checkout develop
git merge main
git push origin develop
```

### 5. 上游同步流程 🔄

#### 与原项目保持同步
```bash
# 第1步: 检查上游更新
python scripts/sync_upstream.py

# 第2步: 处理同步结果
# 如果有更新，脚本会创建 upstream-sync/日期 分支
# 自动处理冲突，保护中文文档和增强功能

# 第3步: 验证同步结果
python -m pytest tests/
python examples/basic_example.py

# 第4步: 合并到主分支
git checkout main
git merge upstream-sync/20240115
git push origin main

# 第5步: 同步到develop
git checkout develop
git merge main
git push origin develop
```

## 🎯 分支命名规范

### 功能分支 (feature/)
```bash
feature/portfolio-analysis      # 投资组合分析
feature/risk-management        # 风险管理
feature/backtesting-engine     # 回测引擎
feature/real-time-data         # 实时数据
```

### 中文增强分支 (enhancement/)
```bash
enhancement/baidu-llm          # 百度LLM集成
enhancement/tushare-data       # Tushare数据源
enhancement/chinese-terms      # 中文金融术语
enhancement/akshare-api        # AkShare API集成
```

### 修复分支 (hotfix/)
```bash
hotfix/memory-leak             # 内存泄漏修复
hotfix/config-error            # 配置错误修复
hotfix/api-rate-limit          # API限流修复
```

### 发布分支 (release/)
```bash
release/v1.1.0-cn             # 版本发布准备
release/v1.2.0-cn-beta        # Beta版本
```

## 🔧 实用技巧

### 查看分支状态
```bash
# 查看当前分支
git branch --show-current

# 查看所有分支
git branch -a

# 查看分支关系
git log --graph --oneline --all

# 查看未合并分支
git branch --no-merged develop
```

### 分支同步
```bash
# 同步develop分支
git checkout develop
git pull origin develop

# 将develop合并到功能分支
git checkout feature/your-feature
git merge develop

# 或者使用rebase
git rebase develop
```

### 分支清理
```bash
# 删除本地已合并分支
git branch --merged develop | grep -v "develop\|main" | xargs -n 1 git branch -d

# 删除远程跟踪分支
git remote prune origin

# 使用我们的工具清理
python scripts/branch_manager.py cleanup
```

## 📊 分支保护规则

### main分支
- ✅ 要求PR审查
- ✅ 要求CI通过
- ✅ 禁止直接推送
- ✅ 禁止强制推送

### develop分支
- ✅ 要求PR审查
- ✅ 要求CI通过
- ✅ 允许管理员绕过

### 功能分支
- ❌ 无特殊限制
- ✅ 自动删除已合并分支

## 🚨 注意事项

### 开发建议
1. **小而频繁的提交** - 每个提交解决一个问题
2. **描述性分支名** - 清楚表达分支用途
3. **及时同步** - 定期从develop拉取更新
4. **完整测试** - 合并前确保测试通过
5. **文档同步** - 功能开发同时更新文档

### 避免的操作
1. **直接推送到main** - 始终通过PR
2. **长期分支** - 功能分支应该短期完成
3. **大型合并** - 避免一次性合并大量更改
4. **跳过测试** - 合并前必须通过所有测试
5. **忽略冲突** - 仔细解决每个合并冲突

## 🔗 相关资源

- **详细策略**: [docs/development/branch-strategy.md](docs/development/branch-strategy.md)
- **分支管理工具**: [scripts/branch_manager.py](scripts/branch_manager.py)
- **GitHub工作流**: [.github/workflows/](/.github/workflows/)

## 📞 获取帮助

```bash
# 查看工具帮助
python scripts/branch_manager.py --help

# 查看特定命令帮助
python scripts/branch_manager.py create --help
```

### 联系方式
- **GitHub Issues**: [提交问题](https://github.com/hsliuping/TradingAgents-CN/issues)
- **邮箱**: hsliup@163.com

---

通过这套分支管理体系，您可以高效地进行功能开发和项目维护！🚀
