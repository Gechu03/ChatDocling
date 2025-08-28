import streamlit as st
import lancedb
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Initialize LanceDB connection
@st.cache_resource
def init_db():
    """Initialize database connection."""
    db = lancedb.connect("data/lancedb")
    return db.open_table("docling")


def get_context(query: str, table, num_results: int = 5) -> str:
    """Search the database for relevant context."""
    results = table.search(query).limit(num_results).to_pandas()
    contexts = []

    for _, row in results.iterrows():
        filename = row["metadata"]["filename"]
        page_numbers = row["metadata"]["page_numbers"]
        title = row["metadata"]["title"]

        # Build source citation safely
        source_parts = []
        if filename:
            source_parts.append(filename)
        if page_numbers is not None and len(page_numbers) > 0:
            page_list = list(page_numbers)  # in case it's a numpy array
            source_parts.append(f"p. {', '.join(str(p) for p in page_list)}")

        source = f"\nSource: {' - '.join(source_parts)}"
        if title:
            source += f"\nTitle: {title}"

        contexts.append(f"{row['text']}{source}")

    return "\n\n".join(contexts)


def get_chat_response(messages, context: str) -> str:
    """Get structured response (Answer + Sources + Reasoning) from OpenAI API."""
    system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.

    Always respond with three sections:

    **Answer** – a clear reply to the user’s question.  
    **Sources** – list the filenames and page numbers where the information was found.  
    **Reasoning** – describe your reasoning:  
    - Restate the user’s question,  
    - Mention the relevant text snippets you found,  
    - Explain how you connected those snippets to form the answer.  

    Do NOT summarize the law itself. Instead, explain how you reasoned from the retrieved text to answer the question.

    Context:
    {context}
    """

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_with_context,
        temperature=0.7,
        stream=True,
    )

    response = st.write_stream(stream)
    return response


def run_chat_app():
    """Main function to run the chat interface."""
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize database connection
    table = init_db()

    st.header("📚 Chat with your documents")

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the document"):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.status("Searching document...", expanded=False) as status:
            context = get_context(prompt, table)

            st.markdown(
                """
                <style>
                .search-result {
                    margin: 10px 0;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #f0f2f6;
                }
                .search-result summary {
                    cursor: pointer;
                    color: #0f52ba;
                    font-weight: 500;
                }
                .search-result summary:hover {
                    color: #1e90ff;
                }
                .metadata {
                    font-size: 0.9em;
                    color: #666;
                    font-style: italic;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.write("Found relevant sections:")
            for chunk in context.split("\n\n"):
                parts = chunk.split("\n")
                text = parts[0]
                metadata = {
                    line.split(": ")[0]: line.split(": ")[1]
                    for line in parts[1:]
                    if ": " in line
                }

                source = metadata.get("Source", "Unknown source")
                title = metadata.get("Title", "Untitled section")

                st.markdown(
                    f"""
                    <div class="search-result">
                        <details>
                            <summary>{source}</summary>
                            <div class="metadata">Section: {title}</div>
                            <div style="margin-top: 8px;">{text}</div>
                        </details>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with st.chat_message("assistant"):
            response = get_chat_response(st.session_state.messages, context)

        st.session_state.messages.append({"role": "assistant", "content": response})
