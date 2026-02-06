import logging
import subprocess
from pathlib import Path
from typing import Optional

from .parser import LikeC4Parser

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class WebComponentGenerator:
    """Generates LikeC4 web component JavaScript files."""

    ASSETS_DIR = "assets/mkdocs_likec4"

    @classmethod
    def get_script_path(cls, project: Optional[str]) -> str:
        """Get the site-relative path for a project's web component JS file."""
        if project is None:
            return f"{cls.ASSETS_DIR}/likec4_views.js"
        return f"{cls.ASSETS_DIR}/likec4_views_{project}.js".lower()

    @classmethod
    def generate(
        cls,
        project_name: Optional[str],
        project_dir: Optional[str],
        build_dir: str,
        site_dir: Path,
        *,
        use_dot: bool = True,
    ) -> None:
        """Generate web component JS file for a LikeC4 project."""
        if project_name is not None and not LikeC4Parser.is_valid_identifier(
            project_name
        ):
            log.error(
                "mkdocs-likec4: Invalid project name '%s': must start with a letter "
                "and contain only letters, numbers, hyphens, and underscores",
                project_name,
            )
            return

        site_dir.joinpath(cls.ASSETS_DIR).mkdir(parents=True, exist_ok=True)
        dest_file = site_dir.joinpath(cls.get_script_path(project_name))

        project_path = (
            build_dir
            if project_name is None
            else str(Path(build_dir) / (project_dir or project_name))
        )
        log.info(
            "mkdocs-likec4: Generating web component for %s from %s",
            f"project '{project_name}'" if project_name else "default project",
            project_path,
        )

        cmd = ["npx", "likec4", "codegen", "webcomponent"]
        if not use_dot:
            cmd.append("--no-use-dot")
        if project_name is not None:
            cmd.extend(["--webcomponent-prefix", project_name.lower()])
        cmd.extend([project_path, "-o", str(dest_file)])

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            log.error(
                "mkdocs-likec4: Failed to generate web component for project '%s': %s",
                project_name or "default",
                e,
            )
        except FileNotFoundError:
            log.error(
                "mkdocs-likec4: 'npx' or 'likec4' command not found. "
                "Ensure Node.js and likec4 are installed."
            )
