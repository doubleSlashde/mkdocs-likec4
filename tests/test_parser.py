"""Tests for the LikeC4 parser module."""

from mkdocs_likec4.parser import LikeC4Parser, ViewOptions


class TestViewOptions:
    """Tests for the ViewOptions dataclass."""

    def test_default_values(self):
        """Test that ViewOptions has correct default values."""
        opts = ViewOptions(view_id="test-view")
        assert opts.view_id == "test-view"
        assert opts.browser == "true"
        assert opts.dynamic_variant == "diagram"
        assert opts.project is None

    def test_custom_values(self):
        """Test ViewOptions with custom values."""
        opts = ViewOptions(
            view_id="my-view",
            browser="false",
            dynamic_variant="sequence",
            project="myproject",
        )
        assert opts.view_id == "my-view"
        assert opts.browser == "false"
        assert opts.dynamic_variant == "sequence"
        assert opts.project == "myproject"


class TestLikeC4ParserPattern:
    """Tests for the regex pattern matching."""

    def test_basic_code_block(self):
        """Test matching a basic likec4-view code block."""
        markdown = """```likec4-view
my-view-id
```"""
        match = LikeC4Parser.PATTERN.search(markdown)
        assert match is not None
        assert match.group(1) == ""
        assert match.group(2) == "my-view-id"

    def test_code_block_with_options(self):
        """Test matching a code block with options."""
        markdown = """```likec4-view browser=false project=myproj
view-id-here
```"""
        match = LikeC4Parser.PATTERN.search(markdown)
        assert match is not None
        assert "browser=false" in match.group(1)
        assert "project=myproj" in match.group(1)
        assert match.group(2) == "view-id-here"

    def test_no_match_for_other_code_blocks(self):
        """Test that other code blocks don't match."""
        markdown = """```python
print("hello")
```"""
        match = LikeC4Parser.PATTERN.search(markdown)
        assert match is None

    def test_multiple_code_blocks(self):
        """Test finding multiple code blocks."""
        markdown = """```likec4-view
view1
```

Some text

```likec4-view project=proj2
view2
```"""
        matches = list(LikeC4Parser.PATTERN.finditer(markdown))
        assert len(matches) == 2
        assert matches[0].group(2) == "view1"
        assert matches[1].group(2) == "view2"


class TestParseOptions:
    """Tests for the parse_options method."""

    def test_empty_options(self):
        """Test parsing empty options string."""
        opts = LikeC4Parser.parse_options("", "test-view")
        assert opts.view_id == "test-view"
        assert opts.browser == "true"
        assert opts.dynamic_variant == "diagram"
        assert opts.project is None

    def test_browser_option_true(self):
        """Test parsing browser=true option."""
        opts = LikeC4Parser.parse_options("browser=true", "view")
        assert opts.browser == "true"

    def test_browser_option_false(self):
        """Test parsing browser=false option."""
        opts = LikeC4Parser.parse_options("browser=false", "view")
        assert opts.browser == "false"

    def test_dynamic_variant_diagram(self):
        """Test parsing dynamic-variant=diagram option."""
        opts = LikeC4Parser.parse_options("dynamic-variant=diagram", "view")
        assert opts.dynamic_variant == "diagram"

    def test_dynamic_variant_sequence(self):
        """Test parsing dynamic-variant=sequence option."""
        opts = LikeC4Parser.parse_options("dynamic-variant=sequence", "view")
        assert opts.dynamic_variant == "sequence"

    def test_project_option(self):
        """Test parsing project option."""
        opts = LikeC4Parser.parse_options("project=myproject", "view")
        assert opts.project == "myproject"

    def test_multiple_options(self):
        """Test parsing multiple options."""
        opts = LikeC4Parser.parse_options(
            "browser=false dynamic-variant=sequence project=proj1", "view"
        )
        assert opts.browser == "false"
        assert opts.dynamic_variant == "sequence"
        assert opts.project == "proj1"

    def test_options_in_any_order(self):
        """Test that options can appear in any order."""
        opts = LikeC4Parser.parse_options(
            "project=proj browser=false dynamic-variant=sequence", "view"
        )
        assert opts.browser == "false"
        assert opts.dynamic_variant == "sequence"
        assert opts.project == "proj"

    def test_invalid_browser_value_ignored(self):
        """Test that invalid browser value is ignored."""
        opts = LikeC4Parser.parse_options("browser=invalid", "view")
        assert opts.browser == "true"  # default

    def test_invalid_variant_value_ignored(self):
        """Test that invalid dynamic-variant value is ignored."""
        opts = LikeC4Parser.parse_options("dynamic-variant=invalid", "view")
        assert opts.dynamic_variant == "diagram"  # default


