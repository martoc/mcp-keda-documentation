"""Tests for document parser."""

import tempfile
from pathlib import Path

import toml

from mcp_keda_documentation.parser import DocumentParser


def test_extract_section_root() -> None:
    """Test extracting section from root-level file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("_index.md"))
    assert section == "root"


def test_extract_section_nested() -> None:
    """Test extracting section from nested file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("docs/2.16/scalers/apache-kafka.md"))
    assert section == "docs"


def test_compute_url_regular_file() -> None:
    """Test computing documentation URL for a regular file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("docs/2.16/scalers/apache-kafka.md"))
    assert url == "https://keda.sh/docs/2.16/scalers/apache-kafka/"


def test_compute_url_index_file() -> None:
    """Test computing URL for an _index.md file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("docs/2.16/scalers/_index.md"))
    assert url == "https://keda.sh/docs/2.16/scalers/"


def test_compute_url_root_index() -> None:
    """Test computing URL for root _index.md."""
    parser = DocumentParser()
    url = parser._compute_url(Path("_index.md"))
    assert url == "https://keda.sh/"


def test_clean_content_removes_hugo_shortcodes() -> None:
    """Test cleaning content removes Hugo shortcode tags."""
    parser = DocumentParser()
    content = "{{< note >}}\nThis is a note.\n{{< /note >}}\nRegular content."
    cleaned = parser._clean_content(content)
    assert "{{<" not in cleaned
    assert "This is a note." in cleaned
    assert "Regular content." in cleaned


def test_clean_content_removes_html_comments() -> None:
    """Test cleaning content removes HTML comments."""
    parser = DocumentParser()
    content = "<!-- Comment -->\nContent\n<!-- Another -->"
    cleaned = parser._clean_content(content)
    assert "<!--" not in cleaned
    assert "Content" in cleaned


def test_clean_content_removes_html_tags() -> None:
    """Test cleaning content removes HTML tags."""
    parser = DocumentParser()
    content = "<div>Some content</div><br/>More content"
    cleaned = parser._clean_content(content)
    assert "<div>" not in cleaned
    assert "Some content" in cleaned
    assert "More content" in cleaned


def test_parse_file_with_toml_frontmatter() -> None:
    """Test parsing a file with TOML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test.md"

        content = """+++
title = "Apache Kafka"
description = "Scale applications based on Apache Kafka topic lag"
+++

# Apache Kafka

This is a test.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Apache Kafka"
        assert doc.description == "Scale applications based on Apache Kafka topic lag"
        assert "Apache Kafka" in doc.content
        assert doc.path == "test.md"


def test_parse_file_without_frontmatter() -> None:
    """Test parsing a file without TOML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test-file.md"

        content = "# Test Content\n\nThis is a test."
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Test File"  # Fallback from filename
        assert "Test Content" in doc.content


def test_extract_faq_version_latest() -> None:
    """Test extracting version from plain 'faq' filename."""
    parser = DocumentParser()
    version = parser._extract_faq_version("faq")
    assert version == "latest"


def test_extract_faq_version_simple() -> None:
    """Test extracting version from 'faq20' filename."""
    parser = DocumentParser()
    version = parser._extract_faq_version("faq20")
    assert version == "2.0"


def test_extract_faq_version_underscore() -> None:
    """Test extracting version from 'faq2_14' filename."""
    parser = DocumentParser()
    version = parser._extract_faq_version("faq2_14")
    assert version == "2.14"


def test_parse_toml_faq_file() -> None:
    """Test parsing a TOML FAQ file with QnA entries."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True)

        faq_data = {
            "qna": [
                {
                    "q": "What is KEDA?",
                    "a": "KEDA stands for Kubernetes Event-driven Autoscaling.",
                },
                {
                    "q": "How does KEDA work?",
                    "a": "KEDA acts as a Kubernetes metrics server.",
                },
            ]
        }

        faq_file = data_dir / "faq.toml"
        with open(faq_file, "w") as f:
            toml.dump(faq_data, f)

        documents = parser.parse_toml_file(faq_file, repo_root)
        assert len(documents) == 2
        assert documents[0].title == "What is KEDA?"
        assert documents[0].section == "faq"
        assert documents[0].url == "https://keda.sh/docs/latest/faq/"
        assert "KEDA stands for" in documents[0].content
        assert documents[0].path == "data/faq.toml#what-is-keda"


def test_parse_toml_faq_file_with_version() -> None:
    """Test parsing a versioned TOML FAQ file."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True)

        faq_data = {
            "qna": [
                {
                    "q": "What is KEDA?",
                    "a": "KEDA is a Kubernetes-based event driven autoscaler.",
                }
            ]
        }

        faq_file = data_dir / "faq2_14.toml"
        with open(faq_file, "w") as f:
            toml.dump(faq_data, f)

        documents = parser.parse_toml_file(faq_file, repo_root)
        assert len(documents) == 1
        assert documents[0].url == "https://keda.sh/docs/2.14/faq/"


def test_parse_toml_faq_file_empty_qna() -> None:
    """Test parsing a TOML FAQ file with empty QnA list."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True)

        faq_data: dict[str, list[object]] = {"qna": []}

        faq_file = data_dir / "faq.toml"
        with open(faq_file, "w") as f:
            toml.dump(faq_data, f)

        documents = parser.parse_toml_file(faq_file, repo_root)
        assert len(documents) == 0


def test_parse_toml_file_produces_multiple_documents() -> None:
    """Test that parse_toml_file produces multiple documents from one TOML file."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True)

        faq_data = {
            "qna": [
                {
                    "q": "What is KEDA?",
                    "a": "KEDA is an autoscaler.",
                },
                {
                    "q": "How do I install KEDA?",
                    "a": "Use Helm or YAML manifests.",
                },
                {
                    "q": "What scalers are available?",
                    "a": "KEDA supports many scalers.",
                },
            ]
        }

        faq_file = data_dir / "faq20.toml"
        with open(faq_file, "w") as f:
            toml.dump(faq_data, f)

        documents = parser.parse_toml_file(faq_file, repo_root)
        assert len(documents) == 3
        assert documents[0].path == "data/faq20.toml#what-is-keda"
        assert documents[1].path == "data/faq20.toml#how-do-i-install-keda"
        assert documents[2].path == "data/faq20.toml#what-scalers-are-available"
        assert all(d.url == "https://keda.sh/docs/2.0/faq/" for d in documents)
