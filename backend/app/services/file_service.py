import os
from fastapi import UploadFile
from ..models.document import Document
from sqlalchemy.orm import Session

class FileService:
    def __init__(self, db: Session):
        self.db = db

    async def save_file(self, file: UploadFile) -> Document:
        # 파일 내용 읽기
        content = await file.read()

        # 텍스트 파일의 경우 내용 저장
        if file.content_type == 'text/plain':
            text_content = content.decode('utf-8')
        else:
            text_content = None

        # DB에 문서 정보 저장
        doc = Document(
            name=file.filename,
            document_type='reference',
            content=text_content,
            file_metadata={'content_type': file.content_type}
        )

        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        return doc
