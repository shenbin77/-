"""
微信公众号推送脚本
将每日分析报告推送到微信公众号
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional
import requests

# 微信公众号配置
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')

# API URLs
TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
PUBLISH_URL = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"

class WeChatPublisher:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        try:
            params = {
                'grant_type': 'client_credential',
                'appid': self.app_id,
                'secret': self.app_secret
            }
            
            response = requests.get(TOKEN_URL, params=params)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                print(f"✅ 获取访问令牌成功，有效期: {result.get('expires_in', 0)}秒")
                return self.access_token
            else:
                print(f"❌ 获取访问令牌失败: {result}")
                return None
                
        except Exception as e:
            print(f"❌ 获取访问令牌异常: {e}")
            return None
    
    def markdown_to_wechat_html(self, markdown_content: str) -> str:
        """将Markdown转换为微信公众号支持的HTML格式"""
        
        # 基础HTML模板
        html_template = """
        <section style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
        {content}
        </section>
        """
        
        # 转换规则
        content = markdown_content
        
        # 标题转换
        content = re.sub(r'^# (.+)$', r'<h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin: 20px 0;">\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2 style="color: #34495e; margin: 18px 0 12px 0; font-size: 1.3em;">\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3 style="color: #2c3e50; margin: 15px 0 10px 0; font-size: 1.1em;">\1</h3>', content, flags=re.MULTILINE)
        
        # 粗体转换
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #2c3e50;">\1</strong>', content)
        
        # 列表转换
        content = re.sub(r'^- (.+)$', r'<li style="margin: 5px 0;">\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li.*?</li>\s*)+', r'<ul style="margin: 10px 0; padding-left: 20px;">\g<0></ul>', content)
        
        # 分割线转换
        content = re.sub(r'^---$', r'<hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">', content, flags=re.MULTILINE)
        
        # 段落转换
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p style="margin: 12px 0; text-align: justify;">{para}</p>'
            formatted_paragraphs.append(para)
        
        content = '\n\n'.join(formatted_paragraphs)
        
        # 特殊样式
        content = re.sub(r'🟢', '<span style="color: #27ae60;">🟢</span>', content)
        content = re.sub(r'🟡', '<span style="color: #f39c12;">🟡</span>', content)
        content = re.sub(r'🔴', '<span style="color: #e74c3c;">🔴</span>', content)
        content = re.sub(r'📊', '<span style="color: #3498db;">📊</span>', content)
        content = re.sub(r'🤖', '<span style="color: #9b59b6;">🤖</span>', content)
        
        return html_template.format(content=content)
    
    def create_draft(self, title: str, content: str, author: str = "AI量化分析") -> Optional[str]:
        """创建草稿"""
        try:
            if not self.access_token:
                print("❌ 访问令牌无效")
                return None
            
            # 转换内容格式
            html_content = self.markdown_to_wechat_html(content)
            
            # 构建请求数据
            articles = [{
                "title": title,
                "author": author,
                "digest": self.extract_digest(content),
                "content": html_content,
                "content_source_url": "",
                "thumb_media_id": "",  # 如果有封面图片，需要先上传获取media_id
                "show_cover_pic": 0,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
            
            data = {"articles": articles}
            
            # 发送请求
            url = f"{DRAFT_URL}?access_token={self.access_token}"
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('errcode') == 0:
                media_id = result.get('media_id')
                print(f"✅ 草稿创建成功，media_id: {media_id}")
                return media_id
            else:
                print(f"❌ 草稿创建失败: {result}")
                return None
                
        except Exception as e:
            print(f"❌ 创建草稿异常: {e}")
            return None
    
    def extract_digest(self, content: str, max_length: int = 120) -> str:
        """提取文章摘要"""
        # 移除Markdown标记
        digest = re.sub(r'[#*\-`]', '', content)
        # 移除多余空白
        digest = re.sub(r'\s+', ' ', digest).strip()
        # 截取前120个字符
        if len(digest) > max_length:
            digest = digest[:max_length] + "..."
        return digest
    
    def publish_draft(self, media_id: str) -> bool:
        """发布草稿"""
        try:
            if not self.access_token:
                print("❌ 访问令牌无效")
                return False
            
            data = {"media_id": media_id}
            url = f"{PUBLISH_URL}?access_token={self.access_token}"
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('errcode') == 0:
                publish_id = result.get('publish_id')
                print(f"✅ 文章发布成功，publish_id: {publish_id}")
                return True
            else:
                print(f"❌ 文章发布失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 发布文章异常: {e}")
            return False

def load_latest_report() -> tuple[str, str]:
    """加载最新的分析报告"""
    try:
        reports_dir = "reports"
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = f"daily_report_{today}.md"
        report_path = os.path.join(reports_dir, report_file)
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else f"AI量化分析日报 - {today}"
            
            print(f"✅ 加载报告成功: {report_path}")
            return title, content
        else:
            print(f"❌ 报告文件不存在: {report_path}")
            return None, None
            
    except Exception as e:
        print(f"❌ 加载报告失败: {e}")
        return None, None

def main():
    """主函数"""
    print("📱 开始推送到微信公众号...")
    
    # 检查配置
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        print("❌ 微信公众号配置不完整，请设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        return False
    
    # 加载报告
    print("📖 加载最新分析报告...")
    title, content = load_latest_report()
    if not title or not content:
        print("❌ 无法加载报告内容")
        return False
    
    # 初始化发布器
    publisher = WeChatPublisher(WECHAT_APP_ID, WECHAT_APP_SECRET)
    
    # 获取访问令牌
    print("🔑 获取访问令牌...")
    if not publisher.get_access_token():
        print("❌ 无法获取访问令牌")
        return False
    
    # 创建草稿
    print("📝 创建文章草稿...")
    media_id = publisher.create_draft(title, content)
    if not media_id:
        print("❌ 无法创建草稿")
        return False
    
    # 发布文章（可选，也可以只创建草稿让人工审核后发布）
    auto_publish = os.getenv('WECHAT_AUTO_PUBLISH', 'false').lower() == 'true'
    
    if auto_publish:
        print("🚀 自动发布文章...")
        if publisher.publish_draft(media_id):
            print("✅ 文章已自动发布")
        else:
            print("❌ 自动发布失败，请手动发布")
            return False
    else:
        print("📋 草稿已创建，请登录公众号后台手动发布")
    
    print("🎉 微信公众号推送完成！")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
