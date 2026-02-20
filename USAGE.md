# Usage Guide

This guide provides detailed instructions for using the MCP KEDA Documentation Server.

## Installation

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerised deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martoc/mcp-keda-documentation.git
   cd mcp-keda-documentation
   ```

2. Initialise the development environment:
   ```bash
   make init
   ```

3. Build the documentation index:
   ```bash
   make index
   ```

## Indexing Documentation

### Initial Indexing

Index the KEDA documentation from the main branch:

```bash
uv run keda-docs-index index
```

### Rebuilding the Index

Clear the existing index and rebuild from scratch:

```bash
uv run keda-docs-index index --rebuild
```

### Indexing a Specific Branch

Index documentation from a specific Git branch:

```bash
uv run keda-docs-index index --branch main
```

### Index Statistics

View the number of indexed documents:

```bash
uv run keda-docs-index stats
```

## Running the MCP Server

### Using the Container Image (Recommended)

The `martoc/mcp-keda-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-keda-documentation:latest
```

### Local Development

Run the server directly using uv:

```bash
make run
# or
uv run mcp-keda-documentation
```

### Building a Local Docker Image

Build and run the server in a Docker container:

```bash
make docker-build
make docker-run
```

## MCP Client Configuration

### Claude Code (Container Image)

Add to your project's `.mcp.json` to use the published container image:

```json
{
  "mcpServers": {
    "keda-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-keda-documentation:latest"]
    }
  }
}
```

### Claude Code (Local Development)

Add to your project's `.mcp.json` for local development:

```json
{
  "mcpServers": {
    "keda-documentation": {
      "command": "uv",
      "args": ["run", "mcp-keda-documentation"],
      "cwd": "/path/to/mcp-keda-documentation"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "keda-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-keda-documentation:latest"]
    }
  }
}
```

## Using the Tools

### Searching Documentation

Search for topics in KEDA documentation:

```
Search for "apache kafka scaler"
Search for "prometheus" in section "docs"
Search for "authentication" with limit 20
```

Example response:
```json
{
  "query": "apache kafka scaler",
  "section_filter": null,
  "result_count": 5,
  "results": [
    {
      "title": "Apache Kafka",
      "url": "https://keda.sh/docs/2.16/scalers/apache-kafka/",
      "path": "docs/2.16/scalers/apache-kafka.md",
      "section": "docs",
      "snippet": "...apache kafka topic lag...",
      "relevance_score": 12.5432
    }
  ]
}
```

### Reading Documentation

Retrieve the full content of a specific page:

```
Read documentation at path "docs/2.16/scalers/apache-kafka.md"
```

Example response:
```json
{
  "path": "docs/2.16/scalers/apache-kafka.md",
  "title": "Apache Kafka",
  "description": "Scale applications based on Apache Kafka topic lag",
  "section": "docs",
  "url": "https://keda.sh/docs/2.16/scalers/apache-kafka/",
  "content": "# Apache Kafka\n\n..."
}
```

## Common Sections

The KEDA documentation is organised into several sections:

- **docs**: Main documentation (concepts, scalers, operate, reference)
- **blog**: Blog posts and announcements
- **troubleshooting**: Troubleshooting guides
- **faq**: Frequently asked questions (from TOML data files)

Use these section names with the `section` parameter to filter search results.

## Development Workflow

### Code Quality Checks

Run all code quality checks:

```bash
make build
```

This runs:
- Linter (ruff)
- Type checker (mypy)
- Tests with coverage (pytest)

### Individual Checks

```bash
make lint       # Run linter only
make typecheck  # Run type checker only
make test       # Run tests only
make format     # Format code
```

### Updating Dependencies

Update the lock file:

```bash
make generate
```

## Troubleshooting

### Index Build Fails

If the index build fails, try:

1. Check your internet connection
2. Verify Git is installed and accessible
3. Try rebuilding with a different branch:
   ```bash
   uv run keda-docs-index index --rebuild --branch main
   ```

### No Search Results

If searches return no results:

1. Verify the index is built:
   ```bash
   uv run keda-docs-index stats
   ```

2. Rebuild the index if necessary:
   ```bash
   uv run keda-docs-index index --rebuild
   ```

### Database Location

The default database location is `data/keda_docs.db`. To use a custom location:

```bash
uv run keda-docs-index index --database /path/to/custom.db
```

## Performance Considerations

- **Initial indexing**: May take several minutes depending on network speed
- **Sparse checkout**: Only `content/` and `data/` are cloned, reducing download size
- **Search performance**: FTS5 with BM25 ranking provides fast, relevant results
- **Memory usage**: Minimal during operation; database is SQLite-based
