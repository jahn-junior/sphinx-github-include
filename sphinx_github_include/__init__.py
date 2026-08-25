"""Sphinx extension for including remote content from GitHub repositories.

This extension extends the standard Docutils Include directive to support
fetching content from GitHub repositories using the format: owner/repo:path
"""

from typing import Any

from sphinx.application import Sphinx

from sphinx_github_include.directive import RemoteIncludeDirective


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the sphinx_github_include extension.

    Args:
        app: The Sphinx application instance.

    Returns:
        Extension metadata dictionary.

    """
    # Register directive
    app.add_directive("github-include", RemoteIncludeDirective)

    # Add configuration values
    app.add_config_value("remote_include_timeout", 5, "html")

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
