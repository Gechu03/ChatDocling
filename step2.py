from docling.chunking import HybridChunker
from utils.tokenizer import OpenAITokenizerWrapper

MAX_TOKENS = 8191  # text-embedding-3-large max tokens

def chunk_documents(documents):
    """
    Receives a list of tuples: (source_name, document)
    Returns a list of tuples: (source_name, chunk)
    """
    tokenizer = OpenAITokenizerWrapper()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=MAX_TOKENS, merge_peers=True)
    all_chunks = []

    for source_name, document in documents:
        try:
            chunk_iter = chunker.chunk(dl_doc=document)
            for chunk in chunk_iter:
                all_chunks.append((source_name, chunk))
        except Exception as e:
            print(f"Error chunking {source_name}: {e}")

    return all_chunks

# Example usage
if __name__ == "__main__":
    from step1 import convert_documents
    files = ["data/uploads/example.pdf"]
    documents = convert_documents(files)
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")
