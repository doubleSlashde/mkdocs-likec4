# LikeC4 for MkDocs

[MkDocs](https://www.mkdocs.org/) plugin for embedding [LikeC4](https://likec4.dev/) diagrams.

## Requirements

- `mkdocs-likec4` python plugin
- [`likec4`](https://likec4.dev/tooling/cli/)
- `graphviz` dependency

Check out the sample [Dockerfile](https://gitlab.doubleslash.de/doubleSlash/coc-fg/tt-devops/mkdocs-likec4/-/blob/main/Dockerfile?ref_type=heads) for how you can provide the likec4 and graphviz dependencies.

## Configuration

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - mkdocs-likec4
```

That's it! The plugin automatically:

- Discovers all projects by scanning for `likec4.config.json` files (other configs formats are not supported yet!)
- Generates separate web components for each project
- Loads web components into the document as required

## Usage

Use the `likec4-view` code block and specify the view-id in the body to embed a LikeC4 diagram:

```` markdown title="LikeC4 Diagram"
``` likec4-view
view-id
```
````

This will embed the diagram from the current LikeC4 project, or the root project if this is a single
project setup.

### View Options

You may provide the following options on the opening fence line:

- `browser=true|false`

    Whether to show views browser popup/Whether the view is interactive. Possible values: `true` 
    or `false` (default: `true`)

- `dynamic-variant=diagram|sequence`

    How a dynamic view should be rendered. Possible values: diagram or sequence (default: `diagram`)

- `project=<project-name>`

    The LikeC4 project to use for this view (for multi-project setups)

## Examples

### Specify project

If you want to embed a diagram from a specific project outside the projects scope,
use the `project` parameter:

```` markdown title="LikeC4 Diagram"
``` likec4-view project=tutorial
index
```

---

``` likec4-view project=deployment
index
```
````

<div class="result" markdown>

```likec4-view project=tutorial
index
```

<hr>

```likec4-view project=deployment
index
```

</div>

!!! danger

    If you don't specify a project in a multi-project setup, and the page it not under a 
    `likec4.config.json` file, the build will fail:
    > Error: Specify exact project, known: [...]

## Known Issues

### My diagram fonts appear larger in MkDocs than in the Likec4 editor

Diagram fronts currently render at 125% due to an incompatibility between MkDocs and LikeC4.

Tracked via [UCD-128](https://jira.doubleslash.de/jira/browse/UCD-128).

??? Details

    MkDocs uses a root font size of 20px to fix Chinese character rendering issues, and resets it to
    10px for all body inline elements (see 
    [mkdocs-material#911](https://github.com/squidfunk/mkdocs-material/issues/911)).
    LikeC4 uses font sizes relative to the root font size. The combination of the 20px root font size
    and the relative font sizes in LikeC4 results in a font size of 125% for `mkdocs-likec4` diagrams.