class TestIsValidIdentifier:
    """Tests for the is_valid_identifier method."""

    def test_valid_simple_name(self):
        """Test valid simple identifier."""
        assert LikeC4Parser.is_valid_identifier("project") is True

    def test_valid_name_with_numbers(self):
        """Test valid identifier with numbers."""
        assert LikeC4Parser.is_valid_identifier("project123") is True

    def test_valid_name_with_hyphen(self):
        """Test valid identifier with hyphen."""
        assert LikeC4Parser.is_valid_identifier("my-project") is True

    def test_valid_name_with_underscore(self):
        """Test valid identifier with underscore."""
        assert LikeC4Parser.is_valid_identifier("my_project") is True

    def test_valid_mixed_name(self):
        """Test valid identifier with mixed characters."""
        assert LikeC4Parser.is_valid_identifier("My-Project_123") is True

    def test_invalid_starts_with_number(self):
        """Test invalid identifier starting with number."""
        assert LikeC4Parser.is_valid_identifier("123project") is False

    def test_invalid_starts_with_hyphen(self):
        """Test invalid identifier starting with hyphen."""
        assert LikeC4Parser.is_valid_identifier("-project") is False

    def test_invalid_contains_space(self):
        """Test invalid identifier with space."""
        assert LikeC4Parser.is_valid_identifier("my project") is False

    def test_invalid_contains_special_chars(self):
        """Test invalid identifier with special characters."""
        assert LikeC4Parser.is_valid_identifier("project@name") is False
        assert LikeC4Parser.is_valid_identifier("project.name") is False
        assert LikeC4Parser.is_valid_identifier("project/name") is False

    def test_invalid_empty_string(self):
        """Test invalid empty identifier."""
        assert LikeC4Parser.is_valid_identifier("") is False

    def test_invalid_with_quotes(self):
        """Test invalid identifier with quotes (XSS attempt)."""
        assert LikeC4Parser.is_valid_identifier('view" onclick="alert(1)') is False

    def test_invalid_with_angle_brackets(self):
        """Test invalid identifier with angle brackets."""
        assert LikeC4Parser.is_valid_identifier("view<script>") is False


class TestToHtml:
    """Tests for the to_html method."""

    def test_basic_html_output(self):
        """Test basic HTML output without project."""
        opts = ViewOptions(view_id="my-view")
        html = LikeC4Parser.to_html(opts)
        assert (
            html
            == '<likec4-view view-id="my-view" browser="true" dynamic-variant="diagram"></likec4-view>'
        )

    def test_html_with_project(self):
        """Test HTML output with valid project."""
        opts = ViewOptions(view_id="my-view", project="myproject")
        html = LikeC4Parser.to_html(opts)
        assert (
            html
            == '<myproject-view view-id="my-view" browser="true" dynamic-variant="diagram"></myproject-view>'
        )

    def test_html_with_uppercase_project(self):
        """Test HTML output with uppercase project (should be lowercased)."""
        opts = ViewOptions(view_id="my-view", project="MyProject")
        html = LikeC4Parser.to_html(opts)
        assert (
            html
            == '<myproject-view view-id="my-view" browser="true" dynamic-variant="diagram"></myproject-view>'
        )

    def test_html_with_custom_options(self):
        """Test HTML output with custom options."""
        opts = ViewOptions(
            view_id="test",
            browser="false",
            dynamic_variant="sequence",
            project="proj",
        )
        html = LikeC4Parser.to_html(opts)
        assert (
            html
            == '<proj-view view-id="test" browser="false" dynamic-variant="sequence"></proj-view>'
        )

    def test_html_with_invalid_project_falls_back(self):
        """Test HTML output with invalid project name falls back to likec4-view."""
        opts = ViewOptions(view_id="my-view", project="123invalid")
        html = LikeC4Parser.to_html(opts)
        assert (
            html
            == '<likec4-view view-id="my-view" browser="true" dynamic-variant="diagram"></likec4-view>'
        )

    def test_html_escapes_invalid_view_id_with_quotes(self):
        """Test that invalid view ID with quotes is escaped to prevent XSS."""
        opts = ViewOptions(view_id='view" onclick="alert(1)')
        html = LikeC4Parser.to_html(opts)
        # Should escape quotes
        assert "onclick" not in html or "&quot;" in html
        assert '"alert' not in html

    def test_html_escapes_invalid_view_id_with_angle_brackets(self):
        """Test that invalid view ID with angle brackets is escaped."""
        opts = ViewOptions(view_id="view<script>alert(1)</script>")
        html = LikeC4Parser.to_html(opts)
        # Should escape angle brackets
        assert "<script>" not in html
        assert "&lt;" in html or "script" not in html
