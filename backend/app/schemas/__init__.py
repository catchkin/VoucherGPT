# schemas/__init__.py
from .base import BaseSchema
from .company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyInDB,
    CompanyWithRelations
)
from .document import (
    DocumentType,
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentInDB
)
from .section import (
    SectionType,
    SectionBase,
    SectionCreate,
    SectionUpdate,
    SectionInDB
)
from .chat import (
    ChatHistoryBase,
    ChatHistoryCreate,
    ChatHistoryInDB,
    ChatReferenceBase,
    ChatReferenceCreate,
    ChatReferenceInDB,
    ChatFeedbackBase,
    ChatFeedbackCreate,
    ChatFeedbackInDB
)

# 순환 참조 해결을 위한 모델 재빌드
CompanyWithRelations.model_rebuild()

__all__ = [
    'BaseSchema',
    # Company schemas
    'CompanyBase',
    'CompanyCreate',
    'CompanyUpdate',
    'CompanyInDB',
    'CompanyWithRelations',
    # Document schemas
    'DocumentType',
    'DocumentBase',
    'DocumentCreate',
    'DocumentUpdate',
    'DocumentInDB',
    # Section schemas
    'SectionType',
    'SectionBase',
    'SectionCreate',
    'SectionUpdate',
    'SectionInDB',
    # Chat schemas
    'ChatHistoryBase',
    'ChatHistoryCreate',
    'ChatHistoryInDB',
    'ChatReferenceBase',
    'ChatReferenceCreate',
    'ChatReferenceInDB',
    'ChatFeedbackBase',
    'ChatFeedbackCreate',
    'ChatFeedbackInDB'
]
