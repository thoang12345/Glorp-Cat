from Functions.tool import Tool
from Functions.Model.config import CHROMADB_PATH, RERANKER_MODEL
import chromadb
from sentence_transformers import CrossEncoder

client = chromadb.PersistentClient(path=CHROMADB_PATH)
model = CrossEncoder(RERANKER_MODEL)

class QueryCollection(Tool):
    def __init__(self):
        super().__init__(
            "query_collection",
            "Searches a specific ChromaDB knowledge collection for information relevant to a user's request and returns the highest-ranked passages with their metadata. Use this tool when the answer is likely to be contained in the user's stored documents. If the appropriate collection is unknown, first call get_collections to discover available collections and select the most relevant one. If you feel like you don't immediately have the answer try querying a database."
        )

    def schema(self):
        return {
            "type" : "function",
            "function" : {
                "name" : self.name,
                "description" : self.description,
                "parameters" : {
                    "type" : "object",
                    "properties" : {
                        "collection_name" : {
                            "type" : "string",
                            "description" : "name of a chromaDB collection. Unless told otherwise, call get_collections tool to get name of collections."
                        },
                        "query" : {
                            "type" : "string",
                            "description" : "query for the collection within database"
                        }
                    },
                    "required" : ["collection_name", "query"]
                }
            }
        }

    def _get_Collection(self, collection_name):
        collection = client.get_collection(name=collection_name)
        return collection

    def _rerank(self, query, documents, metadatas):
        pairs = [
            [query, document]
            for document in documents
        ]

        scores = model.predict(pairs)

        scored_documents = [
            {
                "text": document,
                "metadata": metadata,
                "score": float(score)
            }
            for document, metadata, score in zip(
                documents,
                metadatas,
                scores
            )
        ]

        return sorted(
            scored_documents,
            key=lambda x: x["score"],
            reverse=True
        )[:10]

    async def execute(self, collection_name, query):
        collection = self._get_Collection(collection_name)

        results = collection.query(
            query_texts=[query],
            n_results=20
        )

        try:
            reranked_results = self._rerank(...)
        except Exception:
            # Fall back to Chroma ordering
            reranked_results = [
                {
                    "text": text,
                    "metadata": metadata,
                    "score": None,
                }
                for text, metadata in zip(
                    results["documents"][0],
                    results["metadatas"][0] or [{}] * len(results["documents"][0])
                )
            ][:10]

        llm_payload = {
            "query": query,
            "total_returned": len(reranked_results),
            "results": [
                {
                    "rank": rank,
                    "score": item["score"],
                    "text": item["text"],
                    "metadata": item["metadata"]
                }
                for rank, item in enumerate(reranked_results, start=1)
            ]
        }

        return llm_payload
