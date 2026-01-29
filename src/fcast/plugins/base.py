from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

@dataclass
class ApiParam:
    name: str
    type_repr: str | None = None
    default_repr: str | None = None
    required: bool = False
    doc: str | None = None

@dataclass
class ApiSymbol:
    qualname: str
    kind: str  # class/function/method/endpoint
    signature: str
    params: list[ApiParam]
    doc_url: str | None = None

class LibraryAdapter(ABC):
    """Extract API surface into registry tables."""

    @abstractmethod
    def library_name(self) -> str: ...

    @abstractmethod
    def extract_symbols(self) -> list[ApiSymbol]: ...

class ModelRunner(ABC):
    """Run fit/predict/cv. In this template we keep a mock runner in pipeline/runner.py."""
    @abstractmethod
    def fit(self, *args, **kwargs): ...
