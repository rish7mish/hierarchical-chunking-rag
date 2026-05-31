from pypdf import PdfReader
from dataclasses import dataclass, asdict
from typing import List, Dict
import re
import uuid

@dataclass
class ParentChunk:
    parent_id: str
    document_id: str
    title: str
    text: str
    metadata: Dict


@dataclass
class ChildChunk:
    child_id: str
    parent_id: str
    document_id: str
    text: str
    metadata: Dict