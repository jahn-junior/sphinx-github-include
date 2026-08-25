"""Remote include directive implementation."""

import re

import requests
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.misc import Include
from docutils.utils import new_document
from myst_parser.docutils_ import Parser


class RemoteIncludeDirective(Include):
    """Include directive that supports fetching content from GitHub.

    Extends the standard Docutils Include directive to support GitHub URLs
    in the format: owner/repo:path

    Supports all standard Include options plus:
    - :branch: - Specify a branch name
    - :tag: - Specify a tag name
    - :commit: - Specify a commit SHA
    """

    # Extend parent option_spec with GitHub-specific options
    option_spec = (Include.option_spec or {}).copy()
    option_spec.update(
        {
            "branch": directives.unchanged,
            "tag": directives.unchanged,
            "commit": directives.unchanged,
        }
    )

    def run(self) -> list[nodes.Node]:
        """Process the directive - intercept GitHub URLs before parent path resolution.

        Returns:
            List of docutils nodes

        """
        # Get the path argument
        if not self.arguments:
            raise self.error("github-include directive requires a path argument")

        path = self.arguments[0]

        # Check if this is a GitHub URL (owner/repo:path format)
        github_pattern = r"^([\w-]+)/([\w.-]+):(.+)$"
        match = re.match(github_pattern, path)

        if match:
            # This is a GitHub URL - handle it specially
            return self._handle_github_include(match)

        # Not a GitHub URL - delegate to parent class
        result = super().run()
        # Ensure we return a list (parent may return Sequence)
        return list(result) if not isinstance(result, list) else result

    def _handle_github_include(self, match: re.Match[str]) -> list[nodes.Node]:
        """Handle GitHub URL includes by fetching and parsing content directly.

        Args:
            match: Regex match object with owner, repo, and path groups

        Returns:
            List of docutils nodes

        """
        owner = match.group(1)
        repo = match.group(2)
        file_path = match.group(3)

        # Determine ref from options (priority: commit > tag > branch > 'main')
        ref = (
            self.options.get("commit")
            or self.options.get("tag")
            or self.options.get("branch")
            or "main"
        )

        # Fetch content from GitHub
        try:
            content = self._fetch_from_github(owner, repo, file_path, ref)
        except Exception as e:
            raise self.error(f"Failed to fetch from GitHub: {e}") from e

        # Now we need to process the content like Include does
        # The Include directive has several modes:
        # 1. literal mode - display as literal block
        # 2. code mode - display as code block with syntax highlighting
        # 3. default mode - parse as RST

        # Apply line filtering if specified
        content = self._apply_line_filters(content)

        # Handle different rendering modes
        if "literal" in self.options:
            # Literal mode - create literal block
            literal_block = nodes.literal_block(content, content)
            literal_block["source"] = f"github:{owner}/{repo}:{file_path}@{ref}"
            if "class" in self.options:
                literal_block["classes"].extend(self.options["class"])
            return [literal_block]

        if "code" in self.options:
            # Code mode - create literal block with language
            language = self.options["code"]
            literal_block = nodes.literal_block(content, content)
            literal_block["source"] = f"github:{owner}/{repo}:{file_path}@{ref}"
            literal_block["language"] = language
            literal_block["classes"].append("code")
            literal_block["classes"].append(language)
            if "class" in self.options:
                literal_block["classes"].extend(self.options["class"])
            if "number-lines" in self.options:
                literal_block["linenos"] = True
            return [literal_block]

        # Default mode - parse content based on file extension
        source = f"github:{owner}/{repo}:{file_path}@{ref}"

        # Check if this is a Markdown file
        if file_path.endswith((".md", ".markdown")):
            return self._parse_markdown_content(content, source)
        # Parse as RST using the same approach as Include directive
        lines = content.splitlines()
        # Insert the content into the state machine's input
        self.state_machine.insert_input(lines, source)
        # Return empty list - content will be parsed by state machine
        return []

    def _apply_line_filters(self, content: str) -> str:
        """Apply line filtering options to content.

        Args:
            content: Full file content

        Returns:
            Filtered content based on options

        """
        lines = content.splitlines(keepends=True)

        # Apply start-line and end-line options (1-indexed)
        if "start-line" in self.options:
            start = self.options["start-line"] - 1  # Convert to 0-indexed
            lines = lines[start:]

        if "end-line" in self.options:
            end = self.options["end-line"]
            lines = lines[: end - (self.options.get("start-line", 1) - 1)]

        # Apply start-after and end-before text markers
        if "start-after" in self.options:
            marker = self.options["start-after"]
            for i, line in enumerate(lines):
                if marker in line:
                    lines = lines[i + 1 :]
                    break

        if "end-before" in self.options:
            marker = self.options["end-before"]
            for i, line in enumerate(lines):
                if marker in line:
                    lines = lines[:i]
                    break

        return "".join(lines)

    def _parse_markdown_content(self, content: str, source: str) -> list[nodes.Node]:
        """Parse Markdown content using MyST parser.

        Args:
            content: Markdown content to parse
            source: Source identifier for error messages

        Returns:
            List of docutils nodes

        """
        # Get the current document's settings
        settings = self.state.document.settings

        # Create a new document with the same settings
        document = new_document(source, settings)

        # Create MyST parser and parse the content
        parser = Parser()
        parser.parse(content, document)

        # Return the children of the document (excluding the document node itself)
        return list(document.children)

    def _fetch_from_github(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Fetch file content from GitHub raw content API.

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            ref: Git reference (branch, tag, or commit SHA)

        Returns:
            File content as string

        Raises:
            requests.HTTPError: If fetch fails
            requests.Timeout: If request times out

        """
        # Construct GitHub raw content URL
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"

        # Get timeout from config (access via state machine)
        timeout = getattr(self.state.document.settings, "env", None)
        if timeout and hasattr(timeout, "config"):
            timeout_value = timeout.config.remote_include_timeout
        else:
            timeout_value = 5  # Default

        # Fetch content
        response = requests.get(url, timeout=timeout_value)
        response.raise_for_status()

        # Return decoded content
        return response.text
