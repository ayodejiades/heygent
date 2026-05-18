"""
indexer.py
----------
Handles embedding Yelp businesses into a ChromaDB vector store.
Provides semantic retrieval capabilities for the LangGraph agent.
"""

import json
import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

# Use a lightweight sentence-transformer model that runs fine on CPU
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

class BusinessIndexer:
    def __init__(self, db_path: str = DB_PATH):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use sentence-transformers for embedding
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="yelp_businesses",
            embedding_function=self.embedding_fn
        )

    def _format_document(self, business: Dict[str, Any]) -> str:
        """Format a business into a rich text document for embedding."""
        name = business.get("name", "")
        categories = business.get("categories", "")
        city = business.get("city", "")
        
        # Serialize attributes nicely
        attrs = business.get("attributes", {})
        attr_str = ", ".join([f"{k}: {v}" for k, v in attrs.items() if v])
        
        doc = f"Name: {name}\nCategories: {categories}\nCity: {city}\nAttributes: {attr_str}"
        return doc

    def index_businesses(self, businesses: List[Dict[str, Any]], batch_size: int = 100):
        """Index a list of business dictionaries."""
        docs = []
        metadatas = []
        ids = []

        for i, biz in enumerate(businesses):
            doc = self._format_document(biz)
            docs.append(doc)
            
            # Store full item JSON as a string in metadata for easy retrieval
            # We remove large/nested objects if they break Chroma, but dicts are mostly flat here
            safe_meta = {
                "name": biz.get("name", ""),
                "city": biz.get("city", ""),
                "categories": biz.get("categories", ""),
                "stars": float(biz.get("stars", 0)),
                "raw_json": json.dumps(biz)
            }
            metadatas.append(safe_meta)
            ids.append(biz.get("business_id", f"biz_{i}"))

            if len(docs) >= batch_size:
                self.collection.upsert(
                    documents=docs,
                    metadatas=metadatas,
                    ids=ids
                )
                docs, metadatas, ids = [], [], []

        # Index remaining
        if docs:
            self.collection.upsert(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            
    def retrieve(self, query: str, n_results: int = 20) -> List[Dict[str, Any]]:
        """Retrieve top N most semantically similar businesses."""
        if self.collection.count() == 0:
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Parse back the raw JSON from metadata
        candidates = []
        if results and results['metadatas'] and results['metadatas'][0]:
            for meta in results['metadatas'][0]:
                try:
                    biz = json.loads(meta["raw_json"])
                    candidates.append(biz)
                except json.JSONDecodeError:
                    pass
        return candidates
