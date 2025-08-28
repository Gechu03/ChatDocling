import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from typing import List

def store_chunks_in_lancedb(all_chunks, db_path="data/lancedb"):
    """
    Store processed chunks in LanceDB
    all_chunks: list of tuples (source_name, chunk)
    """
    db = lancedb.connect(db_path)
    func = get_registry().get("openai").create(name="text-embedding-3-large")

    # Metadata schema
    class ChunkMetadata(LanceModel):
        filename: str | None
        page_numbers: List[int] | None
        title: str | None

    class Chunks(LanceModel):
        text: str = func.SourceField()
        vector: Vector(func.ndims()) = func.VectorField()
        metadata: ChunkMetadata

    table = db.create_table("docling", schema=Chunks, mode="overwrite")

    processed_chunks = []
    for source_name, chunk in all_chunks:
        metadata = {
            "filename": source_name,
            "page_numbers": [
                page_no
                for page_no in sorted(
                    set(prov.page_no for item in chunk.meta.doc_items for prov in item.prov)
                )
            ] or None,
            "title": chunk.meta.headings[0] if chunk.meta.headings else None
        }
        processed_chunks.append({"text": chunk.text, "metadata": metadata})

    table.add(processed_chunks)
    print(f"Stored {len(processed_chunks)} chunks in LanceDB.")
    return table

# Example usage
if __name__ == "__main__":
    from step1 import convert_documents
    from step2 import chunk_documents

    files = ["data/uploads/example.pdf"]
    docs = convert_documents(files)
    chunks = chunk_documents(docs)
    table = store_chunks_in_lancedb(chunks)
    print(f"Total rows in table: {table.count_rows()}")
