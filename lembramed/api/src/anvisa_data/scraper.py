from pdfquery import PDFQuery 
import pandas as pd
import re
from pdfminer.high_level import extract_text, extract_pages
import pypdfium2 as pdfium

# re.compile() STARTWITH NUM AND HAS ONLY CAPITAL LETTERS

def get_pdf(pdf_path):
    """Returns a dictionary of topics extracted from each medication bula"""
    # text = extract_text(f"{pdf_path}")
    
    text = "\n".join(
        p.get_textpage().get_text_range() 
        for p in pdfium.PdfDocument(f"{pdf_path}")
    )
    print(text)

    # pdf = PDFQuery(f"{pdf_path}")
    # pdf.load()
    # # Use CSS-like selectors to locate the elements
    # text_elements = pdf.pq('LTTextLineHorizontal')
    # # Extract the text from the elements
    # text = [t.text for t in text_elements]
    # print(text)

    # pdf = PDFQuery(f"{pdf_path}")
    # pdf.load()
    # pdf.tree.write('customers.xml', pretty_print = True)

    # pdf = PDFQuery(f"{pdf_path}")
    # topics = re.compile(r"[0-9]{1}+\.{1}+")
    # print(topics.findall(text))

    # label = pdf.pq('LTTextLineHorizontal:contains("PARA QUE ESTE MEDICAMENTO É INDICADO?")')
    # left_corner = float(label.attr('x0'))
    # bottom_corner = float(label.attr('y0'))
    # name = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner-30, left_corner+150, bottom_corner)).text()
    # print(name)

get_pdf('data/bula_1770753006028.pdf')