# mkdocs-likec4

MkDocs plugin for embedding [LikeC4](https://likec4.dev/) architecture diagrams.

## Quick Start

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - mkdocs-likec4
```

Embed views in your markdown:

````markdown
```likec4-view
<your-view-id>
```
````

## Documentation

For complete documentation, see **[Documentation](https://pages.doubleslash.de/doubleslash/coc-fg/tt-devops/mkdocs-likec4/)**

## Development

### Registry setup

Run `./local-preview` in your terminal to build and run a MkDocs server with the plugin installed,
serving on <http://127.0.0.1:8000/>.

## Releasing

Trigger the manual `release` job from the [`.gitlab-ci.yml`](.gitlab-ci.yml).

The package will be published to the projects PyPi registry and is available at
<https://gitlab.doubleslash.de/api/v4/projects/2340/packages/pypi/simple>.