# -*- coding: utf-8 -*-
"""
聚宽QDII异步接口数据获取 + 邮件发送（使用阿里源安装依赖）
pip install -i https://mirrors.aliyun.com/pypi/simple requests
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

# 获取数据
def fetch_qdii_data():
    timestamp = int(time.time() * 1000)
    url = f"https://www.jisilu.cn/data/qdii/qdii_list/C?___jsl=LST___t={timestamp}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.jisilu.cn/data/qdii/"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    rows = response.json().get("rows", [])[:10]  # 可选前10个
    result = []

    for row in rows:
        cell = row.get("cell", {})
        result.append([
            cell.get("fund_id", ""),            # 基金代码
            cell.get("fund_nm", ""),            # 基金名称
            cell.get("price", ""),              # 现价
            cell.get("discount_rt", ""),        # T-1溢价率
            cell.get("increase_rt", ""),        # 涨跌幅
            cell.get("volume", ""),             # 成交量
            cell.get("amount", ""),             # 总份额
            cell.get("fund_nav", ""),           # 单位净值
            cell.get("nav_dt", ""),             # 净值日期
            cell.get("estimate_value", ""),     # 估值
            cell.get("est_val_dt", "")          # 估值日期
        ])
    return result

# 格式化为纯文本表格
def format_table(data):
    headers = ["基金代码", "基金名称", "现价", "T-1溢价率", "涨跌幅", "成交量", "总份额", "单位净值", "净值日期", "估值", "估值日期"]
    lines = ["\t".join(headers)]
    for row in data:
        lines.append("\t".join(row))
    return "\n".join(lines)

# 发邮件（QQ邮箱为例）
def send_email(subject, body, sender, receivers, smtp_server, smtp_port, smtp_user, smtp_pass):
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(sender)
    message['To'] = Header(", ".join(receivers))
    message['Subject'] = Header(subject, 'utf-8')

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        print("✅ 邮件发送成功")
    except Exception as e:
        print("❌ 邮件发送失败:", e)

# 主流程
if __name__ == "__main__":
    qdii_data = fetch_qdii_data()
    table_str = format_table(qdii_data)

    # 邮件配置
    subject = "聚宽QDII异步数据日报"
    sender = "your_email@qq.com"
    receivers = ["target@example.com"]
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    smtp_user = "your_email@qq.com"
    smtp_pass = "你的授权码"  # 注意这里是授权码

    send_email(subject, table_str, sender, receivers, smtp_server, smtp_port, smtp_user, smtp_pass)
