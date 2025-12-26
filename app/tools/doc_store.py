import os
from typing import List
from uuid import uuid4

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from pypdf import PdfReader

from app.config import settings
from app.models import DocumentChunk


# Initialize Chroma persistent client
_chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

# _embedding_function = SentenceTransformerEmbeddingFunction(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

_embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

_collection = _chroma_client.get_or_create_collection(
    name="research_docs",
    embedding_function=_embedding_function,
)


def _index_pdf_file(doc_id: str, source: str, local_path: str) -> None:
    """Extract text from PDF pages and index into Chroma"""
    reader = PdfReader(local_path)
    texts: List[str] = []
    ids: List[str] = []
    metadatas: List[dict] = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue

        chunk_id = f"{doc_id}_page_{i}"

        texts.append(text)
        ids.append(chunk_id)
        metadatas.append({
            "doc_id": doc_id,
            "source": source,
            "page": i
        })

    if texts:
        _collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas,
        )


def sync_local_docs(folder_path: str) -> None:
    """
    Load PDF files from a local directory and index into Chroma.
    Call once on startup.

    Example:
    sync_local_docs("./data/docs")
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Document folder not found: {folder_path}")

    for file in os.listdir(folder_path):
        if not file.lower().endswith(".pdf"):
            continue

        doc_path = os.path.join(folder_path, file)
        doc_id = str(uuid4())

        _index_pdf_file(
            doc_id=doc_id,
            source=file,
            local_path=doc_path,
        )

    _chroma_client.persist()


def query_docs(query: str, n_results: int = 10) -> List[DocumentChunk]:
    """Embed + retrieve matched chunks with metadata"""
    res = _collection.query(query_texts=[query], n_results=n_results)
    docs = res.get("documents", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]

    chunks: List[DocumentChunk] = []

    for text, meta in zip(docs, metadatas):
        chunks.append(
            DocumentChunk(
                doc_id=meta["doc_id"],
                source=meta["source"],
                page=meta["page"],
                text=text[:2000],  # trim chunk for quality
            )
        )

    return chunks
