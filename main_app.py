import os
import streamlit as st
from chat_app import run_chat_app
from step1 import convert_documents
from step2 import chunk_documents
from step3 import store_chunks_in_lancedb

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📚 Document Q&A App")

page = st.sidebar.selectbox(
    "Choose a page", ["Upload & Preprocess", "Chat"], key="main_page_select"
)

if page == "Upload & Preprocess":
    st.header("Upload your files and preprocess")

    uploaded_files = st.file_uploader(
        "Upload your documents", type=["pdf", "html", "txt"], accept_multiple_files=True
    )

    urls_input = st.text_area(
        "Or enter URLs (one per line)"
    )

    if uploaded_files or urls_input:
        files_to_process = []
        if uploaded_files:
            for f in uploaded_files:
                path = os.path.join(UPLOAD_DIR, f.name)
                with open(path, "wb") as out_file:
                    out_file.write(f.read())
                files_to_process.append(path)

        urls_to_process = [u.strip() for u in urls_input.split("\n") if u.strip()]

        if st.button("Run preprocessing"):
            st.info("Running preprocessing... This may take a while.")

            # Step 1: Convert
            documents = convert_documents(file_paths=files_to_process, urls=urls_to_process)
            st.success(f"Converted {len(documents)} documents.")

            # Step 2: Chunk
            chunks = chunk_documents(documents)
            st.success(f"Created {len(chunks)} chunks.")

            # Step 3: Store in LanceDB
            table = store_chunks_in_lancedb(chunks)
            st.success(f"Stored chunks in LanceDB! Total rows: {table.count_rows()}")

elif page == "Chat":
    run_chat_app()
