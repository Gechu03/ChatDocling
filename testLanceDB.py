import lancedb

# Open your table
db = lancedb.connect("data/lancedb")
table = db.open_table("docling")

# Convert to a pandas DataFrame for easy inspection
df = table.to_pandas()

# Show first few chunks
for i, row in df.head(20).iterrows():
    print(f"Chunk {i+1}")
    print("Filename:", row['metadata']['filename'])
    print("Page numbers:", row['metadata']['page_numbers'])
    print("Title/Heading:", row['metadata']['title'])
    print("Text snippet:", row['text'][:500])  # first 500 characters
    print("-"*80)