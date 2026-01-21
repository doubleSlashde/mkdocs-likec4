"""Tests for the LikeC4 generator module."""

import subprocess
from unittest.mock import patch

from mkdocs_likec4.generator import WebComponentGenerator


class TestGetScriptPath:
    """Tests for the get_script_path method."""

    def test_default_project_path(self):
        """Test script path for default (None) project."""
        path = WebComponentGenerator.get_script_path(None)
        assert path == "assets/mkdocs_likec4/likec4_views.js"

    def test_named_project_path(self):
        """Test script path for named project."""
        path = WebComponentGenerator.get_script_path("myproject")
        assert path == "assets/mkdocs_likec4/likec4_views_myproject.js"

    def test_uppercase_project_lowercased(self):
        """Test that uppercase project names are lowercased."""
        path = WebComponentGenerator.get_script_path("MyProject")
        assert path == "assets/mkdocs_likec4/likec4_views_myproject.js"

    def test_mixed_case_project(self):
        """Test mixed case project name."""
        path = WebComponentGenerator.get_script_path("My-Project_123")
        assert path == "assets/mkdocs_likec4/likec4_views_my-project_123.js"


class TestGenerate:
    """Tests for the generate method."""

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_default_project(self, mock_run, tmp_path):
        """Test generating web component for default project."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        WebComponentGenerator.generate(
            project_name=None,
            project_dir=None,
            build_dir="/docs",
            site_dir=site_dir,
        )

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        call_kwargs = mock_run.call_args[1]
        assert call_args[0] == "npx"
        assert call_args[1] == "likec4"
        assert call_args[2] == "codegen"
        assert call_args[3] == "webcomponent"
        assert "/docs" in call_args[4]
        assert "--webcomponent-prefix" not in call_args
        # Verify check=True is passed for proper error handling
        assert call_kwargs.get("check") is True

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_named_project(self, mock_run, tmp_path):
        """Test generating web component for named project."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        WebComponentGenerator.generate(
            project_name="myproject",
            project_dir="subdir",
            build_dir="/docs",
            site_dir=site_dir,
        )

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "--webcomponent-prefix" in call_args
        prefix_idx = call_args.index("--webcomponent-prefix")
        assert call_args[prefix_idx + 1] == "myproject"

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_creates_assets_dir(self, mock_run, tmp_path):
        """Test that generate creates the assets directory."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        WebComponentGenerator.generate(
            project_name=None,
            project_dir=None,
            build_dir="/docs",
            site_dir=site_dir,
        )

        assets_dir = site_dir / "assets" / "mkdocs_likec4"
        assert assets_dir.exists()

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_invalid_project_name_skipped(self, mock_run, tmp_path):
        """Test that invalid project names are skipped."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        WebComponentGenerator.generate(
            project_name="123invalid",
            project_dir=None,
            build_dir="/docs",
            site_dir=site_dir,
        )

        mock_run.assert_not_called()

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_handles_subprocess_error(self, mock_run, tmp_path):
        """Test that subprocess errors are handled gracefully."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")

        # Should not raise
        WebComponentGenerator.generate(
            project_name=None,
            project_dir=None,
            build_dir="/docs",
            site_dir=site_dir,
        )

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_handles_file_not_found(self, mock_run, tmp_path):
        """Test that FileNotFoundError is handled gracefully."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()
        mock_run.side_effect = FileNotFoundError("npx not found")

        # Should not raise
        WebComponentGenerator.generate(
            project_name=None,
            project_dir=None,
            build_dir="/docs",
            site_dir=site_dir,
        )

    @patch("mkdocs_likec4.generator.subprocess.run")
    def test_generate_output_path(self, mock_run, tmp_path):
        """Test that output path is correct."""
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        WebComponentGenerator.generate(
            project_name="proj",
            project_dir="projdir",
            build_dir="/docs",
            site_dir=site_dir,
        )

        call_args = mock_run.call_args[0][0]
        output_idx = call_args.index("-o")
        output_path = call_args[output_idx + 1]
        assert "likec4_views_proj.js" in output_path
