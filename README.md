# sphinx-github-include

sphinx-github-include adds a Sphinx directive for including content directly from GitHub
repositories using the format `owner/repo:path`.

## Basic usage

Include and parse RST or Markdown content:

```rst
.. github-include:: sphinx-doc/sphinx:README.rst
   :branch: master
   :start-line: 21
   :end-line: 25
```

Display code with syntax highlighting using `:code:`:

```rst
.. github-include:: python/cpython:Lib/this.py
   :code: python
   :number-lines:
```

Display literal text using `:literal:`:

```rst
.. github-include:: github/gitignore:Python.gitignore
   :literal:
```

Specify a version with `:branch:`, `:tag:`, or `:commit:` (defaults to `main`):

```rst
.. github-include:: owner/repo:path/to/file.py
   :tag: v1.0.0
```

Filter lines with `:start-line:`, `:end-line:`, `:start-after:`, or `:end-before:`:

```rst
.. github-include:: owner/repo:example.py
   :start-line: 10
   :end-line: 50
```

## Project setup

Install via pip:

```bash
pip install sphinx-github-include
```

Add to your `conf.py`:

```python
extensions = [
    "sphinx_github_include"
]
```

## Community and support

Report issues on the [GitHub
repository](https://github.com/canonical/sphinx-ext-template).

sphinx-github-include is covered by the [Ubuntu Code of
Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## License and copyright

sphinx-github-include is released under the [GPL-3.0 license](LICENSE).
