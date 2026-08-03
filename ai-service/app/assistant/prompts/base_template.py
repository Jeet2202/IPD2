"""
PromptTemplate system — no Jinja2 dependency, simple str.format_map().
All templates are module-level constants; no file I/O at runtime.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    role: str   # "system" | "user" | "assistant"
    template: str

    def render(self, **kwargs) -> str:
        """
        Renders the template by substituting {variable} placeholders.
        Unmatched keys in kwargs are silently ignored.
        Missing placeholders raise KeyError intentionally — fail fast.
        """
        return self.template.format_map(kwargs)

    def to_message(self, **kwargs) -> dict:
        """Returns an OpenAI-style message dict ready for the LLM."""
        return {"role": self.role, "content": self.render(**kwargs)}
