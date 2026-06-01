import json
import pytesseract
from PIL import Image
from pathlib import Path

pages = {p["page"]: p["text"] for p in json.loads(open("extracted_text.json").read())}
image_pages = {int(f.stem.split("_")[1]): f for f in sorted(Path("page_images").glob("*.png"))}

print(f"Native text pages: {len([p for p in pages if len(pages[p].strip()) > 4])}")
print(f"Image pages to OCR: {len(image_pages)}")

merged = {}

# Native text pages
for pnum, text in pages.items():
    if len(text.strip()) > 4:
        merged[pnum] = {"page": pnum, "source": "pdf", "text": text}

# OCR image pages
total = len(image_pages)
for i, (pnum, img_path) in enumerate(image_pages.items()):
    text = pytesseract.image_to_string(Image.open(img_path))
    merged[pnum] = {"page": pnum, "source": "ocr", "text": text}
    if (i + 1) % 25 == 0:
        print(f"  OCR: {i + 1}/{total} pages done")

# Output in page order
ordered = [merged[p] for p in sorted(merged.keys())]

output = Path("full_text.json")
output.write_text(json.dumps(ordered, indent=2, ensure_ascii=False))

total_chars = sum(len(p["text"]) for p in ordered)
pdf_pages = sum(1 for p in ordered if p["source"] == "pdf")
ocr_pages = sum(1 for p in ordered if p["source"] == "ocr")
print(f"\nDone. {len(ordered)} pages → {output}")
print(f"  PDF text: {pdf_pages} pages")
print(f"  OCR text: {ocr_pages} pages")
print(f"  Total chars: {total_chars:,}")
