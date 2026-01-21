"""Tests for the LikeC4 plugin module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from mkdocs_likec4.plugin import LikeC4Plugin


@pytest.fixture
def plugin():
    """Create a fresh plugin instance."""
    return LikeC4Plugin()


@pytest.fixture
def docs_dir(tmp_path):
    """Create a temporary docs directory."""
    docs = tmp_path / "docs"
    docs.mkdir()
    return docs


class TestPluginInit:
    """Tests for plugin initialization."""

    def test_init_defaults(self, plugin):
        """Test that plugin initializes with correct defaults."""
        assert plugin.docs_dir is None
        assert plugin.page_projects == {}
        assert plugin.project_map == {}


class TestDiscoverProjects:
    """Tests for the _discover_projects method."""

    def test_discover_single_project(self, plugin, docs_dir):
        """Test discovering a single project."""
        project_dir = docs_dir / "myproject"
        project_dir.mkdir()
        config_file = project_dir / "likec4.config.json"
        config_file.write_text(json.dumps({"name": "myproject"}))

        plugin._discover_projects(docs_dir)

        assert "myproject" in plugin.project_map
        assert plugin.project_map["myproject"] == "myproject"

    def test_discover_multiple_projects(self, plugin, docs_dir):
        """Test discovering multiple projects."""
        for name in ["project1", "project2", "project3"]:
            project_dir = docs_dir / name
            project_dir.mkdir()
            config_file = project_dir / "likec4.config.json"
            config_file.write_text(json.dumps({"name": name}))

        plugin._discover_projects(docs_dir)

        assert len(plugin.project_map) == 3
        assert "project1" in plugin.project_map
        assert "project2" in plugin.project_map
        assert "project3" in plugin.project_map

    def test_discover_nested_project(self, plugin, docs_dir):
        """Test discovering a nested project."""
        nested_dir = docs_dir / "sub" / "nested"
        nested_dir.mkdir(parents=True)
        config_file = nested_dir / "likec4.config.json"
        config_file.write_text(json.dumps({"name": "nested"}))

        plugin._discover_projects(docs_dir)

        assert "nested" in plugin.project_map
        assert plugin.project_map["nested"] == "sub/nested"

    def test_discover_no_projects_uses_default(self, plugin, docs_dir):
        """Test that no projects defaults to root project."""
        plugin._discover_projects(docs_dir)

        assert None in plugin.project_map
        assert plugin.project_map[None] == "."

    def test_discover_invalid_json_skipped(self, plugin, docs_dir):
        """Test that invalid JSON config files are skipped."""
        project_dir = docs_dir / "badproject"
        project_dir.mkdir()
        config_file = project_dir / "likec4.config.json"
        config_file.write_text("not valid json")

        plugin._discover_projects(docs_dir)

        assert "badproject" not in plugin.project_map
        # Should fall back to default
        assert None in plugin.project_map

    def test_discover_config_without_name_skipped(self, plugin, docs_dir):
        """Test that config without name field is skipped."""
        project_dir = docs_dir / "noname"
        project_dir.mkdir()
        config_file = project_dir / "likec4.config.json"
        config_file.write_text(json.dumps({"version": "1.0"}))

        plugin._discover_projects(docs_dir)

        assert "noname" not in plugin.project_map

    def test_discover_nonexistent_dir(self, plugin, tmp_path):
        """Test discovering projects in nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"

        plugin._discover_projects(nonexistent)

        # Should not raise, project_map remains empty
        assert plugin.project_map == {}


class TestFindNearestProject:
    """Tests for the _find_nearest_project method."""

    def test_find_project_in_same_directory(self, plugin, docs_dir):
        """Test finding project when page is in project directory."""
        plugin.project_map = {"myproject": "myproject"}

        page_path = docs_dir / "myproject" / "index.md"
        result = plugin._find_nearest_project(page_path, docs_dir)

        assert result == "myproject"

    def test_find_project_in_subdirectory(self, plugin, docs_dir):
        """Test finding project when page is in subdirectory of project."""
        plugin.project_map = {"myproject": "myproject"}

        page_path = docs_dir / "myproject" / "sub" / "page.md"
        result = plugin._find_nearest_project(page_path, docs_dir)

        assert result == "myproject"

    def test_find_no_project_returns_none(self, plugin, docs_dir):
        """Test that pages outside projects return None."""
        plugin.project_map = {"myproject": "myproject"}

        page_path = docs_dir / "other" / "page.md"
        result = plugin._find_nearest_project(page_path, docs_dir)

        assert result is None

    def test_find_root_project(self, plugin, docs_dir):
        """Test finding root project."""
        plugin.project_map = {None: "."}

        page_path = docs_dir / "page.md"
        result = plugin._find_nearest_project(page_path, docs_dir)

        assert result is None


class TestOnConfig:
    """Tests for the on_config method."""

    def test_on_config_sets_docs_dir(self, plugin, docs_dir):
        """Test that on_config sets docs_dir."""
        config = {"docs_dir": str(docs_dir)}

        result = plugin.on_config(config)

        assert plugin.docs_dir == docs_dir
        assert result == config

    def test_on_config_discovers_projects(self, plugin, docs_dir):
        """Test that on_config triggers project discovery."""
        project_dir = docs_dir / "proj"
        project_dir.mkdir()
        config_file = project_dir / "likec4.config.json"
        config_file.write_text(json.dumps({"name": "proj"}))

        config = {"docs_dir": str(docs_dir)}
        plugin.on_config(config)

        assert "proj" in plugin.project_map


