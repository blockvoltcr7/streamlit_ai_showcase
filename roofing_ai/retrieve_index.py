from pinecone import Pinecone

pc = Pinecone(
    api_key="pcsk_6W336u_FhXNh62ENMCaU2nkqdE2c7szrrDMaJJSY7E9bVDKr2aP4j74ubWd3jnz4krpiKg"
)
index = pc.Index("n8n")
print(index)
# Retrieve and print all active indexes
active_indexes = pc.list_indexes()
print("Active Pinecone Indexes:")
for index in active_indexes:
    print(index)
