import fitz
import json
from pathlib import Path

pages = json.loads(open("extracted_text.json").read())
empty_page_nums = [p["page"] for p in pages if len(p["text"].strip()) <= 4]

out_dir = Path("page_images")
out_dir.mkdir(exist_ok=True)

doc = fitz.open("HA_Volume_II_part_I.pdf")
mat = fitz.Matrix(2, 2)  # 2x zoom = ~150dpi, good for OCR

print(f"Rendering {len(empty_page_nums)} image-based pages...")
for i, pnum in enumerate(empty_page_nums):
    page = doc[pnum - 1]
    pix = page.get_pixmap(matrix=mat)
    out_path = out_dir / f"page_{pnum:04d}.png"
    pix.save(out_path)
    if (i + 1) % 50 == 0:
        print(f"  {i + 1}/{len(empty_page_nums)} done")

print(f"\nDone. Images saved to {out_dir}/")
