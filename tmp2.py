import json
from pdfrw import PdfReader, PdfWriter
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, portrait

# OCR結果を重ねる処理に必要なファイルは以下の2つです
PDF_FILE = "sample.pdf"
OCR_RESULT_FILE = "OCR_sample_data.json"

# 文字コードの指定
encoding = "utf_8_sig"

# フォントを指定
font_name = "HeiseiKakuGo-W5"


# 1ページ分のPDFを作成する関数
def make_page(writer, font_name, pdf_page, data_page):
    # 中間生成物ファイル名
    tmp_file = "work.pdf"

    # OCR結果のjsonデータからページサイズを取得
    page_width = data_page["width"]
    page_height = data_page["height"]
    pagesize = (page_width * inch, page_height * inch)

    # ここで定義したpdfにOCR結果を重畳して、tmp_fileに保存する
    pdf = canvas.Canvas(tmp_file, pagesize = pagesize)

    # 既存のPDFページをオブジェクト化
    pp = pagexobj(pdf_page)
    pdf.doForm(makerl(pdf,pp))

    # フォント設定
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    pdf.setFont(font_name, 8)

    # テキスト書き込み
    for line_num, line in enumerate(data_page["lines"]):
        # テキスト始点座標
        (pos_x,pos_y) = (line["boundingBox"][6], line["boundingBox"][7])

        # テキストボックスサイズ
        box_width = line["boundingBox"][2]-line["boundingBox"][0]
        box_height = line["boundingBox"][7]-line["boundingBox"][1]

        # 色指定
        pdf.setFillColorRGB(1,1,1,0)
        pdf.setStrokeColorRGB(1,0,0,1)

        # テキストボックス描画
        pdf.setStrokeColorRGB(0,1,0,1)
        pdf.rect(
            pos_x * inch,
            (page_height - pos_y) * inch,
            box_width * inch,
            box_height * inch,
            stroke = 1,
            fill = 1
        )

        pdf.setFillColorRGB(0,0,1,1)
        # テキスト番号表示
        pdf.drawString(
            (pos_x - 0.3) * inch, # ここでx方向の位置を調整する
            (page_height - pos_y + 0.2) * inch, # ここでy方向の位置を調整する
            "L:" + str(line_num)
        )

        # テキスト
        text = line["text"]

        pdf.setFillColorRGB(1,0,0,1)
        # テキストを描画する
        pdf.drawString(
            pos_x * inch,  # ここでx方向の位置を調整する
            (page_height - pos_y + box_height) * inch, # ここでy方向の位置を調整する
            text
        )

    pdf.showPage()
    pdf.save()

    # 中間生成のPDFファイルを読み込む
    with open(tmp_file, mode="rb") as f:
        pdf_reader = PdfReader(f)

    # 中間生成PDFをwriterに取り込む
    writer.addPage(pdf_reader.pages[0])




# 出力ファイル名を定義
PDF_FILE_WITH_OCR_RESULT = "OCR_sample_data_mapping.pdf"

# OCR結果ファイル(json)をロードする
with open(OCR_RESULT_FILE,"r",encoding = encoding) as f:
    data_dict = json.load(f)

# pdfwriter定義
pdf_writer = PdfWriter()

# OCR対象となったPDFファイルを読み込む
input_pdf_pages = PdfReader(PDF_FILE, decompress = False).pages

# ファイルのページ分処理を回す
for page_num,data_page in enumerate(data_dict["analyzeResult"]["readResults"]):

    # 所定のページのpdf情報を取得する
    pdf_page = input_pdf_pages[page_num]

    # 1ページ毎にOCRの結果が重畳されたPDFデータを作成してpdf_writerに書き込む
    make_page(pdf_writer, font_name, pdf_page, data_page)

# OCR結果が重畳されたPDFデータをファイル化する
with open(PDF_FILE_WITH_OCR_RESULT, mode="wb") as f:
    pdf_writer.write(f)