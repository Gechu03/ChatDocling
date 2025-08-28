import os
import lancedb
from docling.document_converter import DocumentConverter
from utils.sitemap import get_sitemap_urls

UPLOAD_DIR = "data/uploads"
DB_DIR = "data/lancedb"
TABLE_NAME = "docling"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)


def extract_text_from_doc(doc):
    """Extract text from a Docling document (pages or elements)."""
    texts = []

    # Case 1: document has pages
    if hasattr(doc, "pages") and doc.pages:
        for page in doc.pages:
            if getattr(page, "text", None):
                texts.append((page.text, getattr(page, "page_number", None)))
            elif hasattr(page, "elements"):
                parts = [el.text for el in page.elements if getattr(el, "text", None)]
                if parts:
                    texts.append(("\n".join(parts), getattr(page, "page_number", None)))

    # Case 2: no pages, only elements
    elif hasattr(doc, "elements") and doc.elements:
        parts = [el.text for el in doc.elements if getattr(el, "text", None)]
        if parts:
            texts.append(("\n".join(parts), None))

    # Case 3: fallback to document.text
    elif getattr(doc, "text", None):
        texts.append((doc.text, None))

    return texts


def convert_documents(file_paths=None, urls=None):
    """
    Convert uploaded files and URLs into Docling documents.
    Stores results in LanceDB table 'docling' (appends, doesn't overwrite).
    """
    converter = DocumentConverter()
    docs = []

    # Connect to LanceDB
    db = lancedb.connect(DB_DIR)

    if TABLE_NAME in db.table_names():
        table = db.open_table(TABLE_NAME)
    else:
        # Create table if missing
        table = db.create_table(
            TABLE_NAME,
            data=[{"vector": [], "text": "", "metadata": {}}],
            mode="overwrite"
        )
        table.delete("1=1")  # remove dummy row

    # Convert files
    if file_paths:
        for filepath in file_paths:
            filename = os.path.basename(filepath)
            try:
                result = converter.convert(filepath)
                if result.document:
                    docs.append((filename, result.document))
            except Exception as e:
                print(f"❌ Error converting file {filename}: {e}")

    # Convert URLs
    if urls:
        for url in urls:
            try:
                result = converter.convert(url)
                if result.document:
                    docs.append((url, result.document))
            except Exception as e:
                print(f"❌ Error converting URL {url}: {e}")

    # Extract + store
    records = []
    for source_name, doc in docs:
        extracted_texts = extract_text_from_doc(doc)

        for text, page_number in extracted_texts:
            if not text.strip():
                continue

            metadata = {
                "filename": source_name,
                "page_numbers": [page_number] if page_number else [],
                "title": getattr(doc, "title", None),
            }
            records.append({"vector": [], "text": text, "metadata": metadata})

    if records:
        table.add(records)
        print(f"✅ Added {len(records)} chunks to {TABLE_NAME}")
    else:
        print("⚠️ No records extracted (doc may be empty).")

    return docs


# Example usage
if __name__ == "__main__":
    files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR)]
    urls = ["https://arxiv.org/pdf/2408.09869", "https://docling-project.github.io/docling/"]
    documents = convert_documents(files, urls)
    print(f"Converted {len(documents)} documents.")
