"""Tests for data models."""

from mcp_keda_documentation.models import Document, DocumentMetadata, SearchResult


def test_document_metadata_creation() -> None:
    """Test creating a DocumentMetadata instance."""
    metadata = DocumentMetadata(
        title="Apache Kafka",
        description="Scale applications based on Apache Kafka topic lag",
        license="MIT",
    )
    assert metadata.title == "Apache Kafka"
    assert metadata.description == "Scale applications based on Apache Kafka topic lag"
    assert metadata.license == "MIT"


def test_document_metadata_optional_fields() -> None:
    """Test DocumentMetadata with optional fields."""
    metadata = DocumentMetadata(title="ScaledObject")
    assert metadata.title == "ScaledObject"
    assert metadata.description is None
    assert metadata.license is None


def test_document_creation() -> None:
    """Test creating a Document instance."""
    doc = Document(
        path="docs/2.16/scalers/apache-kafka.md",
        title="Apache Kafka",
        description="Scale applications based on Apache Kafka topic lag",
        section="docs",
        content="# Apache Kafka\n\nContent here",
        url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
    )
    assert doc.path == "docs/2.16/scalers/apache-kafka.md"
    assert doc.title == "Apache Kafka"
    assert doc.section == "docs"
    assert "Content here" in doc.content


def test_search_result_creation() -> None:
    """Test creating a SearchResult instance."""
    result = SearchResult(
        path="docs/2.16/scalers/apache-kafka.md",
        title="Apache Kafka",
        url="https://keda.sh/docs/2.16/scalers/apache-kafka/",
        snippet="...apache kafka topic lag...",
        score=12.5,
        section="docs",
    )
    assert result.path == "docs/2.16/scalers/apache-kafka.md"
    assert result.score == 12.5
    assert result.section == "docs"
