# pdf_processor.py
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

def clean_text(text):
    """Clean extracted PDF text"""
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces
    return text.strip()

def process_pdf(pdf_path):
    """Extract and chunk PDF content"""
    print(f"Processing PDF: {pdf_path}")
    
    # Extract text
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_text(cleaned_text)
    print(f"Created {len(chunks)} text chunks")
    return chunks

if __name__ == "__main__":
    chunks = process_pdf("gale_encyclopedia.pdf")
    with open("chunks_sample.txt", "w") as f:
        f.write("\n\n--- CHUNK ---\n\n".join(chunks[:3]))  # Save first 3 chunks as sample