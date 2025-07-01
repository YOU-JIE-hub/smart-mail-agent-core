# src/quote_generator.py

from fpdf import FPDF
from datetime import datetime
import os
import logging
logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
logging.getLogger("fpdf").setLevel(logging.WARNING)
# 預設報價方案與價格
STANDARD_PACKAGES = {
    "AI 顧問入門方案": 12000,
    "RPA 自動化整合": 18000,
    "企業級部署支援": 30000
}

# 系統預設中文字型路徑（需事先安裝）
FONT_PATH_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_PATH_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def generate_quote_pdf_pretty(output_path: str, client_name: str, package_name: str = None, custom_items: list = None):
    # 建立 PDF 物件與頁面
    pdf = FPDF()
    pdf.add_page()

    # 載入中文字型
    pdf.add_font("NotoSans", "", FONT_PATH_REGULAR, uni=True)
    pdf.add_font("NotoSans", "B", FONT_PATH_BOLD, uni=True)

    # 標題
    pdf.set_font("NotoSans", "B", 20)
    pdf.set_text_color(150, 0, 0)
    pdf.cell(0, 15, "報價單 Quotation", ln=True)

    # 基本資訊
    pdf.set_font("NotoSans", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"日期：{datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(0, 10, f"客戶名稱：{client_name}", ln=True)
    pdf.ln(5)

    # 欄位標題
    col_name = 120
    col_price = 50

    pdf.set_font("NotoSans", "B", 12)
    pdf.cell(col_name, 10, "項目", border=1)
    pdf.cell(col_price, 10, "價格 (NT$)", border=1, ln=True)

    # 資料內容
    items = custom_items if custom_items else [{"name": package_name, "price": STANDARD_PACKAGES.get(package_name, 0)}]
    if not items or (not custom_items and package_name not in STANDARD_PACKAGES):
        raise ValueError("請指定有效 package_name 或 custom_items")

    pdf.set_font("NotoSans", "", 12)
    total = 0
    for it in items:
        pdf.cell(col_name, 10, it['name'], border=1)
        pdf.cell(col_price, 10, f"{it['price']}", border=1, ln=True)
        total += it['price']

    # 總計
    pdf.set_font("NotoSans", "B", 12)
    pdf.cell(col_name, 10, "總計：", border=1)
    pdf.cell(col_price, 10, f"{total}", border=1, ln=True)

    # 備註
    pdf.ln(10)
    pdf.set_font("NotoSans", "", 11)
    pdf.set_text_color(100, 100, 255)
    pdf.cell(0, 10, "如有疑問請聯絡我們，謝謝！", ln=True)

    # 儲存檔案
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)

    print(f"報價單已產出：{output_path}")
