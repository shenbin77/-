# 🔄 上游同步指南

## 快速开始

### 1. 一键同步（推荐）

```bash
# 自动检查并同步上游更新
python scripts/sync_upstream.py

# 自动模式（不询问确认）
python scripts/sync_upstream.py --auto

# 使用rebase策略
python scripts/sync_upstream.py --strategy rebase
```

### 2. 手动同步

```bash
# 1. 添加上游仓库（首次运行）
git remote add upstream https://github.com/TauricResearch/TradingAgents.git

# 2. 获取上游更新
git fetch upstream

# 3. 检查新提交
git log --oneline HEAD..upstream/main

# 4. 创建同步分支
git checkout -b sync-$(date +%Y%m%d)

# 5. 合并上游更新
git merge upstream/main

# 6. 解决冲突（如果有）
# 编辑冲突文件，然后：
git add .
git commit

# 7. 切换回主分支并合并
git checkout main
git merge sync-$(date +%Y%m%d)

# 8. 推送更新
git push origin main
```

## 🚨 常见情况处理

### 情况1: 文档冲突
```bash
# 保持我们的中文文档
git checkout --ours README.md docs/
git add README.md docs/
git commit -m "保持中文文档版本"
```

### 情况2: 配置文件冲突
```bash
# 手动合并配置文件
git mergetool config/default.yaml
# 或者手动编辑后：
git add config/default.yaml
git commit -m "合并配置文件更新"
```

### 情况3: 核心代码冲突
```bash
# 优先采用上游版本
git checkout --theirs tradingagents/
git add tradingagents/
git commit -m "采用上游核心代码更新"
```

## 📋 同步检查清单

### 同步前
- [ ] 当前工作已保存并提交
- [ ] 没有正在进行的功能开发
- [ ] 创建备份标签：`git tag backup-$(date +%Y%m%d)`

### 同步中
- [ ] 检查上游更新内容
- [ ] 正确处理合并冲突
- [ ] 保护中文文档和增强功能

### 同步后
- [ ] 运行测试：`python -m pytest tests/`
- [ ] 验证基本功能：`python examples/basic_example.py`
- [ ] 检查文档完整性
- [ ] 推送到远程仓库

## 🔧 工具和脚本

### 自动化脚本
- `scripts/sync_upstream.py` - 主要同步脚本
- `sync_config.yaml` - 同步配置文件
- `.github/workflows/upstream-sync-check.yml` - GitHub Actions工作流

### 配置文件
- `sync_config.yaml` - 详细的同步策略配置
- 可以自定义冲突处理、文件保护等规则

## 📞 获取帮助

### 文档资源
- [详细同步策略](docs/maintenance/upstream-sync.md)
- [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)

### 联系方式
- 邮箱: hsliup@163.com
- GitHub: [@hsliuping](https://github.com/hsliuping)

## ⚠️ 注意事项

1. **备份重要**: 同步前务必备份当前状态
2. **测试充分**: 同步后要进行完整测试
3. **文档保护**: 保持我们的中文文档体系
4. **冲突谨慎**: 仔细处理每个合并冲突
5. **社区友好**: 考虑向上游贡献有价值的改进

---

通过这套完整的同步体系，我们可以轻松保持与原项目的技术同步！🚀
