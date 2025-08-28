import os
import lancedb
from docling.document_converter import DocumentConverter
from utils.sitemap import get_sitemap_urls

UPLOAD_DIR = "data/uploads"
DB_DIR = "data/lancedb"
TABLE_NAME = "docling"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)


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
        # Create a table if it doesn’t exist yet
        table = db.create_table(
            TABLE_NAME,
            data=[{
                "vector": [],
                "text": "",
                "metadata": {}
            }],
            mode="overwrite"
        )
        # Remove the dummy row after creation
        table.delete("1=1")

    # Convert uploaded files
    if file_paths:
        for filepath in file_paths:
            filename = os.path.basename(filepath)
            try:
                result = converter.convert(filepath)
                if result.document:
                    docs.append((filename, result.document))
            except Exception as e:
                print(f"Error converting file {filename}: {e}")

    # Convert URLs
    if urls:
        for url in urls:
            try:
                result = converter.convert(url)
                if result.document:
                    docs.append((url, result.document))
            except Exception as e:
                print(f"Error converting URL {url}: {e}")

    # Store in LanceDB
    records = []
    for source_name, doc in docs:
        for page in doc.pages:
            # ✅ FIX: Access page.text instead of page.get_text()
            text = getattr(page, "text", "") or ""
            if not text.strip():
                continue
            metadata = {
                "filename": source_name,
                "page_numbers": [getattr(page, "page_number", None)],
                "title": getattr(page, "title", None),
            }
            records.append({
                "vector": [],  # placeholder for step2
                "text": text,
                "metadata": metadata,
            })

    if records:
        table.add(records)
        print(f"✅ Added {len(records)} chunks to {TABLE_NAME}")
    else:
        print("⚠️ No records extracted.")

    return docs


# Example usage
if __name__ == "__main__":
    files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR)]
    urls = ["https://arxiv.org/pdf/2408.09869", "https://docling-project.github.io/docling/"]
    documents = convert_documents(files, urls)
    print(f"Converted {len(documents)} documents.")
