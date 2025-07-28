FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install pymupdf

CMD ["python", "main.py"]