class TestOnPageMarkdown:
    """Tests for the on_page_markdown method."""

    def test_replaces_code_block(self, plugin, docs_dir):
        """Test that likec4-view code blocks are replaced."""
        plugin.docs_dir = docs_dir
        plugin.project_map = {None: "."}

        page = MagicMock()
        page.file.src_uri = "index.md"
        page.file.src_path = "index.md"

        markdown = """# Title

```likec4-view
my-view
```

Some text."""

        result = plugin.on_page_markdown(markdown, page)

        assert "```likec4-view" not in result
        assert '<likec4-view view-id="my-view"' in result
        assert "Some text." in result

    def test_replaces_multiple_code_blocks(self, plugin, docs_dir):
        """Test that multiple code blocks are replaced."""
        plugin.docs_dir = docs_dir
        plugin.project_map = {None: "."}

        page = MagicMock()
        page.file.src_uri = "index.md"
        page.file.src_path = "index.md"

        markdown = """```likec4-view
view1
```

```likec4-view
view2
```"""

        result = plugin.on_page_markdown(markdown, page)

        assert 'view-id="view1"' in result
        assert 'view-id="view2"' in result

    def test_tracks_projects_on_page(self, plugin, docs_dir):
        """Test that projects used on page are tracked."""
        plugin.docs_dir = docs_dir
        plugin.project_map = {"proj": "proj"}

        page = MagicMock()
        page.file.src_uri = "proj/index.md"
        page.file.src_path = "proj/index.md"

        markdown = """```likec4-view
my-view
```"""

        plugin.on_page_markdown(markdown, page)

        assert "proj/index.md" in plugin.page_projects
        assert "proj" in plugin.page_projects["proj/index.md"]

    def test_preserves_non_likec4_content(self, plugin, docs_dir):
        """Test that non-likec4 content is preserved."""
        plugin.docs_dir = docs_dir
        plugin.project_map = {None: "."}

        page = MagicMock()
        page.file.src_uri = "index.md"
        page.file.src_path = "index.md"

        markdown = """# Title

```python
print("hello")
```

Some text."""

        result = plugin.on_page_markdown(markdown, page)

        assert result == markdown


class TestOnPageContent:
    """Tests for the on_page_content method."""

    def test_injects_script_for_page_with_views(self, plugin):
        """Test that script tags are injected for pages with views."""
        plugin.page_projects = {"index.md": {None}}

        page = MagicMock()
        page.file.src_uri = "index.md"
        page.url = "index.html"

        html = "<h1>Title</h1>"
        result = plugin.on_page_content(html, page)

        assert "<script" in result
        assert "likec4_views.js" in result
        assert "<h1>Title</h1>" in result

    def test_no_script_for_page_without_views(self, plugin):
        """Test that no script is injected for pages without views."""
        plugin.page_projects = {}

        page = MagicMock()
        page.file.src_uri = "other.md"
        page.url = "other.html"

        html = "<h1>Title</h1>"
        result = plugin.on_page_content(html, page)

        assert result == html

    def test_injects_multiple_scripts_for_multiple_projects(self, plugin):
        """Test that multiple scripts are injected for multiple projects."""
        plugin.page_projects = {"index.md": {"proj1", "proj2"}}

        page = MagicMock()
        page.file.src_uri = "index.md"
        page.url = "index.html"

        html = "<h1>Title</h1>"
        result = plugin.on_page_content(html, page)

        assert "likec4_views_proj1.js" in result
        assert "likec4_views_proj2.js" in result


class TestOnPostBuild:
    """Tests for the on_post_build method."""

    @patch("mkdocs_likec4.plugin.WebComponentGenerator.generate")
    def test_generates_for_all_used_projects(self, mock_generate, plugin, tmp_path):
        """Test that web components are generated for all used projects."""
        plugin.docs_dir = tmp_path / "docs"
        plugin.docs_dir.mkdir()
        plugin.project_map = {"proj1": "proj1", "proj2": "proj2"}
        plugin.page_projects = {
            "page1.md": {"proj1"},
            "page2.md": {"proj2"},
        }

        site_dir = tmp_path / "site"
        site_dir.mkdir()
        config = {"site_dir": str(site_dir)}

        plugin.on_post_build(config)

        assert mock_generate.call_count == 2

    @patch("mkdocs_likec4.plugin.WebComponentGenerator.generate")
    def test_skips_undiscovered_projects(self, mock_generate, plugin, tmp_path):
        """Test that undiscovered projects are skipped."""
        plugin.docs_dir = tmp_path / "docs"
        plugin.docs_dir.mkdir()
        plugin.project_map = {"proj1": "proj1"}
        plugin.page_projects = {
            "page1.md": {"proj1", "unknown"},
        }

        site_dir = tmp_path / "site"
        site_dir.mkdir()
        config = {"site_dir": str(site_dir)}

        plugin.on_post_build(config)

        # Only proj1 should be generated
        assert mock_generate.call_count == 1
        call_args = mock_generate.call_args[0]
        assert call_args[0] == "proj1"
