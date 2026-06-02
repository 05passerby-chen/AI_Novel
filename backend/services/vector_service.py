# backend/services/vector_service.py
# -*- coding: utf-8 -*-
"""ChromaDB vector store for character embeddings."""

import os
import chromadb
from chromadb.utils import embedding_functions
from services.llm_service import load_settings

VECTOR_DIR = os.path.expanduser("~/.ai_novel_editor_vectors")


def _get_embedding_function():
    """Create an embedding function. Tries DeepSeek API first, falls back to local."""
    settings = load_settings()
    try:
        # Try DeepSeek OpenAI-compatible embedding
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.deepseekApiKey or "sk-placeholder",
            api_base=settings.deepseekBaseUrl or "https://api.deepseek.com/v1",
            model_name="text-embedding-ada-002",
        )
    except Exception:
        pass

    try:
        # Fallback: local sentence-transformers
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    except Exception:
        pass

    # Last resort: use ChromaDB's default (all-MiniLM-L6-v2 via ONNX)
    return embedding_functions.DefaultEmbeddingFunction()


def get_collection(novel_id: str) -> chromadb.Collection:
    """Get or create a ChromaDB collection for this novel."""
    client = chromadb.PersistentClient(path=VECTOR_DIR)
    ef = _get_embedding_function()
    return client.get_or_create_collection(
        name=f"novel_{novel_id}",
        embedding_function=ef,
    )


def clear_collection(novel_id: str) -> None:
    """Delete and recreate the collection."""
    client = chromadb.PersistentClient(path=VECTOR_DIR)
    try:
        client.delete_collection(name=f"novel_{novel_id}")
    except Exception:
        pass


def index_characters(novel_id: str, characters: list[dict]) -> None:
    """Index character data into the vector store."""
    if not characters:
        return

    collection = get_collection(novel_id)

    ids = []
    documents = []
    metadatas = []

    for char in characters:
        # Build a rich text representation of the character
        doc_parts = [
            f"Name: {char.get('name', '')}",
            f"Classification: {char.get('classification', '')}",
        ]

        def _latest(entries: list, field: str) -> str:
            """Get the latest timeline entry value, or empty string."""
            if not entries:
                return ""
            sorted_entries = sorted(entries, key=lambda e: e.get("chapter", 0))
            return sorted_entries[-1].get("value", "") if sorted_entries else ""

        def _all_entries(entries: list, field: str) -> str:
            """Format all timeline entries as 'Ch.X: value | Ch.Y: value'."""
            if not entries:
                return ""
            parts = []
            for e in sorted(entries, key=lambda e: e.get("chapter", 0)):
                parts.append(f"Ch.{e.get('chapter', 0)}: {e.get('value', '')}")
            return " | ".join(parts)

        # Use the latest value for indexing (most representative)
        doc_parts.append(f"Occupation: {_latest(char.get('occupation', []), 'occupation')}")
        doc_parts.append(f"Personality: {_all_entries(char.get('personality', []), 'personality')}")
        doc_parts.append(f"Appearance: {_all_entries(char.get('appearance', []), 'appearance')}")
        doc_parts.append(f"Background: {_latest(char.get('background', []), 'background')}")
        doc_parts.append(f"Long-term Goals: {_latest(char.get('longTermGoals', []), 'longTermGoals')}")
        doc_parts.append(f"Short-term Goals: {_latest(char.get('shortTermGoals', []), 'shortTermGoals')}")
        doc_parts.append(f"Secrets: {_all_entries(char.get('secrets', []), 'secrets')}")
        doc_parts.append(f"Weaknesses: {_all_entries(char.get('weaknesses', []), 'weaknesses')}")

        # Add attitude information
        for att in char.get('attitudes', []):
            doc_parts.append(
                f"Attitude toward {att.get('targetId', '')}: "
                f"{att.get('initialAttitude', '')} → {att.get('resultingAttitude', '')} "
                f"(trigger: {att.get('triggerEvent', '')}, ch.{att.get('triggerChapter', 0)})"
            )

        # Add state timeline
        for state in char.get('stateTimeline', []):
            doc_parts.append(
                f"Ch.{state.get('chapter', 0)}: {state.get('status', '')} — {state.get('description', '')}"
            )

        doc_text = "\n".join(doc_parts)

        ids.append(f"char_{char.get('id', '')}")
        documents.append(doc_text)
        metadatas.append({
            "name": char.get("name", ""),
            "classification": char.get("classification", ""),
            "locked": char.get("locked", False),
        })

    # Upsert — overwrites existing entries with same IDs
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)


def query_characters(novel_id: str, query: str, k: int = 5) -> list[str]:
    """Query the vector store for relevant character context."""
    try:
        collection = get_collection(novel_id)
        results = collection.query(query_texts=[query], n_results=k)
        documents = results.get("documents", [[]])[0]
        return documents
    except Exception:
        return []


def build_context_for_chapter(novel_id: str, chapter_info: str) -> str:
    """Build a combined context string for AI chapter generation."""
    try:
        docs = query_characters(novel_id, chapter_info, k=10)
        if not docs:
            return ""

        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(f"--- Character Context {i+1} ---\n{doc}")

        return "\n\n".join(context_parts)
    except Exception:
        return ""
