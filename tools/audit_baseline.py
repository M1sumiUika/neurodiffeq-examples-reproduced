"""读取全部 PDF 页面，只保存元数据和定位清单，不分发整本PDF或全文。"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader

p=argparse.ArgumentParser()
p.add_argument("pdf")
args=p.parse_args()
path=Path(args.pdf)
r=PdfReader(path)
root=Path(__file__).resolve().parents[1]
pages=[]
for i,page in enumerate(r.pages):
    text=page.extract_text()
    fonts=[]
    def visit(t,cm,tm,font,size):
        if font and t.strip(): fonts.append((str(font.get("/BaseFont","")),t.strip()))
    page.extract_text(visitor_text=visit)
    candidates=[t for font,t in fonts if ("Mono" in font or "Courier" in font or "SFTT" in font or "NimbusMon" in font) and
                ("=" in t or "solution(" in t or "MeshGenerator" in t)]
    pages.append(dict(pdf_page=i+1,printed_page=i-3 if i>=4 else None,
        characters=len(text),cell_labels=sorted(set(re.findall(r"\[(\d+)\]:",text)), key=int),
        api_code_candidates=candidates if 38<=i<124 else []))
report=dict(filename=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            pages=len(r.pages),metadata={str(k):str(v) for k,v in r.metadata.items()},
            page_scan=pages,scope="全页提取；代码块、内嵌用法与图表另经人工核对。API签名不视为可执行示例。")
(root/"docs/baseline_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Pages:",len(pages),"SHA256:",report["sha256"])
for i in range(38,124):
    text=r.pages[i].extract_text()
    names=re.findall(r"(?:class)?neurodiffeq\.[a-z_]+\.\s*([A-Za-z_]+)",text)
    print(f"PDF {i+1}: "+", ".join(names))

