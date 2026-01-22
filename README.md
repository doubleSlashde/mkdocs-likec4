# mkdocs-likec4

MkDocs plugin for embedding [LikeC4](https://likec4.dev/) architecture diagrams.

## Quick Start

1. Ensure `likec4` and `graphviz` are available on the build system
2. Install the `mkdocs-likec4` plugin via `pip`:
  ```shell
  pip install mkdocs-likec4
  ```
3. Add the plugin to your `mkdocs.yml`:
  ```yaml
  plugins:
    - search
    - mkdocs-likec4
  ```
4. Start embedding views in your markdown:
  ````markdown
  ```likec4-view
  <your-view-id>
  ```
  ````

## Documentation

For detailed instructions, configuration options and a demo, please read the **[documentation](https://doubleslashde.github.io/mkdocs-likec4/)**.

## Development

### Local setup

Run `./local-preview` in your terminal to build and run a MkDocs server with the plugin installed,
serving on <http://127.0.0.1:8000/>.

## Releasing

Manually trigger the `release` workflow via GitHub Actions, which will auto-bump the plugin version and perform the release process.
PyPi publishing is set up via [trusted publishing](https://docs.pypi.org/trusted-publishers/).

## License

mkdocs-likec4 is licensed under the [Apache License, Version 2.0](LICENSE).
