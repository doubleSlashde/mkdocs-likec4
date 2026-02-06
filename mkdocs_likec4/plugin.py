import logging
from pathlib import Path
from typing import Optional

import pyjson5
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import get_relative_url

from .generator import WebComponentGenerator
from .parser import LikeC4Parser

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class LikeC4Plugin(BasePlugin):
    """MkDocs plugin for embedding LikeC4 architecture diagrams."""

    config_scheme = (("use_dot", config_options.Type(bool, default=True)),)

    def __init__(self):
        self.docs_dir = None
        self.page_projects = {}
        self.project_map = {}

    def _discover_projects(self, docs_dir: Path):
        """Discover LikeC4 projects by scanning for likec4.config.json files."""
        if not docs_dir.exists():
            log.warning("mkdocs-likec4: docs_dir does not exist: %s", docs_dir)
            return

        for config_file in docs_dir.rglob("likec4.config.json"):
            try:
                with config_file.open("r") as f:
                    config_data = pyjson5.load(f)
                if project_name := config_data.get("name"):
                    project_dir = str(config_file.parent.relative_to(docs_dir))
                    self.project_map[project_name] = project_dir
                    log.info(
                        "mkdocs-likec4: Discovered project '%s' at %s",
                        project_name,
                        project_dir,
                    )
            except (pyjson5.Json5Exception, OSError) as e:
                log.warning("mkdocs-likec4: Failed to read %s: %s", config_file, e)

        if not self.project_map:
            self.project_map[None] = "."
            log.info(
                "mkdocs-likec4: No projects discovered, using default root project"
            )

    def _find_nearest_project(self, page_path: Path, docs_dir: Path) -> Optional[str]:
        """Find the nearest LikeC4 project by traversing upward from the page."""
        current = page_path.parent
        while current >= docs_dir:
            relative_str = str(current.relative_to(docs_dir))
            for project_name, project_dir in self.project_map.items():
                if project_dir == relative_str:
                    return project_name
            if current == docs_dir:
                break
            current = current.parent
        return None

    def on_config(self, config):
        self.docs_dir = Path(config["docs_dir"])
        self._discover_projects(self.docs_dir)
        return config

    def on_page_markdown(self, markdown: str, page, **kwargs) -> str:
        """Parse likec4-view code blocks and replace with web component HTML."""
        page_file = page.file.src_uri
        projects_on_page = set()
        page_path = self.docs_dir / page.file.src_path

        def replacer(match):
            options_text = (match.group(1) or "").strip()
            view_id = match.group(2).strip()
            opts = LikeC4Parser.parse_options(options_text, view_id)

            if opts.project is None:
                opts.project = self._find_nearest_project(page_path, self.docs_dir)
                if opts.project:
                    log.debug(
                        "mkdocs-likec4: Auto-detected project '%s' for %s",
                        opts.project,
                        page_file,
                    )

            projects_on_page.add(opts.project)
            return LikeC4Parser.to_html(opts)

        markdown = LikeC4Parser.PATTERN.sub(replacer, markdown)
        if projects_on_page:
            self.page_projects[page_file] = projects_on_page
        return markdown

    def on_page_content(self, html, page, **kwargs):
        """Inject project-specific JavaScript only on pages that use likec4-view."""
        page_file = page.file.src_uri
        if page_file not in self.page_projects:
            return html

        scripts = [
            f'<script src="{get_relative_url(WebComponentGenerator.get_script_path(p), page.url)}"></script>'
            for p in self.page_projects[page_file]
        ]
        return "\n".join(scripts) + "\n" + html

    def on_post_build(self, config):
        """Generate web component JS files for all projects used across the site."""
        site_dir = Path(config["site_dir"])
        all_projects = {p for projects in self.page_projects.values() for p in projects}

        for project in all_projects:
            if project in self.project_map:
                WebComponentGenerator.generate(
                    project,
                    self.project_map[project],
                    str(self.docs_dir),
                    site_dir,
                    use_dot=self.config["use_dot"],
                )
            else:
                log.warning(
                    "mkdocs-likec4: Skipping generation for undiscovered project: %s",
                    project,
                )
