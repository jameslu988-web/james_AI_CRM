import streamlit as st
import pandas as pd

from .database import get_session, Customer, EmailHistory, Order
from src.email_system.ai_writer import AIEmailWriter


class CRMDashboard:
    def __init__(self):
        self.session = get_session()

    def render(self):
        st.set_page_config(
            page_title="外贸CRM系统",
            layout="wide",
            page_icon="🩲",
        )
        st.markdown(
            """
            <style>
            .hero{padding:12px 18px;border-radius:12px;background:linear-gradient(90deg,#0ea5e9,#22c55e);color:#fff;margin-bottom:16px;}
            .cards{display:flex;gap:12px;margin-bottom:16px;}
            .card{flex:1;background:#ffffff;border-radius:12px;padding:16px;border:1px solid #eee;box-shadow:0 1px 8px rgba(0,0,0,.06);}
            .card .label{font-size:12px;color:#666;margin-bottom:6px;}
            .card .value{font-size:24px;font-weight:700;}
            .section-title{font-weight:600;margin-top:12px;margin-bottom:8px;}
            .stButton>button{border-radius:8px;padding:8px 14px;}
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
            [data-testid="stSidebar"]{background:#f7f9fc;border-right:1px solid #eee;}
            [data-testid="stSidebar"] .stButton>button{border-radius:10px;margin-bottom:8px;height:40px;font-weight:600;}
            [data-testid="stSidebar"] .stButton>button:hover{filter:brightness(0.98);}            
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.sidebar:
            st.markdown(
                """
                <div style="padding:12px 8px 4px 8px;">
                    <div style="font-weight:700;font-size:16px;margin-bottom:8px;">导航</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # 初始化导航状态（使用固定 key，不受语言影响）
            if "nav_page" not in st.session_state:
                st.session_state["nav_page"] = "dashboard"

            def nav_button(label, page_key):
                active = st.session_state["nav_page"] == page_key
                clicked = st.button(
                    label,
                    use_container_width=True,
                    type="primary" if active else "secondary",
                    key=f"nav_{page_key}",
                )
                if clicked:
                    st.session_state["nav_page"] = page_key
                    st.rerun()

            lang = st.session_state.get("lang", "中文")
            lbl_dashboard = "📊 仪表盘" if lang == "中文" else "📊 Dashboard"
            lbl_customers = "👥 客户管理" if lang == "中文" else "👥 Customers"
            lbl_emails = "📧 邮件营销" if lang == "中文" else "📧 Email"
            lbl_orders = "📦 订单管理" if lang == "中文" else "📦 Orders"
            lbl_settings = "⚙️ 自动化设置" if lang == "中文" else "⚙️ Settings"

            nav_button(lbl_dashboard, "dashboard")
            nav_button(lbl_customers, "customers")
            nav_button(lbl_emails, "emails")
            nav_button(lbl_orders, "orders")
            nav_button(lbl_settings, "settings")

            page = st.session_state["nav_page"]

        if page == "dashboard":
            self.render_dashboard()
        elif page == "customers":
            self.render_customers()
        elif page == "emails":
            self.render_email_campaigns()
        elif page == "orders":
            self.render_orders()
        elif page == "settings":
            self.render_settings()

    def render_dashboard(self):
        # 顶部品牌横幅
        st.markdown(
            """
            <div class='hero'>
              <h2 style='margin:0;'>Underwear Export CRM</h2>
              <p style='margin:6px 0 0 0;'>助力海外客户开发 · 低MOQ · 高品质 · 快交期</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 统计数据
        total_customers = self.session.query(Customer).count()
        active_status = ["contacted", "replied", "qualified", "negotiating"]
        active_leads = sum(
            1 for c in self.session.query(Customer).all() if c.status in active_status
        )
        from datetime import datetime
        month_amount = 0
        try:
            from sqlalchemy import extract
            month_orders = (
                self.session.query(Order)
                .filter(extract('year', Order.order_date) == datetime.now().year)
                .filter(extract('month', Order.order_date) == datetime.now().month)
                .all()
            )
            month_amount = sum(float(o.total_amount or 0) for o in month_orders)
        except Exception:
            month_amount = 0

        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class='card'>
                  <div class='label'>总客户数</div>
                  <div class='value'>{total_customers}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class='card'>
                  <div class='label'>活跃线索</div>
                  <div class='value'>{active_leads}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class='card'>
                  <div class='label'>本月订单金额</div>
                  <div class='value'>${month_amount:.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            # 新增：本月订单数
            month_orders_count = len(month_orders) if 'month_orders' in locals() else 0
            st.markdown(
                f"""
                <div class='card'>
                  <div class='label'>本月订单数</div>
                  <div class='value'>{month_orders_count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 简易漏斗占位图（后续替换为真实数据）
        st.markdown("<div class='section-title'>销售漏斗（占位）</div>", unsafe_allow_html=True)
        import pandas as pd
        funnel = pd.DataFrame(
            {
                "阶段": ["Cold", "Contacted", "Replied", "Qualified", "Negotiating", "Customer"],
                "数量": [
                    sum(1 for c in self.session.query(Customer).all() if (c.status or "cold") == "cold"),
                    sum(1 for c in self.session.query(Customer).all() if c.status == "contacted"),
                    sum(1 for c in self.session.query(Customer).all() if c.status == "replied"),
                    sum(1 for c in self.session.query(Customer).all() if c.status == "qualified"),
                    sum(1 for c in self.session.query(Customer).all() if c.status == "negotiating"),
                    sum(1 for c in self.session.query(Customer).all() if c.status == "customer"),
                ],
            }
        )
        # 使用面积图替代柱状图
        st.area_chart(funnel.set_index("阶段"))

        # 需要关注的提醒区
        st.markdown("<div class='section-title'>需要关注</div>", unsafe_allow_html=True)
        # 今日需跟进客户（next_followup_date 到期或缺失且非 cold）
        from datetime import datetime, timedelta
        customers_all = self.session.query(Customer).all()
        need_follow = []
        now = datetime.now()
        for c in customers_all:
            if (c.status or 'cold') != 'cold':
                if c.next_followup_date is None or c.next_followup_date <= now:
                    need_follow.append({
                        '公司': c.company_name,
                        '联系人': c.contact_name or '-',
                        '邮箱': c.email or '-',
                        '状态': c.status or 'cold'
                    })
        import pandas as pd
        if need_follow:
            st.markdown("**今日需跟进客户**")
            st.dataframe(pd.DataFrame(need_follow), use_container_width=True)
        else:
            st.info("暂无需跟进客户")

        # 延期订单（estimated_completion_date 已过且未完成/未交付）
        delayed = []
        orders_all = self.session.query(Order).all()
        for o in orders_all:
            if o.estimated_completion_date and o.estimated_completion_date < (now - timedelta(days=int(st.session_state.get("settings", {}).get("delay_tolerance_days", 0)))):
                if o.status not in ['shipped', 'delivered', 'completed']:
                    delayed.append({
                        '订单': o.order_number,
                        '公司': next((c.company_name for c in customers_all if c.id == o.customer_id), '-'),
                        '状态': o.status,
                        '预计完成': o.estimated_completion_date.strftime('%Y-%m-%d')
                    })
        if delayed:
            st.markdown("**延期订单**")
            st.dataframe(pd.DataFrame(delayed), use_container_width=True)
        else:
            st.info("暂无延期订单")
        st.markdown("---")
        colj1, colj2 = st.columns(2)
        with colj1:
            if st.button("查看需跟进客户", type="primary"):
                st.session_state["nav_page"] = "👥 客户管理"
                st.session_state["show_need_follow_only"] = True
                st.rerun()
        with colj2:
            if st.button("查看延期订单", type="secondary"):
                st.session_state["nav_page"] = "📦 订单管理"
                st.rerun()

    def render_customers(self):
        st.subheader("👥 客户管理")
        
        # 批量导入客户（CSV）
        st.markdown("**批量导入客户（CSV）**")
        uploaded = st.file_uploader("上传CSV文件", type=["csv"], accept_multiple_files=False)
        if uploaded is not None:
            import pandas as pd
            try:
                df = pd.read_csv(uploaded)
                df.columns = [str(c).strip().lower() for c in df.columns]
                st.caption("预览前10条：")
                st.dataframe(df.head(10), use_container_width=True)
        
                if st.button("开始导入", type="primary"):
                    added = 0
                    for _, row in df.iterrows():
                        company_name = str(row.get("company_name") or "").strip()
                        if not company_name:
                            continue
                        try:
                            c = Customer(
                                company_name=company_name,
                                contact_name=(str(row.get("contact_name") or "").strip() or None),
                                email=(str(row.get("email") or "").strip() or None),
                                country=(str(row.get("country") or "").strip() or None),
                                status=(str(row.get("status") or "cold").strip() or "cold"),
                                source=(str(row.get("source") or "").strip() or None),
                                website=(str(row.get("website") or "").strip() or None),
                                industry=(str(row.get("industry") or "").strip() or None),
                                phone=(str(row.get("phone") or "").strip() or None),
                            )
                            self.session.add(c)
                            self.session.commit()
                            added += 1
                        except Exception:
                            self.session.rollback()
                            # 可能是重复邮箱等约束冲突，跳过
                            continue
                    st.success(f"导入完成，新增 {added} 条记录")
                    st.rerun()
            except Exception as e:
                st.error(f"读取CSV失败：{e}")

        # 新增客户表单（置顶，便于快速录入）
        with st.form("add_customer_form"):
            st.markdown("**新增客户**")
            cols = st.columns(3)
            with cols[0]:
                company_name = st.text_input("公司名称 *", "")
            with cols[1]:
                contact_name = st.text_input("联系人", "")
            with cols[2]:
                email = st.text_input("邮箱", "")
            cols2 = st.columns(3)
            with cols2[0]:
                country = st.selectbox(
                    "国家",
                    [
                        "",
                        "USA",
                        "UK",
                        "Germany",
                        "France",
                        "Italy",
                        "Spain",
                        "Netherlands",
                        "Canada",
                        "Australia",
                        "China",
                        "Singapore",
                        "UAE",
                    ],
                    index=0,
                )
            with cols2[1]:
                status = st.selectbox(
                    "状态",
                    [
                        "cold",
                        "contacted",
                        "replied",
                        "qualified",
                        "negotiating",
                        "customer",
                        "lost",
                    ],
                    index=0,
                )
            with cols2[2]:
                source = st.text_input("来源（如：Google/LinkedIn）", "")
            cols3 = st.columns(3)
            with cols3[0]:
                website = st.text_input("网站", "")
            with cols3[1]:
                industry = st.selectbox(
                    "行业",
                    [
                        "",
                        "Retail",
                        "E-commerce",
                        "Fashion",
                        "Fitness",
                        "Hotel",
                        "Subscription",
                    ],
                    index=0,
                )
            with cols3[2]:
                phone = st.text_input("电话", "")

            submitted = st.form_submit_button("保存客户")
            if submitted:
                if not company_name.strip():
                    st.error("公司名称为必填项")
                else:
                    try:
                        c = Customer(
                            company_name=company_name.strip(),
                            contact_name=contact_name.strip() or None,
                            email=email.strip() or None,
                            country=(country or None),
                            status=status,
                            source=source.strip() or None,
                            website=website.strip() or None,
                            industry=industry or None,
                            phone=phone.strip() or None,
                        )
                        self.session.add(c)
                        self.session.commit()
                        st.success("客户已保存")
                        st.rerun()
                    except Exception as e:
                        self.session.rollback()
                        st.error(f"保存失败：{e}")

        # 搜索与筛选
        st.markdown("---")
        
        # 批量操作
        st.markdown("**批量操作**")
        with st.expander("批量更新客户状态"):
            # 先获取所有客户用于批量选择
            all_customers_for_bulk = self.session.query(Customer).all()
            selected_ids = st.multiselect(
                "选择客户",
                options=[(c.id, f"{c.company_name} - {c.contact_name or 'N/A'}") for c in all_customers_for_bulk],
                format_func=lambda x: x[1],
                key="bulk_select_status"
            )
            new_status_bulk = st.selectbox(
                "批量状态",
                ["cold", "contacted", "replied", "qualified", "negotiating", "customer", "lost"],
                key="bulk_status"
            )
            if st.button("批量更新", type="primary", key="bulk_update_btn"):
                if selected_ids:
                    for cid, _ in selected_ids:
                        customer = self.session.query(Customer).filter_by(id=cid).first()
                        if customer:
                            customer.status = new_status_bulk
                    self.session.commit()
                    st.success(f"已更新 {len(selected_ids)} 个客户的状态为 {new_status_bulk}")
                    st.rerun()
                else:
                    st.warning("请先选择客户")
        
        with st.expander("批量删除客户"):
            del_ids = st.multiselect(
                "选择要删除的客户",
                options=[(c.id, f"{c.company_name} - {c.contact_name or 'N/A'}") for c in all_customers_for_bulk],
                format_func=lambda x: x[1],
                key="bulk_delete"
            )
            if st.button("⚠️ 确认删除", type="secondary", key="bulk_delete_btn"):
                if del_ids:
                    for cid, _ in del_ids:
                        customer = self.session.query(Customer).filter_by(id=cid).first()
                        if customer:
                            self.session.delete(customer)
                    self.session.commit()
                    st.success(f"已删除 {len(del_ids)} 个客户")
                    st.rerun()
                else:
                    st.warning("请先选择客户")
        
        st.markdown("---")
        col_s, col_f = st.columns([2, 1])
        with col_s:
            search = st.text_input("搜索（公司/联系人/邮箱/网站）", "")
        with col_f:
            status_filter = st.selectbox(
                "状态筛选",
                [
                    "全部",
                    "cold",
                    "contacted",
                    "replied",
                    "qualified",
                    "negotiating",
                    "customer",
                    "lost",
                ],
                index=0,
            )

        # 展示所选客户的邮件历史（可关闭）
        if st.session_state.get("show_history_customer_id"):
            cid = st.session_state["show_history_customer_id"]
            st.markdown("---")
            st.markdown("**客户邮件历史**")
            target = self.session.query(Customer).filter(Customer.id == cid).first()
            if target:
                st.write(f"客户：{target.company_name}（{target.contact_name or '-'} | {target.email or '-' }）")
                hist = (
                    self.session.query(EmailHistory)
                    .filter(EmailHistory.customer_id == cid)
                    .order_by(EmailHistory.id.desc())
                    .limit(200)
                    .all()
                )
                dir_filter = st.selectbox("方向过滤", ["全部", "outbound", "inbound"], index=0, key=f"dir_{cid}")
                q = st.text_input("搜索主题或正文", "", key=f"q_{cid}")
                filtered_hist = []
                for h in hist:
                    if dir_filter != "全部" and h.direction != dir_filter:
                        continue
                    if q and q.lower() not in (f"{h.subject or ''} {h.body or ''}".lower()):
                        continue
                    filtered_hist.append(h)
                if filtered_hist:
                    st.write(f"共 {len(filtered_hist)} 条记录")
                    for h in filtered_hist:
                        with st.expander(f"{h.direction} | {h.subject or '(无主题)'}"):
                            st.write(f"**方向**: {h.direction}")
                            st.write(f"**主题**: {h.subject or '-'}")
                            st.write(f"**正文**:")
                            st.text_area("", h.body or "(无正文)", height=150, key=f"body_cust_{h.id}")
                            st.write(f"**AI生成**: {'是' if h.ai_generated else '否'}")
                            # 附件下载
                            if h.attachments:
                                import json
                                try:
                                    attach_list = json.loads(h.attachments)
                                    st.write(f"**附件** ({len(attach_list)} 个):")
                                    for att in attach_list:
                                        import os
                                        if os.path.exists(att):
                                            filename = os.path.basename(att)
                                            col_preview, col_action = st.columns([3, 1])
                                            with col_preview:
                                                # 图片预览
                                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                                    st.image(att, caption=filename, width=300)
                                                # PDF预览
                                                elif filename.lower().endswith('.pdf'):
                                                    with open(att, "rb") as f:
                                                        pdf_bytes = f.read()
                                                        import base64
                                                        b64 = base64.b64encode(pdf_bytes).decode()
                                                        pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="400" type="application/pdf"></iframe>'
                                                        st.markdown(pdf_display, unsafe_allow_html=True)
                                                # Word预览
                                                elif filename.lower().endswith(('.doc', '.docx')):
                                                    try:
                                                        import mammoth
                                                        with open(att, "rb") as docx_file:
                                                            result = mammoth.convert_to_html(docx_file)
                                                            st.markdown(result.value, unsafe_allow_html=True)
                                                    except ImportError:
                                                        st.info("Word预览需安装 mammoth: pip install mammoth")
                                                    except Exception as e:
                                                        st.info(f"Word预览失败: {e}")
                                                # Excel预览
                                                elif filename.lower().endswith(('.xls', '.xlsx')):
                                                    try:
                                                        import pandas as pd
                                                        df = pd.read_excel(att)
                                                        st.dataframe(df, use_container_width=True)
                                                    except Exception as e:
                                                        st.info(f"Excel预览失败: {e}")
                                                else:
                                                    st.info(f"文件: {filename} (不支持预览)")
                                            with col_action:
                                                with open(att, "rb") as f:
                                                    st.download_button(f"⬇️ 下载", f, file_name=filename, key=f"dl_cust_{h.id}_{att}")
                                                if st.button(f"🗑️ 删除", key=f"del_cust_{h.id}_{att}"):
                                                    try:
                                                        attach_list.remove(att)
                                                        h.attachments = json.dumps(attach_list) if attach_list else None
                                                        self.session.commit()
                                                        if os.path.exists(att):
                                                            os.remove(att)
                                                        st.success("已删除附件")
                                                        st.rerun()
                                                    except Exception as e:
                                                        st.error(f"删除失败: {e}")
                                except Exception as e:
                                    st.info(f"附件解析失败: {e}")
                            else:
                                st.info("无附件")
                else:
                    st.info("暂无历史记录或无匹配结果")
            if st.button("关闭历史", key="close_history"):
                st.session_state.pop("show_history_customer_id", None)
                st.rerun()

        # 数据查询与展示（卡片 + 操作）
        customers = self.session.query(Customer).all()
        filtered = []
        for c in customers:
            text = " ".join(
                [
                    str(c.company_name or ""),
                    str(c.contact_name or ""),
                    str(c.email or ""),
                    str(c.website or ""),
                ]
            ).lower()
            if search and (search.lower() not in text):
                continue
            if status_filter != "全部" and (c.status or "cold") != status_filter:
                continue
            filtered.append(c)

        from datetime import datetime
        if st.session_state.get("show_need_follow_only"):
            filtered = [
                c for c in filtered
                if (c.status or 'cold') != 'cold' and (c.next_followup_date is None or c.next_followup_date <= datetime.now())
            ]
            st.info("筛选：需跟进客户（来自仪表盘快捷入口）")
            if st.button("清除筛选", key="clear_need_follow"):
                st.session_state.pop("show_need_follow_only", None)
                st.rerun()
        if not filtered:
            st.info("暂无符合条件的客户记录。可以使用上方表单新增客户。")
        else:
            # 导出当前列表为CSV
            import pandas as pd
            export_data = [
                {
                    "公司名称": c.company_name,
                    "联系人": c.contact_name,
                    "邮箱": c.email,
                    "国家": c.country,
                    "行业": c.industry,
                    "网站": c.website,
                    "状态": c.status,
                    "电话": c.phone,
                }
                for c in filtered
            ]
            export_df = pd.DataFrame(export_data)
            if not export_df.empty:
                csv = export_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "导出当前列表为CSV",
                    data=csv,
                    file_name="customers_export.csv",
                    mime="text/csv",
                )

            for c in filtered:
                with st.expander(f"{c.company_name} - {c.contact_name or '-'}"):
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.write(f"**邮箱**: {c.email or '-'}")
                        st.write(f"**电话**: {c.phone or '-'}")
                    with info_cols[1]:
                        st.write(f"**国家**: {c.country or '-'}")
                        st.write(f"**行业**: {c.industry or '-'}")
                    with info_cols[2]:
                        st.write(f"**网站**: {c.website or '-'}")
                        st.write(f"**状态**: {c.status or 'cold'}")

                    btn_cols = st.columns(4)
                    with btn_cols[0]:
                        if st.button("发送开发信", key=f"send_{c.id}"):
                            st.session_state["nav_page"] = "emails"
                            st.session_state["selected_customer_id"] = c.id
                            st.rerun()
                    with btn_cols[1]:
                        # 简易查看历史
                        if st.button("查看历史", key=f"history_{c.id}"):
                            st.session_state["show_history_customer_id"] = c.id
                            st.rerun()
                    with btn_cols[2]:
                        if st.button("编辑", key=f"edit_btn_{c.id}"):
                            st.session_state[f"edit_{c.id}"] = True
                    with btn_cols[3]:
                        if st.button("创建订单", key=f"order_{c.id}"):
                            st.session_state["nav_page"] = "📦 订单管理"
                            st.session_state["selected_customer_id"] = c.id
                            st.rerun()

                    # 编辑表单
                    if st.session_state.get(f"edit_{c.id}"):
                        with st.form(f"edit_form_{c.id}"):
                            e_cols = st.columns(3)
                            with e_cols[0]:
                                new_company = st.text_input("公司名称 *", value=c.company_name or "")
                            with e_cols[1]:
                                new_contact = st.text_input("联系人", value=c.contact_name or "")
                            with e_cols[2]:
                                new_email = st.text_input("邮箱", value=c.email or "")
                            e_cols2 = st.columns(3)
                            with e_cols2[0]:
                                new_country = st.selectbox(
                                    "国家",
                                    [
                                        "",
                                        "USA",
                                        "UK",
                                        "Germany",
                                        "France",
                                        "Italy",
                                        "Spain",
                                        "Netherlands",
                                        "Canada",
                                        "Australia",
                                        "China",
                                        "Singapore",
                                        "UAE",
                                    ],
                                    index=(["", "USA", "UK", "Germany", "France", "Italy", "Spain", "Netherlands", "Canada", "Australia", "China", "Singapore", "UAE"].index(c.country) if c.country in ["", "USA", "UK", "Germany", "France", "Italy", "Spain", "Netherlands", "Canada", "Australia", "China", "Singapore", "UAE"] else 0),
                                )
                            with e_cols2[1]:
                                new_status = st.selectbox(
                                    "状态",
                                    [
                                        "cold",
                                        "contacted",
                                        "replied",
                                        "qualified",
                                        "negotiating",
                                        "customer",
                                        "lost",
                                    ],
                                    index=(
                                        ["cold", "contacted", "replied", "qualified", "negotiating", "customer", "lost"].index(c.status)
                                        if (c.status in ["cold", "contacted", "replied", "qualified", "negotiating", "customer", "lost"]) else 0
                                    ),
                                )
                            with e_cols2[2]:
                                new_source = st.text_input("来源（如：Google/LinkedIn）", value=c.source or "")
                            e_cols3 = st.columns(3)
                            with e_cols3[0]:
                                new_website = st.text_input("网站", value=c.website or "")
                            with e_cols3[1]:
                                new_industry = st.selectbox(
                                    "行业",
                                    ["", "Retail", "E-commerce", "Fashion", "Fitness", "Hotel", "Subscription"],
                                    index=(
                                        ["", "Retail", "E-commerce", "Fashion", "Fitness", "Hotel", "Subscription"].index(c.industry)
                                        if (c.industry in ["", "Retail", "E-commerce", "Fashion", "Fitness", "Hotel", "Subscription"]) else 0
                                    ),
                                )
                            with e_cols3[2]:
                                new_phone = st.text_input("电话", value=c.phone or "")

                            saved = st.form_submit_button("保存修改")
                            if saved:
                                try:
                                    c.company_name = new_company.strip() or c.company_name
                                    c.contact_name = new_contact.strip() or None
                                    c.email = new_email.strip() or None
                                    c.country = new_country or None
                                    c.status = new_status
                                    c.source = new_source.strip() or None
                                    c.website = new_website.strip() or None
                                    c.industry = new_industry or None
                                    c.phone = new_phone.strip() or None
                                    self.session.commit()
                                    st.success("已更新")
                                    st.session_state[f"edit_{c.id}"] = False
                                    st.rerun()
                                except Exception as e:
                                    self.session.rollback()
                                    st.error(f"更新失败：{e}")

    def render_email_campaigns(self):
        st.subheader("📧 邮件营销")

        customers = self.session.query(Customer).all()
        if not customers:
            st.info("当前还没有客户，请先在客户管理页新增客户。")
            return

        # 选择目标客户
        options = {f"{c.company_name} ({c.contact_name or '-'} | {c.email or '-'})": c.id for c in customers}
        labels = list(options.keys())
        preselect_index = 0
        if "selected_customer_id" in st.session_state:
            for i, lbl in enumerate(labels):
                if options[lbl] == st.session_state["selected_customer_id"]:
                    preselect_index = i
                    break
        selection = st.selectbox("选择客户", labels, index=preselect_index)
        customer_id = options[selection]
        customer = next(c for c in customers if c.id == customer_id)

        # 生成主题与正文（可编辑）
        default_subject = f"Quick question about {customer.company_name}"
        if "quick_reply_subject" in st.session_state:
            default_subject = st.session_state.pop("quick_reply_subject")
        subject = st.text_input("主题", default_subject)

        writer = AIEmailWriter()
        generated = writer.generate_cold_email(
            {
                "company_name": customer.company_name,
                "contact_name": customer.contact_name,
                "website": customer.website,
                "industry": customer.industry,
            }
        )
        if "quick_reply_body" in st.session_state:
            generated = st.session_state.pop("quick_reply_body")

        body = st.text_area("正文", generated, height=240)

        # 附件上传
        uploaded_files = st.file_uploader("上传附件（可选）", accept_multiple_files=True)
        attachments_info = []
        # 快速回复带入的附件
        if "quick_reply_attachments" in st.session_state:
            import json
            try:
                prev_attachments = json.loads(st.session_state.pop("quick_reply_attachments"))
                attachments_info.extend(prev_attachments)
                st.info(f"已自动带入 {len(prev_attachments)} 个原附件")
            except Exception:
                pass
        if uploaded_files:
            import os
            attach_dir = "data/attachments"
            os.makedirs(attach_dir, exist_ok=True)
            for uf in uploaded_files:
                file_path = os.path.join(attach_dir, f"{customer.id}_{uf.name}")
                with open(file_path, "wb") as f:
                    f.write(uf.getbuffer())
                attachments_info.append(file_path)
            st.success(f"已上传 {len(uploaded_files)} 个新附件")

        cols = st.columns(2)
        with cols[0]:
            save_clicked = st.button("保存到历史（不发送）", type="primary")
        with cols[1]:
            # 预留：未来集成真实发送
            st.button("模拟发送（预留）", disabled=True)

        if save_clicked:
            try:
                from datetime import datetime, timedelta
                import json
                record = EmailHistory(
                    customer_id=customer.id,
                    direction="outbound",
                    subject=subject,
                    body=body,
                    ai_generated=True,
                    attachments=json.dumps(attachments_info) if attachments_info else None,
                )
                self.session.add(record)
                # 更新客户的最近联系和下次跟进时间
                customer.last_contact_date = datetime.now()
                customer.next_followup_date = datetime.now() + timedelta(days=int(st.session_state.get("settings", {}).get("followup_days", 7)))
                self.session.commit()
                st.success("已保存到客户邮件历史，并更新跟进日期")
            except Exception as e:
                self.session.rollback()
                st.error(f"保存失败：{e}")

        # 展示该客户最近邮件历史（简版）
        st.markdown("---")
        st.markdown("**最近邮件历史（Top 10）**")
        history = (
            self.session.query(EmailHistory)
            .filter(EmailHistory.customer_id == customer.id)
            .order_by(EmailHistory.id.desc())
            .limit(200)
            .all()
        )
        dir_filter = st.selectbox("方向过滤", ["全部", "outbound", "inbound"], index=0)
        q = st.text_input("搜索主题或正文", "")
        import pandas as pd
        data = []
        for h in history:
            if dir_filter != "全部" and h.direction != dir_filter:
                continue
            if q and q.lower() not in (f"{h.subject or ''} {h.body or ''}".lower()):
                continue
            data.append({
                "方向": h.direction,
                "主题": h.subject,
                "AI生成": "是" if h.ai_generated else "否",
                "ID": h.id,
            })
        df = pd.DataFrame(data)
        if df.empty:
            st.info("暂无历史记录或无匹配结果。")
        else:
            st.dataframe(df[["方向", "主题", "AI生成"]], use_container_width=True)
            # 查看详情
            selected_id = st.selectbox("选择邮件ID查看详情", df["ID"].tolist() if not df.empty else [], format_func=lambda x: f"ID: {x}")
            if selected_id:
                detail = next((h for h in history if h.id == selected_id), None)
                if detail:
                    with st.expander(f"详情 - {detail.subject or '(无主题)'}", expanded=True):
                        st.write(f"**方向**: {detail.direction}")
                        st.write(f"**主题**: {detail.subject or '-'}")
                        st.write(f"**正文**:")
                        st.text_area("", detail.body or "(无正文)", height=200, key=f"body_{detail.id}")
                        st.write(f"**AI生成**: {'是' if detail.ai_generated else '否'}")
                        # 附件下载
                        if detail.attachments:
                            import json
                            try:
                                attach_list = json.loads(detail.attachments)
                                st.write(f"**附件** ({len(attach_list)} 个):")
                                for att in attach_list:
                                    import os
                                    if os.path.exists(att):
                                        filename = os.path.basename(att)
                                        col_preview, col_action = st.columns([3, 1])
                                        with col_preview:
                                            # 图片预览
                                            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                                st.image(att, caption=filename, width=300)
                                            # PDF预览
                                            elif filename.lower().endswith('.pdf'):
                                                with open(att, "rb") as f:
                                                    pdf_bytes = f.read()
                                                    import base64
                                                    b64 = base64.b64encode(pdf_bytes).decode()
                                                    pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="400" type="application/pdf"></iframe>'
                                                    st.markdown(pdf_display, unsafe_allow_html=True)
                                            # Word预览
                                            elif filename.lower().endswith(('.doc', '.docx')):
                                                try:
                                                    import mammoth
                                                    with open(att, "rb") as docx_file:
                                                        result = mammoth.convert_to_html(docx_file)
                                                        st.markdown(result.value, unsafe_allow_html=True)
                                                except ImportError:
                                                    st.info("Word预览需安装 mammoth: pip install mammoth")
                                                except Exception as e:
                                                    st.info(f"Word预览失败: {e}")
                                            # Excel预览
                                            elif filename.lower().endswith(('.xls', '.xlsx')):
                                                try:
                                                    import pandas as pd
                                                    df = pd.read_excel(att)
                                                    st.dataframe(df, use_container_width=True)
                                                except Exception as e:
                                                    st.info(f"Excel预览失败: {e}")
                                            else:
                                                st.info(f"文件: {filename} (不支持预览)")
                                        with col_action:
                                            with open(att, "rb") as f:
                                                st.download_button(f"⬇️ 下载", f, file_name=filename, key=f"dl_{detail.id}_{att}")
                                            if st.button(f"🗑️ 删除", key=f"del_{detail.id}_{att}"):
                                                try:
                                                    attach_list.remove(att)
                                                    detail.attachments = json.dumps(attach_list) if attach_list else None
                                                    self.session.commit()
                                                    if os.path.exists(att):
                                                        os.remove(att)
                                                    st.success("已删除附件")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"删除失败: {e}")
                            except Exception as e:
                                st.info(f"附件解析失败: {e}")
                        else:
                            st.info("无附件")
                        # 快速回复按钮
                        if st.button("快速回复", key=f"reply_{detail.id}"):
                            st.session_state["quick_reply_subject"] = f"Re: {detail.subject or ''}" 
                            st.session_state["quick_reply_body"] = f"\n\n--- 原邮件 ---\n{detail.body or ''}\n---\n"
                            # 带入附件
                            if detail.attachments:
                                st.session_state["quick_reply_attachments"] = detail.attachments
                            st.success("已填充回复内容（含附件），请向上滚动到邮件生成区")


    def render_orders(self):
        st.subheader("📦 订单管理")

        customers = self.session.query(Customer).all()
        if not customers:
            st.info("当前还没有客户，请先在客户管理页新增客户。")
            return

        options = {f"{c.company_name} ({c.contact_name or '-'} | {c.email or '-'})": c.id for c in customers}
        labels = list(options.keys())
        preselect_index = 0
        if "selected_customer_id" in st.session_state:
            for i, lbl in enumerate(labels):
                if options[lbl] == st.session_state["selected_customer_id"]:
                    preselect_index = i
                    break
        selection = st.selectbox("选择客户", labels, index=preselect_index)
        customer_id = options[selection]
        customer = next(c for c in customers if c.id == customer_id)

        # 创建订单表单
        with st.form("create_order_form"):
            st.markdown("**创建订单**")
            cols = st.columns(3)
            with cols[0]:
                product_details = st.text_input("产品描述", "Men's underwear - private label")
            with cols[1]:
                quantity = st.number_input("数量", min_value=1, step=10, value=100)
            with cols[2]:
                unit_price = st.number_input("单价(USD)", min_value=0.0, step=0.1, value=2.5)
            cols2 = st.columns(3)
            with cols2[0]:
                status = st.selectbox("状态", ["quotation", "confirmed", "production", "shipped", "delivered", "completed"], index=0)
            with cols2[1]:
                factory_name = st.text_input("工厂名称", "Main Factory")
            with cols2[2]:
                notes = st.text_input("备注", "")
            cols3 = st.columns(2)
            with cols3[0]:
                prod_start = st.date_input("生产开始日期", None)
            with cols3[1]:
                est_complete = st.date_input("预计发货日期", None)

            ship_actual = st.date_input("实际发货日期", None)

            submitted = st.form_submit_button("保存订单")
            if submitted:
                try:
                    from datetime import datetime
                    import random
                    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
                    total_amount = float(quantity) * float(unit_price)
                    # 将日期合并为 datetime（如存在）
                    prod_dt = datetime.combine(prod_start, datetime.min.time()) if prod_start else None
                    est_dt = datetime.combine(est_complete, datetime.min.time()) if est_complete else None
                    ship_dt = datetime.combine(ship_actual, datetime.min.time()) if ship_actual else None
                    o = Order(
                        customer_id=customer.id,
                        order_number=order_number,
                        product_details=product_details,
                        quantity=int(quantity),
                        unit_price=float(unit_price),
                        total_amount=total_amount,
                        status=status,
                        factory_name=factory_name or None,
                        notes=notes or None,
                        order_date=datetime.now(),
                        production_start_date=prod_dt,
                        estimated_completion_date=est_dt,
                        ship_date=ship_dt,
                    )
                    self.session.add(o)
                    self.session.commit()
                    st.success(f"订单已保存: {order_number} (总额 ${total_amount:.2f})")
                    st.rerun()
                except Exception as e:
                    self.session.rollback()
                    st.error(f"保存失败：{e}")

        # 订单列表与状态跟踪
        st.markdown("---")
        st.markdown("**该客户订单列表**")
        orders = (
            self.session.query(Order)
            .filter(Order.customer_id == customer.id)
            .order_by(Order.id.desc())
            .all()
        )
        if not orders:
            st.info("暂无订单记录。")
        else:
            for o in orders:
                total = f"${(o.total_amount or 0):.2f}"
                with st.expander(f"{o.order_number} | 状态: {o.status} | 总额: {total}"):
                    st.write(f"产品: {o.product_details}")
                    st.write(f"数量: {o.quantity} | 单价: ${o.unit_price}")
                    st.write(f"工厂: {o.factory_name or '-'}")
                    st.write(f"备注: {o.notes or '-'}")

                    # 简易时间线
                    tl = []
                    def fmt(d):
                        return d.strftime('%Y-%m-%d') if d else '-'
                    tl.append(f"订单创建: {fmt(o.order_date)}")
                    tl.append(f"生产开始: {fmt(o.production_start_date)}")
                    tl.append(f"预计发货: {fmt(o.estimated_completion_date)}")
                    tl.append(f"实际发货: {fmt(o.ship_date)}")
                    st.markdown("**时间线**")
                    for item in tl:
                        st.write(f"- {item}")

                    # 可视化流程图
                    st.markdown("**订单流程可视化**")
                    stages = [
                        {"name": "报价", "status": "quotation", "date": o.order_date},
                        {"name": "确认", "status": "confirmed", "date": o.order_date},
                        {"name": "生产", "status": "production", "date": o.production_start_date},
                        {"name": "发货", "status": "shipped", "date": o.estimated_completion_date},
                        {"name": "交付", "status": "delivered", "date": o.ship_date},
                        {"name": "完成", "status": "completed", "date": None},
                    ]
                    current_idx = next((i for i, s in enumerate(stages) if s["status"] == o.status), 0)
                    
                    # Mermaid 流程图
                    mermaid_code = "graph LR\n"
                    for idx, stage in enumerate(stages):
                        node_id = f"N{idx}"
                        date_str = fmt(stage['date']) if stage['date'] else '待定'
                        if idx < current_idx:
                            mermaid_code += f"    {node_id}[\"✅ {stage['name']}<br/>{date_str}\"]:::completed\n"
                        elif idx == current_idx:
                            mermaid_code += f"    {node_id}[\"🔵 {stage['name']}<br/>{date_str}\"]:::current\n"
                        else:
                            mermaid_code += f"    {node_id}[\"⚪ {stage['name']}<br/>{date_str}\"]:::pending\n"
                        if idx < len(stages) - 1:
                            mermaid_code += f"    {node_id} --> N{idx+1}\n"
                    mermaid_code += "    classDef completed fill:#d4edda,stroke:#28a745,stroke-width:2px\n"
                    mermaid_code += "    classDef current fill:#cfe2ff,stroke:#0d6efd,stroke-width:3px\n"
                    mermaid_code += "    classDef pending fill:#f8f9fa,stroke:#6c757d,stroke-width:1px\n"
                    
                    st.markdown(f"```mermaid\n{mermaid_code}\n```")

                    # 进度条与延期状态
                    from datetime import datetime
                    now = datetime.now()
                    status_map = {"quotation": 0.1, "confirmed": 0.3, "production": 0.6, "shipped": 0.9, "delivered": 1.0, "completed": 1.0}
                    progress = status_map.get(o.status, 0.1)
                    is_delayed = False
                    if o.estimated_completion_date and o.estimated_completion_date < now and o.status not in ['shipped', 'delivered', 'completed']:
                        is_delayed = True
                    color = "red" if is_delayed else "green"
                    st.markdown(f"**订单进度** ({int(progress*100)}%)")
                    st.progress(progress)
                    if is_delayed:
                        st.error("⚠️ 订单已延期")
                    else:
                        st.success("✅ 订单正常")

                    u_cols = st.columns(2)
                    with u_cols[0]:
                        new_status = st.selectbox(
                            "更新状态",
                            ["quotation", "confirmed", "production", "shipped", "delivered", "completed"],
                            index=(
                                ["quotation", "confirmed", "production", "shipped", "delivered", "completed"].index(o.status)
                                if o.status in ["quotation", "confirmed", "production", "shipped", "delivered", "completed"] else 0
                            ),
                            key=f"status_{o.id}",
                        )
                    with u_cols[1]:
                        if st.button("保存状态", key=f"save_status_{o.id}"):
                            try:
                                o.status = new_status
                                self.session.commit()
                                st.success("状态已更新")
                                st.rerun()
                            except Exception as e:
                                self.session.rollback()
                                st.error(f"更新失败：{e}")

    def render_settings(self):
        st.subheader("⚙️ 自动化设置")
        # 初始化设置
        if "settings" not in st.session_state:
            st.session_state["settings"] = {
                "followup_days": 7,
                "delay_tolerance_days": 0,
            }
        s = st.session_state["settings"]
        
        # 分页
        tab1, tab2, tab3 = st.tabs(["基础设置", "自动化任务", "工具集"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                followup_days = st.number_input(
                    "默认跟进间隔（天）",
                    min_value=1,
                    max_value=30,
                    value=int(s.get("followup_days", 7)),
                )
            with col2:
                delay_tol = st.number_input(
                    "延期容忍（天）",
                    min_value=0,
                    max_value=14,
                    value=int(s.get("delay_tolerance_days", 0)),
                )
            lang_default = st.session_state.get("lang", "中文")
            lang = st.radio("界面语言", ["中文", "English"], index=(0 if lang_default=="中文" else 1))
            st.session_state["lang"] = lang
            if st.button("保存设置", type="primary"):
                s["followup_days"] = int(followup_days)
                s["delay_tolerance_days"] = int(delay_tol)
                st.success("设置已保存")
            st.info("说明：保存后，新的邮件保存将按跟进间隔生成 next_followup_date；延期订单按容忍天数判断。")
        
        with tab2:
            st.markdown("**自动化任务调度**")
            st.info("调度器占位，需单独运行后台进程")
            
            schedule_info = """
            **已配置的定时任务：**
            - 🔍 每天 09:00: 搜索新客户（50个）
            - 📧 每天 10:00: 发送每日邮件
            - 🔔 每 2 小时: 检查邮件回复
            - 📦 每天 15:00: 订单状态检查
            - 📈 每周一 09:00: 生成周报
            
            **启动调度器：**
            ```bash
            python -m src.utils.scheduler
            ```
            """
            st.markdown(schedule_info)
        
        with tab3:
            st.markdown("**客户获取工具**")
            if st.button("测试Google搜索器"):
                from src.prospecting.google_scraper import GoogleScraper
                scraper = GoogleScraper()
                results = scraper.find_prospects(limit=5)
                st.success(f"找到 {len(results)} 个潜在客户")
                import pandas as pd
                st.dataframe(pd.DataFrame(results))
            
            st.markdown("**邮箱查找工具**")
            test_domain = st.text_input("测试域名", "example.com")
            if st.button("查找邮箱"):
                from src.prospecting.email_finder import EmailFinder
                finder = EmailFinder()
                emails = finder.get_company_emails(test_domain)
                st.write("可能的邮箱：")
                for email in emails:
                    st.code(email)
            
            st.markdown("---")
            st.markdown("**报表生成器**")
            if st.button("生成周报"):
                from src.utils.reports import ReportGenerator
                reporter = ReportGenerator(self.session)
                report = reporter.generate_weekly_report()
                st.text_area("周报内容", report, height=300)
                st.download_button("下载周报", report, file_name=f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt")
            
            st.markdown("**通知测试**")
            if st.button("发送测试通知"):
                from src.utils.notification import NotificationSystem
                notifier = NotificationSystem()
                notifier.send_alert("系统测试", "这是一条测试通知消息", "info")
                st.success("通知已发送（控制台查看）")


def main():
    dashboard = CRMDashboard()
    dashboard.render()
