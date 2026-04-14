import zipfile
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional
from xml.etree import ElementTree as ET

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.resume_agent import analyze_resume_text

RESUMES_COLLECTION = "resumes"


def _extract_text_from_docx(raw_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(raw_bytes)) as docx_zip:
            with docx_zip.open("word/document.xml") as document_xml:
                tree = ET.parse(document_xml)
                root = tree.getroot()
                paragraphs = []
                for paragraph in root.iter():
                    if paragraph.tag.endswith("}p"):
                        texts = [node.text for node in paragraph.iter() if node.text]
                        if texts:
                            paragraphs.append("".join(texts))
                return "\n".join(paragraphs).strip()
    except Exception:
        return ""


def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return ""

    try:
        reader = PdfReader(BytesIO(raw_bytes))
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text).strip()
    except Exception:
        return ""


async def extract_resume_text(file: UploadFile, text: Optional[str] = None) -> str:
    if text and text.strip():
        return text.strip()

    raw_bytes = await file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        return _extract_text_from_pdf(raw_bytes)
    if filename.endswith(".docx"):
        return _extract_text_from_docx(raw_bytes)

    try:
        return raw_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return raw_bytes.decode("latin-1").strip()
        except Exception:
            return ""


async def analyze_and_store_resume(
    db: AsyncIOMotorDatabase,
    text: Optional[str] = None,
    file: Optional[UploadFile] = None,
    user_id: str = "default_user",
) -> Dict[str, Any]:
    resume_text = text.strip() if text else ""
    if file is not None:
        resume_text = await extract_resume_text(file, resume_text)

    analysis = await analyze_resume_text(resume_text)
    document: Dict[str, Any] = {
        "user_id": user_id,
        "resume_text": resume_text,
        "analysis": analysis,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[RESUMES_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
