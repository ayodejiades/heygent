"""
indexer.py
----------
Handles embedding Yelp businesses into a ChromaDB vector store.
Provides semantic retrieval capabilities using a pure-python LSA (TF-IDF + SVD)
embedding function to prevent native PyTorch/ONNX library load failures.
"""

import json
import os
import pickle
import chromadb
from typing import List, Dict, Any
from chromadb import EmbeddingFunction
from chromadb.api.types import Documents, Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "lsa_model.pkl")

DEFAULT_CORPUS = [
    "Nigerian African Restaurants Lagos Suya Mama Cass Spice Garden",
    "Italian Pizza Pasta Restaurants Lagos Pizza Place",
    "Chinese Noodles Rice Restaurants Lagos",
    "American Burgers Fries Fast Food Restaurants Lagos",
    "Cafe Coffee Tea Breakfast Lagos",
    "Suya Street Food Spicy Meat Lagos",
    "Bar Club Nightlife Drinks Lagos",
    "Spicy local food traditional African soup",
    "Quiet cafe study workspace coffee pastry",
    "Fast food burgers quick bite dinner"
]

class LSAEmbeddingFunction(EmbeddingFunction):
    """
    Pure Python LSA-based embedding function.
    Eliminates heavy native C++ dependencies like PyTorch and ONNX.
    """
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.vectorizer = None
        self.svd = None
        self.load_or_fit_default()

    @classmethod
    def name(cls) -> str:
        return "LSAEmbeddingFunction"

    def load_or_fit_default(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.vectorizer = data["vectorizer"]
                    self.svd = data["svd"]
                return
            except Exception as e:
                print(f"Warning: Failed to load LSA model: {e}. Fitting default.")
        
        # Fallback default fitting
        self.vectorizer = TfidfVectorizer(stop_words='english')
        X = self.vectorizer.fit_transform(DEFAULT_CORPUS)
        self.svd = TruncatedSVD(n_components=min(16, X.shape[1]))
        self.svd.fit(X)

    def fit_and_save(self, documents: List[str]):
        """Fit the TF-IDF and SVD models on the actual database documents and save to disk."""
        self.vectorizer = TfidfVectorizer(stop_words='english')
        X = self.vectorizer.fit_transform(documents)
        # Use 128 dimensions for rich semantic capture, or less if database is tiny
        n_components = min(128, X.shape[1] - 1)
        if n_components < 2:
            n_components = 1
        self.svd = TruncatedSVD(n_components=n_components)
        self.svd.fit(X)
        
        # Save to disk
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "svd": self.svd
            }, f)

    def __call__(self, input: Documents) -> Embeddings:
        # Convert documents to LSA vectors
        X = self.vectorizer.transform(input)
        vectors = self.svd.transform(X)
        return vectors.tolist()


class BusinessIndexer:
    def __init__(self, db_path: str = DB_PATH):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Initialize LSA embedding function
        self.embedding_fn = LSAEmbeddingFunction()
        
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
        
        attrs = business.get("attributes", {})
        attr_str = ", ".join([f"{k}: {v}" for k, v in attrs.items() if v])
        
        doc = f"Name: {name}\nCategories: {categories}\nCity: {city}\nAttributes: {attr_str}"
        return doc

    def index_businesses(self, businesses: List[Dict[str, Any]], batch_size: int = 100):
        """Index a list of business dictionaries."""
        docs = []
        for biz in businesses:
            docs.append(self._format_document(biz))

        if not docs:
            return

        # Fit and save LSA model first to ensure optimal vectors
        self.embedding_fn.fit_and_save(docs)
        
        # Re-initialize collection to use the newly fitted embedding function
        self.collection = self.client.get_or_create_collection(
            name="yelp_businesses",
            embedding_function=self.embedding_fn
        )

        metadatas = []
        ids = []
        current_docs = []

        for i, biz in enumerate(businesses):
            doc = self._format_document(biz)
            current_docs.append(doc)
            
            safe_meta = {
                "name": biz.get("name", ""),
                "city": biz.get("city", ""),
                "categories": biz.get("categories", ""),
                "stars": float(biz.get("stars", 0)),
                "raw_json": json.dumps(biz)
            }
            metadatas.append(safe_meta)
            ids.append(biz.get("business_id", f"biz_{i}"))

            if len(current_docs) >= batch_size:
                self.collection.upsert(
                    documents=current_docs,
                    metadatas=metadatas,
                    ids=ids
                )
                current_docs, metadatas, ids = [], [], []

        # Index remaining
        if current_docs:
            self.collection.upsert(
                documents=current_docs,
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
        
        candidates = []
        if results and results['metadatas'] and results['metadatas'][0]:
            for meta in results['metadatas'][0]:
                try:
                    biz = json.loads(meta["raw_json"])
                    candidates.append(biz)
                except json.JSONDecodeError:
                    pass
        return candidates
