# 📄 PDF Outline Extractor

This project extracts a structured outline (Title, H1–H4) from PDF documents based on font size, style, and layout. Built for **Adobe India Hackathon Round 1A**, it uses Python and PyMuPDF for accurate text parsing.

---

## 📦 Features

- Extracts the **document title** from the first page (can span up to 2 lines)
- Identifies headings as **H1, H2, H3, H4** based on font size and boldness
- Skips repeating the title in the heading list
- Removes unwanted lines (headers, footers, boilerplate text)
- Outputs clean, structured `.json` files

---

## 🛠️ Tech Stack

- Python 3.9+
- PyMuPDF (`fitz`)
- Docker (for easy containerized execution)

---

## 📁 Folder Structure

project/
├── app/
│ └── main.py
├── input/
│ └── your-file.pdf
├── output/
├── Dockerfile
└── README.md
---

## 🐳 Running with Docker

### Step 1: Build the Docker image

```bash
docker build -t pdf-outline .

### Step 2: Run the Container

docker run --rm -v ${PWD}/input:/input -v ${PWD}/output:/output pdf-outline

##OUTPUT FORMAT
 {
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Section",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subsection",
      "page": 2
    }
  ]
}

