"""Entidade PullRequest."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PullRequest:
    """Representa um Pull Request mergeado."""
    titulo: str
    link: str
    data_merge: str
    descricao: str
    numero: int
    branch: Optional[str] = None
    commits: Optional[List[str]] = None

