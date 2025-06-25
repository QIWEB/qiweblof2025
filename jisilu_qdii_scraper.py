import requests
from bs4 import BeautifulSoup
import yagmail

def fetch_qdii_data():
    url = "https://www.jisilu.cn/data/qdii/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    session = requests.Session()
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find("table", id="flex_qdiic")
    rows = table.tbody.find_all("tr")[:4]

    data = []
    for row in rows:
        cols = row.find_all("td")
        record = [col.text.strip() for col in cols[:12]]
        data.append(record)

    return data

def format_html_table(data):
    # 新表头顺序：把 "T-1 溢价率" 放到 "现价" 后
    headers = [
        "代码", "名称", "现价", "T-1溢价率", "涨幅", "成交(万元)", "场内份额(万份)",
        "新增(万份)", "T-2净值", "净值日期", "T-1估值", "估值日期"
    ]
    
    html = '<table border="1" cellpadding="5" cellspacing="0">'
    html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    
    for row in data:
        # row原始顺序是 0:代码, 1:名称, 2:现价, 3:涨幅, 4:成交, 5:场内份额,
        # 6:新增, 7:T-2净值, 8:净值日期, 9:T-1估值, 10:估值日期, 11:T-1溢价率
        rearranged = [
            row[0],       # 代码
            row[1],       # 名称
            row[2],       # 现价
            row[11],      # T-1溢价率（新位置）
            row[3],       # 涨幅
            row[4],       # 成交
            row[5],       # 场内份额
            row[6],       # 新增份额
            row[7],       # T-2净值
            row[8],       # 净值日期
            row[9],       # T-1估值
            row[10],      # 估值日期
        ]
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in rearranged) + "</tr>"
    
    html += "</table>"
    return html


def send_email(html_table):
    user = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    to = os.environ["EMAIL_TO"]

    yag = yagmail.SMTP(user=user, password=password)
    yag.send(to=to, subject="集思录QDII 数据报告", contents=[html_table])

if __name__ == "__main__":
    import os
    data = fetch_qdii_data()
    html = format_html_table(data)
    send_email(html)
