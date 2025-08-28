import os
from docling.document_converter import DocumentConverter
from utils.sitemap import get_sitemap_urls

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_documents(file_paths=None, urls=None):
    """
    Convert uploaded files and URLs into Docling documents.
    Returns list of tuples: (source_name, document)
    """
    converter = DocumentConverter()
    docs = []

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

    return docs

# Example usage
if __name__ == "__main__":
    files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR)]
    urls = ["https://arxiv.org/pdf/2408.09869", "https://docling-project.github.io/docling/"]
    documents = convert_documents(files, urls)
    print(f"Converted {len(documents)} documents.")
