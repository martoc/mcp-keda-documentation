"""Tests for database operations."""

import tempfile
from pathlib import Path

from mcp_keda_documentation.database import DocumentDatabase
from mcp_keda_documentation.models import Document


def test_database_initialisation() -> None:
    """Test database initialisation creates schema."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)
        assert db.db_path == db_path
        assert db_path.exists()


def test_upsert_document() -> None:
    """Test inserting and updating a document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="docs/2.16/scalers/apache-kafka.md",
            title="Apache Kafka",
            description="Scale based on Kafka topic lag",
            section="docs",
            content="Content about Apache Kafka scaler",
            url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
        )

        db.upsert_document(doc)
        retrieved = db.get_document("docs/2.16/scalers/apache-kafka.md")

        assert retrieved is not None
        assert retrieved.title == "Apache Kafka"
        assert retrieved.content == "Content about Apache Kafka scaler"


def test_upsert_document_update() -> None:
    """Test updating an existing document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="docs/2.16/scalers/apache-kafka.md",
            title="Original",
            description=None,
            section="docs",
            content="Original content",
            url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
        )
        db.upsert_document(doc1)

        doc2 = Document(
            path="docs/2.16/scalers/apache-kafka.md",
            title="Updated",
            description=None,
            section="docs",
            content="Updated content",
            url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
        )
        db.upsert_document(doc2)

        retrieved = db.get_document("docs/2.16/scalers/apache-kafka.md")
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "Updated content"


def test_search_documents() -> None:
    """Test searching documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="Apache Kafka Scaler",
            description="Kafka scaler guide",
            section="docs",
            content="This document covers the Apache Kafka scaler for KEDA",
            url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
        )
        doc2 = Document(
            path="doc2.md",
            title="Prometheus Scaler",
            description="Prometheus scaler guide",
            section="docs",
            content="This document covers the Prometheus scaler for KEDA",
            url="https://keda.sh/docs/2.16/scalers/prometheus/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("kafka")
        assert len(results) > 0
        assert any("Kafka" in r.title for r in results)


def test_search_with_section_filter() -> None:
    """Test searching with section filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="KEDA Scalers",
            description=None,
            section="docs",
            content="Documentation about KEDA scalers",
            url="https://keda.sh/docs/2.16/scalers/",
        )
        doc2 = Document(
            path="doc2.md",
            title="KEDA Blog Post",
            description=None,
            section="blog",
            content="Blog post about KEDA features",
            url="https://keda.sh/blog/post/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("KEDA", section="docs")
        assert len(results) == 1
        assert results[0].section == "docs"


def test_get_document_not_found() -> None:
    """Test getting a non-existent document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        result = db.get_document("nonexistent.md")
        assert result is None


def test_clear_database() -> None:
    """Test clearing all documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="test.md",
            title="Test",
            description=None,
            section="docs",
            content="Content",
            url="https://keda.sh/docs/test/",
        )
        db.upsert_document(doc)

        assert db.get_document_count() == 1

        db.clear()

        assert db.get_document_count() == 0


def test_get_document_count() -> None:
    """Test getting document count."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        assert db.get_document_count() == 0

        for i in range(5):
            doc = Document(
                path=f"doc{i}.md",
                title=f"Doc {i}",
                description=None,
                section="docs",
                content=f"Content {i}",
                url=f"https://keda.sh/docs/doc{i}/",
            )
            db.upsert_document(doc)

        assert db.get_document_count() == 5
