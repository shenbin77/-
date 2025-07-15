"""
分析表单组件
"""

import streamlit as st
import datetime

def render_analysis_form():
    """渲染股票分析表单"""
    
    st.subheader("📋 分析配置")
    
    # 创建表单
    with st.form("analysis_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # 市场选择
            market_type = st.selectbox(
                "选择市场 🌍",
                options=["美股", "A股"],
                index=1,
                help="选择要分析的股票市场"
            )

            # 根据市场类型显示不同的输入提示
            if market_type == "美股":
                stock_symbol = st.text_input(
                    "股票代码 📈",
                    value="AAPL",
                    placeholder="输入美股代码，如 AAPL, TSLA, MSFT",
                    help="输入要分析的美股代码"
                ).upper().strip()
            else:  # A股
                stock_symbol = st.text_input(
                    "股票代码 📈",
                    value="000001",
                    placeholder="输入A股代码，如 000001, 600519",
                    help="输入要分析的A股代码，如 000001(平安银行), 600519(贵州茅台)"
                ).strip()
            
            # 分析日期
            analysis_date = st.date_input(
                "分析日期 📅",
                value=datetime.date.today(),
                help="选择分析的基准日期"
            )
        
        with col2:
            # 研究深度
            research_depth = st.select_slider(
                "研究深度 🔍",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: {
                    1: "1级 - 快速分析",
                    2: "2级 - 基础分析",
                    3: "3级 - 标准分析",
                    4: "4级 - 深度分析",
                    5: "5级 - 全面分析"
                }[x],
                help="选择分析的深度级别，级别越高分析越详细但耗时更长"
            )
        
        # 分析师团队选择
        st.markdown("### 👥 选择分析师团队")
        
        col1, col2 = st.columns(2)
        
        with col1:
            market_analyst = st.checkbox(
                "📈 市场分析师",
                value=True,
                help="专注于技术面分析、价格趋势、技术指标"
            )
            
            social_analyst = st.checkbox(
                "💭 社交媒体分析师",
                value=False,
                help="分析社交媒体情绪、投资者情绪指标"
            )
        
        with col2:
            news_analyst = st.checkbox(
                "📰 新闻分析师",
                value=False,
                help="分析相关新闻事件、市场动态影响"
            )
            
            fundamentals_analyst = st.checkbox(
                "💰 基本面分析师",
                value=True,
                help="分析财务数据、公司基本面、估值水平"
            )
        
        # 收集选中的分析师
        selected_analysts = []
        if market_analyst:
            selected_analysts.append(("market", "市场分析师"))
        if social_analyst:
            selected_analysts.append(("social", "社交媒体分析师"))
        if news_analyst:
            selected_analysts.append(("news", "新闻分析师"))
        if fundamentals_analyst:
            selected_analysts.append(("fundamentals", "基本面分析师"))
        
        # 显示选择摘要
        if selected_analysts:
            st.success(f"已选择 {len(selected_analysts)} 个分析师: {', '.join([a[1] for a in selected_analysts])}")
        else:
            st.warning("请至少选择一个分析师")
        
        # 高级选项
        with st.expander("🔧 高级选项"):
            include_sentiment = st.checkbox(
                "包含情绪分析",
                value=True,
                help="是否包含市场情绪和投资者情绪分析"
            )
            
            include_risk_assessment = st.checkbox(
                "包含风险评估",
                value=True,
                help="是否包含详细的风险因素评估"
            )
            
            custom_prompt = st.text_area(
                "自定义分析要求",
                placeholder="输入特定的分析要求或关注点...",
                help="可以输入特定的分析要求，AI会在分析中重点关注"
            )

        # 提交按钮
        submitted = st.form_submit_button(
            "🚀 开始分析",
            type="primary",
            use_container_width=True
        )

    # 只有在提交时才返回数据
    if submitted:
        return {
            'submitted': True,
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'analysis_date': str(analysis_date),
            'analysts': [a[0] for a in selected_analysts],
            'research_depth': research_depth,
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }
    else:
        return {'submitted': False}
