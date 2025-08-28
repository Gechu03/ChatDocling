import lancedb
from dotenv import load_dotenv
load_dotenv() 
# --------------------------------------------------------------
# Connect to the database
# --------------------------------------------------------------

uri = "data/lancedb"
db = lancedb.connect(uri)


# --------------------------------------------------------------
# Load the table
# --------------------------------------------------------------

table = db.open_table("docling")


# --------------------------------------------------------------
# Search the table
# --------------------------------------------------------------

result = table.search(query="what's docling?", query_type="vector").limit(3)
print(result.to_pandas())
