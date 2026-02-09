import logging
import re
from dataclasses import dataclass
from html import escape
from typing import Optional

log = logging.getLogger(f"mkdocs.plugins.{__name__}")

IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")


@dataclass
class ViewOptions:
    """Options parsed from a likec4-view code block."""

    view_id: str
    browser: str = "true"
    dynamic_variant: str = "diagram"
    project: Optional[str] = None


class LikeC4Parser:
    """Parser for likec4-view markdown code blocks."""

    PATTERN = re.compile(
        r"([ \t]*)```likec4-view([^\r\n]*)\r?\n([^\r\n]+)\r?\n\1```",
    )
    OPT_BROWSER = re.compile(r"\bbrowser=(true|false)\b")
    OPT_VARIANT = re.compile(r"\bdynamic-variant=(diagram|sequence)\b")
    OPT_PROJECT = re.compile(r"\bproject=([^\s]+)\b")

    @classmethod
    def is_valid_identifier(cls, value: str) -> bool:
        """Validate that an identifier contains only safe characters."""
        return bool(IDENTIFIER_PATTERN.match(value))

    @classmethod
    def parse_options(cls, options_text: str, view_id: str) -> ViewOptions:
        """
        Parse options from the opening fence line of a likec4-view block.

        Options can appear in any order and are all optional with sensible defaults.
        """
        opts = ViewOptions(view_id=view_id)

        if m := cls.OPT_BROWSER.search(options_text):
            opts.browser = m.group(1)

        if m := cls.OPT_VARIANT.search(options_text):
            opts.dynamic_variant = m.group(1)

        if m := cls.OPT_PROJECT.search(options_text):
            opts.project = m.group(1)

        return opts

    @classmethod
    def to_html(cls, opts: ViewOptions) -> str:
        if not cls.is_valid_identifier(opts.view_id):
            log.warning(
                "mkdocs-likec4: Invalid view ID '%s': contains unsafe characters",
                opts.view_id,
            )

        valid_project = opts.project and cls.is_valid_identifier(opts.project)
        if opts.project and not valid_project:
            log.warning(
                "mkdocs-likec4: Invalid project name '%s': using 'likec4-view' tag",
                opts.project,
            )

        tag = f"{opts.project.lower()}-view" if valid_project else "likec4-view"
        return (
            f'<{tag} view-id="{escape(opts.view_id, quote=True)}" '
            f'browser="{opts.browser}" dynamic-variant="{opts.dynamic_variant}"></{tag}>'
        )
