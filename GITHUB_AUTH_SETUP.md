# 🔐 GitHub认证配置指南
# GitHub Authentication Setup Guide

## ❌ **当前问题**

推送到GitHub时出现 `401 (Unauthorized)` 错误，需要配置正确的认证。

---

## 🔑 **解决方案1：使用Personal Access Token（推荐）**

### **第一步：创建GitHub Token**

1. **登录GitHub** → 点击右上角头像 → **Settings**
2. 左侧菜单 → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. 点击 **Generate new token** → **Generate new token (classic)**
4. 配置Token：
   - **Note**: `Stock Analysis Auto Sync`
   - **Expiration**: `No expiration` 或选择合适期限
   - **Scopes**: 勾选以下权限：
     - ✅ `repo` (完整仓库访问权限)
     - ✅ `workflow` (GitHub Actions权限)

5. 点击 **Generate token**
6. **⚠️ 重要**: 立即复制Token，页面关闭后无法再查看

### **第二步：配置Git使用Token**

```bash
# 方法1：更新远程URL（推荐）
git remote set-url origin https://YOUR_TOKEN@github.com/shenbin77/-.git

# 方法2：使用Git凭据管理器
git config --global credential.helper manager-core
```

### **第三步：测试推送**

```bash
git push origin main
```

---

## 🔑 **解决方案2：使用SSH密钥**

### **第一步：生成SSH密钥**

```bash
# 生成新的SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 启动SSH代理
eval "$(ssh-agent -s)"

# 添加SSH密钥到代理
ssh-add ~/.ssh/id_ed25519
```

### **第二步：添加SSH密钥到GitHub**

1. 复制公钥内容：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

2. **GitHub** → **Settings** → **SSH and GPG keys** → **New SSH key**
3. 粘贴公钥内容并保存

### **第三步：更新远程URL**

```bash
git remote set-url origin git@github.com:shenbin77/-.git
```

---

## 🛠️ **快速修复脚本**

创建 `fix_github_auth.py`：

```python
#!/usr/bin/env python3
import subprocess
import getpass

def fix_github_auth():
    print("🔐 GitHub认证修复工具")
    print("=" * 30)
    
    # 获取Token
    token = getpass.getpass("请输入您的GitHub Personal Access Token: ")
    
    if not token:
        print("❌ Token不能为空")
        return
    
    try:
        # 更新远程URL
        new_url = f"https://{token}@github.com/shenbin77/-.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', new_url], check=True)
        
        print("✅ GitHub认证配置成功")
        
        # 测试推送
        print("🧪 测试推送...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 推送测试成功！")
        else:
            print(f"❌ 推送测试失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 配置失败: {e}")

if __name__ == "__main__":
    fix_github_auth()
```

---

## 🎯 **推荐配置流程**

### **立即执行：**

1. **创建GitHub Token**（按照上面步骤）
2. **配置Git认证**：
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/shenbin77/-.git
   ```
3. **测试推送**：
   ```bash
   git push origin main
   ```
4. **启动自动同步**：
   ```bash
   python simple_auto_sync.py
   ```

---

## 🔒 **安全注意事项**

1. **Token安全**：
   - 不要在代码中硬编码Token
   - 定期更新Token
   - 使用最小权限原则

2. **仓库安全**：
   - 不要提交敏感信息
   - 使用 `.gitignore` 忽略敏感文件

3. **访问控制**：
   - 定期检查Token使用情况
   - 及时撤销不需要的Token

---

## 🧪 **测试自动同步**

配置完认证后：

1. **运行简化版自动同步**：
   ```bash
   python simple_auto_sync.py
   ```

2. **修改任意文件**测试自动检测

3. **确认自动提交**功能正常

4. **手动推送**验证认证配置

---

## 🎉 **完成后您将拥有：**

✅ **正确的GitHub认证配置**
✅ **自动检测代码变化**
✅ **自动提交到本地仓库**
✅ **手动推送到GitHub**（避免认证问题）

**配置完成后，您的代码修改将自动提交，只需要定期手动推送即可！** 🚀
