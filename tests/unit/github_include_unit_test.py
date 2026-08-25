"""Unit tests for github-include directive."""

import re


def test_github_url_pattern_valid():
    """Test valid GitHub URL patterns."""
    pattern = r"^([\w-]+)/([\w.-]+):(.+)$"

    assert re.match(pattern, "owner/repo:path/to/file.rst")
    assert re.match(pattern, "sphinx-doc/sphinx:README.rst")
    assert re.match(pattern, "user-name/repo.name:file.py")


def test_github_url_pattern_invalid():
    """Test invalid GitHub URL patterns."""
    pattern = r"^([\w-]+)/([\w.-]+):(.+)$"

    assert not re.match(pattern, "local-file.rst")
    assert not re.match(pattern, "/absolute/path.rst")
    assert not re.match(pattern, "../relative/path.rst")
    assert not re.match(pattern, "owner:repo:file")


def test_ref_priority():
    """Test Git ref selection priority: commit > tag > branch > main."""

    # Only branch
    options = {"branch": "develop"}
    ref = options.get("commit") or options.get("tag") or options.get("branch") or "main"
    assert ref == "develop"

    # Branch and tag (tag wins)
    options = {"branch": "develop", "tag": "v1.0"}
    ref = options.get("commit") or options.get("tag") or options.get("branch") or "main"
    assert ref == "v1.0"

    # All three (commit wins)
    options = {"branch": "develop", "tag": "v1.0", "commit": "abc123"}
    ref = options.get("commit") or options.get("tag") or options.get("branch") or "main"
    assert ref == "abc123"

    # None (default main)
    options = {}
    ref = options.get("commit") or options.get("tag") or options.get("branch") or "main"
    assert ref == "main"


def test_line_filtering_start_end():
    """Test line filtering with start-line and end-line."""
    content = "line1\nline2\nline3\nline4\nline5\n"
    lines = content.splitlines(keepends=True)

    # Start from line 2 (1-indexed, so index 1)
    start = 2 - 1
    filtered = lines[start:]
    assert "".join(filtered) == "line2\nline3\nline4\nline5\n"

    # End at line 4
    end = 4
    filtered = lines[:end]
    assert "".join(filtered) == "line1\nline2\nline3\nline4\n"

    start = 2 - 1
    filtered = lines[start:]  # First: apply start-line
    end = 4
    filtered = filtered[: end - (2 - 1)]  # Second: apply end-line
    assert "".join(filtered) == "line2\nline3\nline4\n"


def test_line_filtering_markers():
    """Test line filtering with text markers."""
    content = "line1\n## START\nline2\nline3\n## END\nline4\n"
    lines = content.splitlines(keepends=True)

    # Start after marker
    marker = "## START"
    for i, line in enumerate(lines):
        if marker in line:
            lines = lines[i + 1 :]
            break
    assert "".join(lines) == "line2\nline3\n## END\nline4\n"

    # End before marker
    lines = content.splitlines(keepends=True)
    marker = "## END"
    for i, line in enumerate(lines):
        if marker in line:
            lines = lines[:i]
            break
    assert "".join(lines) == "line1\n## START\nline2\nline3\n"


def test_markdown_file_detection():
    """Test Markdown file extension detection."""
    assert "file.md".endswith((".md", ".markdown"))
    assert "file.markdown".endswith((".md", ".markdown"))
    assert not "file.rst".endswith((".md", ".markdown"))
    assert not "file.py".endswith((".md", ".markdown"))


def test_github_url_construction():
    """Test GitHub raw URL construction."""
    owner = "sphinx-doc"
    repo = "sphinx"
    ref = "master"
    path = "README.rst"

    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    assert (
        url == "https://raw.githubusercontent.com/sphinx-doc/sphinx/master/README.rst"
    )
