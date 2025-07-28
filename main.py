import os
import json
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any


class PDFOutlineExtractor:
    def extract_text_with_lines(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        all_lines = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                for line in block.get("lines", []):
                    text = ""
                    sizes, flags, bboxes = [], [], []

                    for span in line["spans"]:
                        if not span["text"].strip():
                            continue
                        text += " " + span["text"].strip()
                        sizes.append(span["size"])
                        flags.append(span["flags"])
                        bboxes.append(span["bbox"])

                    if text.strip():
                        all_lines.append({
                            "text": text.strip(),
                            "page": page_num + 1,
                            "font_size": max(sizes),
                            "font_flags": max(flags),
                            "bbox": bboxes[0]
                        })

        doc.close()
        return all_lines

    def extract_title(self, lines: List[Dict]) -> str:
        first_page = [l for l in lines if l["page"] == 1]
        if not first_page:
            return "Untitled Document"

        first_page.sort(key=lambda l: l["bbox"][1])  # top-down
        base = first_page[0]
        title = base["text"]
        title_font = base["font_size"]
        title_flags = base["font_flags"]

        for next_line in first_page[1:]:
            if abs(next_line["font_size"] - title_font) < 0.5 and \
               next_line["font_flags"] == title_flags and \
               abs(next_line["bbox"][1] - base["bbox"][3]) < 25:
                title += " " + next_line["text"]
                break

        return re.sub(r"\s+", " ", title.strip()).rstrip(" .,:")

    def is_heading_candidate(self, text: str) -> bool:
        text = text.lower()
        if len(text) < 3 or sum(c in text for c in '.,;:!?') > 5:
            return False

        blacklist = [
            'figure', 'table', 'http', '@', 'email', 'copyright',
            'isbn', 'doi', 'page', 'signature', 'name of', 'date of'
        ]
        return not any(word in text for word in blacklist)

    def classify_heading_level(self, font_size: float, all_sizes: List[float], flags: int) -> str:
        unique_sizes = sorted(set(all_sizes), reverse=True)
        is_bold = flags & (1 << 4) != 0

        if font_size >= unique_sizes[0] - 0.1:
            return "H1"
        elif len(unique_sizes) > 1 and font_size >= unique_sizes[1] - 0.1:
            return "H2" if is_bold else "H3"
        elif len(unique_sizes) > 2 and font_size >= unique_sizes[2] - 0.1:
            return "H3"
        else:
            return "H4"

    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        lines = self.extract_text_with_lines(pdf_path)
        if not lines:
            return {"title": "Empty Document", "outline": []}

        title = self.extract_title(lines)
        font_sizes = [line["font_size"] for line in lines]

        outline = []
        seen = set()

        for line in lines:
            text = line["text"].strip()
            if text.lower() == title.lower() or text in seen:
                continue
            if not self.is_heading_candidate(text):
                continue

            level = self.classify_heading_level(line["font_size"], font_sizes, line["font_flags"])
            outline.append({
                "level": level,
                "text": text,
                "page": line["page"]
            })
            seen.add(text)

        return {"title": title, "outline": outline}


def process_directory():
    input_dir = Path("/input")
    output_dir = Path("/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    extractor = PDFOutlineExtractor()
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"📄 Processing: {pdf_file.name}")
        result = extractor.extract_outline(str(pdf_file))

        output_path = output_dir / f"{pdf_file.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved: {output_path.name}")


if __name__ == "__main__":
    process_directory()
