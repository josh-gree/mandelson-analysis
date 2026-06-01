import fitz
import json
from pathlib import Path

pdf_path = Path("HA_Volume_II_part_I.pdf")
doc = fitz.open(pdf_path)

pages = []
for i, page in enumerate(doc):
    text = page.get_text()
    pages.append({"page": i + 1, "text": text})
    print(f"Page {i + 1}/{len(doc)}: {len(text)} chars")

output = Path("extracted_text.json")
output.write_text(json.dumps(pages, indent=2, ensure_ascii=False))
print(f"\nDone. {len(doc)} pages → {output}")
