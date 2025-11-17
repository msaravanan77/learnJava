"""
Shared Types for Workspace Intelligence Services
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CodeLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"


class IndexStatus(Enum):
    """Indexing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CodeElement:
    """Represents a code element (function, class, variable)"""
    id: str
    workspace_id: str
    file_path: str
    name: str
    element_type: str  # function, class, variable, import
    language: CodeLanguage
    start_line: int
    end_line: int
    code: str
    docstring: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CodeEmbedding:
    """Represents a code embedding"""
    element_id: str
    vector: List[float]
    model: str
    dimension: int
    created_at: datetime


@dataclass
class SearchResult:
    """Search result from vector database"""
    element_id: str
    score: float
    code_element: CodeElement
    metadata: Dict[str, Any]


@dataclass
class Workspace:
    """Workspace information"""
    id: str
    name: str
    root_path: str
    language: Optional[CodeLanguage] = None
    total_files: int = 0
    total_elements: int = 0
    indexed_at: Optional[datetime] = None
    status: IndexStatus = IndexStatus.PENDING


@dataclass
class FileDependency:
    """File dependency relationship"""
    source_file: str
    target_file: str
    import_type: str  # direct, transitive
    line_number: int


@dataclass
class User:
    """User information"""
    id: str
    email: str
    name: str
    workspace_ids: List[str]
    created_at: datetime


@dataclass
class APIRequest:
    """API request metadata"""
    request_id: str
    user_id: str
    workspace_id: str
    endpoint: str
    method: str
    timestamp: datetime
    ip_address: str


@dataclass
class APIResponse:
    """API response metadata"""
    request_id: str
    status_code: int
    response_time_ms: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None


# Constants
MAX_EMBEDDING_DIMENSION = 768
MAX_CODE_LENGTH = 10000
MAX_CONTEXT_TOKENS = 3500
DEFAULT_SEARCH_TOP_K = 10
