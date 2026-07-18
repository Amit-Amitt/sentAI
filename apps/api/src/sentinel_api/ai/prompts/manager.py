import re

from sentinel_api.ai.exceptions import PromptException


class PromptManager:
    """Manages prompt templates, handles versioning, and interpolates variables."""

    def __init__(self) -> None:
        # Store templates mapping: name -> version -> raw_template_str
        self._templates: dict[str, dict[str, str]] = {}

    def register_template(self, name: str, version: str, template: str) -> None:
        """Registers a raw template string under a name and version identifier."""
        if name not in self._templates:
            self._templates[name] = {}
        self._templates[name][version] = template

    def render(self, name: str, version: str, **variables: str) -> str:
        """Interpolates variables inside double-curly brackets {{ variable_name }} in the template."""
        if name not in self._templates:
            raise PromptException(f"Prompt template '{name}' is not registered.")

        versions = self._templates[name]
        if version not in versions:
            raise PromptException(
                f"Version '{version}' for template '{name}' not found. "
                f"Available versions: {list(versions.keys())}"
            )

        template = versions[version]
        try:
            # Convert standard jinja/double-brace format {{ var }} to python format {var}
            python_format_template = re.sub(r"\{\{\s*(\w+)\s*\}\}", r"{\1}", template)
            return python_format_template.format(**variables)
        except KeyError as ke:
            raise PromptException(
                f"Missing required parameter {ke} during prompt rendering for '{name}' (v{version})."
            ) from ke
        except Exception as e:
            raise PromptException(
                f"Failed to render template '{name}' (v{version}): {e}"
            ) from e
