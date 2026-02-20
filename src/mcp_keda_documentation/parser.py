"""Parser for KEDA documentation markdown and TOML files."""

import re
from pathlib import Path

import frontmatter  # type: ignore[import-untyped]
import toml
from frontmatter.default_handlers import TOMLHandler  # type: ignore[import-untyped]

from mcp_keda_documentation.models import Document, DocumentMetadata


class DocumentParser:
    """Parses markdown files with TOML frontmatter and TOML data files."""

    KEDA_DOCS_BASE_URL = "https://keda.sh"

    def parse_file(self, file_path: Path, base_path: Path) -> Document | None:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to the markdown file.
            base_path: Base path of the documentation directory.

        Returns:
            Document instance or None if parsing fails.
        """
        try:
            post = frontmatter.load(file_path, handler=TOMLHandler())
            metadata = self._extract_metadata(post.metadata, file_path)
            relative_path = file_path.relative_to(base_path)
            section = self._extract_section(relative_path)
            url = self._compute_url(relative_path)
            content = self._clean_content(post.content)

            return Document(
                path=str(relative_path),
                title=metadata.title,
                description=metadata.description,
                section=section,
                content=content,
                url=url,
            )
        except Exception:
            return None

    def parse_toml_file(self, file_path: Path, base_path: Path) -> list[Document]:
        """Parse a TOML FAQ data file and extract documents.

        Supports FAQ files containing [[qna]] arrays.

        Args:
            file_path: Path to the TOML file.
            base_path: Base path of the repository root.

        Returns:
            List of Document instances extracted from the TOML data.
        """
        try:
            with open(file_path) as f:
                data = toml.load(f)

            if not isinstance(data, dict):
                return []

            relative_path = file_path.relative_to(base_path)
            relative_str = str(relative_path)

            qna = data.get("qna")
            if isinstance(qna, list):
                version = self._extract_faq_version(file_path.stem)
                return self._parse_faq_entries(qna, relative_str, version)

            return []
        except Exception:
            return []

    def _extract_faq_version(self, stem: str) -> str:
        """Extract version string from FAQ filename stem.

        Args:
            stem: Filename without extension (e.g., 'faq', 'faq20', 'faq2_14').

        Returns:
            Version string (e.g., 'latest', '2.0', '2.14').
        """
        # Remove the 'faq' prefix
        version_part = stem.removeprefix("faq")

        if not version_part:
            return "latest"

        # Handle underscore-separated versions like 'faq2_14' -> '2.14'
        if "_" in version_part:
            parts = version_part.split("_", 1)
            return f"{parts[0]}.{parts[1]}"

        # Handle simple versions like 'faq20' -> '2.0'
        if len(version_part) >= 2:
            return f"{version_part[0]}.{version_part[1:]}"

        return version_part

    def _parse_faq_entries(self, qna: list[object], file_path: str, version: str) -> list[Document]:
        """Parse FAQ QnA entries into documents.

        Each QnA entry becomes a separate document.

        Args:
            qna: List of QnA dictionaries with 'q' and 'a' keys.
            file_path: Relative path to the TOML file.
            version: KEDA version string for URL generation.

        Returns:
            List of Document instances for each QnA entry.
        """
        documents: list[Document] = []

        for entry in qna:
            if not isinstance(entry, dict):
                continue

            question = entry.get("q")
            answer = entry.get("a")

            if not isinstance(question, str) or not isinstance(answer, str):
                continue

            # Sanitise question for use as fragment identifier
            fragment = re.sub(r"[^a-zA-Z0-9-]", "-", question.lower()).strip("-")
            fragment = re.sub(r"-+", "-", fragment)

            lines = [
                question,
                "",
                answer,
            ]

            if version == "latest":
                url = f"{self.KEDA_DOCS_BASE_URL}/docs/latest/faq/"
            else:
                url = f"{self.KEDA_DOCS_BASE_URL}/docs/{version}/faq/"

            documents.append(
                Document(
                    path=f"{file_path}#{fragment}",
                    title=question,
                    description=None,
                    section="faq",
                    content="\n".join(lines),
                    url=url,
                )
            )

        return documents

    def _extract_metadata(self, metadata: dict[str, object], file_path: Path) -> DocumentMetadata:
        """Extract structured metadata from frontmatter.

        Args:
            metadata: Dictionary of frontmatter fields.
            file_path: Path to the file for fallback title extraction.

        Returns:
            DocumentMetadata instance.
        """
        title = metadata.get("title")
        if not isinstance(title, str):
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        description = metadata.get("description")
        if not isinstance(description, str):
            description = None

        license_info = metadata.get("license")
        if not isinstance(license_info, str):
            license_info = None

        return DocumentMetadata(
            title=title,
            description=description,
            license=license_info,
        )

    def _extract_section(self, relative_path: Path) -> str:
        """Extract the top-level section from the path.

        Args:
            relative_path: Path relative to docs directory.

        Returns:
            Section name (first directory component or 'root').
        """
        parts = relative_path.parts
        return parts[0] if len(parts) > 1 else "root"

    def _compute_url(self, relative_path: Path) -> str:
        """Compute the keda.sh documentation URL.

        Args:
            relative_path: Path relative to the content directory.

        Returns:
            Full URL to the documentation page.
        """
        path_str = str(relative_path)
        # Remove .md extension
        path_str = re.sub(r"\.md$", "", path_str)
        # Handle _index pages (Hugo section pages)
        path_str = re.sub(r"/_index$", "", path_str)
        # Handle root _index
        if path_str == "_index":
            path_str = ""

        if path_str:
            return f"{self.KEDA_DOCS_BASE_URL}/{path_str}/"
        return f"{self.KEDA_DOCS_BASE_URL}/"

    def _clean_content(self, content: str) -> str:
        """Clean markdown content for indexing.

        Removes Hugo-specific syntax and other markup artifacts.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned content suitable for indexing.
        """
        # Remove Hugo shortcode tags ({{< >}} form) while preserving inner content
        content = re.sub(r"\{\{<[^>]*>\}\}", "", content)
        # Remove Hugo shortcode tags ({{% %}} form) while preserving inner content
        content = re.sub(r"\{\{%[^%]*%\}\}", "", content)
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        return content.strip()
