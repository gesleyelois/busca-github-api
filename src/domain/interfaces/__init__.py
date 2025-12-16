"""Interfaces do domínio."""

from .github_repository import IGitHubRepository
from .file_repository import IFileRepository
from .html_generator import IHTMLGenerator

__all__ = ['IGitHubRepository', 'IFileRepository', 'IHTMLGenerator']

