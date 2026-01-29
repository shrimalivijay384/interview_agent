"""
CV Upload and Management Routes
"""
import logging
import os
import json
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import PyPDF2
import docx
import io
from ..services.jd_generator import generate_jd_from_cv

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv", tags=["cv"])

# Storage directory for CVs
CV_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cvs')
os.makedirs(CV_STORAGE_DIR, exist_ok=True)


class CVResponse(BaseModel):
    """Response model for CV operations"""
    success: bool
    message: str
    cv_id: Optional[str] = None
    parsed_data: Optional[dict] = None


class CVListItem(BaseModel):
    """CV list item"""
    cv_id: str
    name: str
    email: Optional[str] = None
    uploaded_at: str
    file_size: int


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_doc(file_content: bytes) -> str:
    """Extract text from DOC file (fallback to plain text)"""
    try:
        # Try to decode as plain text
        text = file_content.decode('utf-8', errors='ignore')
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOC: {e}")
        raise ValueError(f"Failed to extract text from DOC: {str(e)}")


def parse_cv_text(text: str) -> dict:
    """Parse CV text into structured data (basic parsing)"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    parsed = {
        "raw_text": text,
        "name": "",
        "email": "",
        "phone": "",
        "summary": "",
        "work_experience": [],
        "education": [],
        "skills": [],
        "parsed_at": datetime.utcnow().isoformat()
    }
    
    # Try to extract basic info from first few lines
    if lines:
        parsed["name"] = lines[0]  # Assume first line is name
        
        # Look for email and phone in first 5 lines
        for line in lines[:5]:
            if '@' in line and not parsed["email"]:
                parsed["email"] = line
            elif any(char.isdigit() for char in line) and not parsed["phone"]:
                # Simple phone detection
                import re
                phone_match = re.search(r'[\d\-\+\(\)\s]{10,}', line)
                if phone_match:
                    parsed["phone"] = phone_match.group(0).strip()
    
    return parsed


@router.post("/upload", response_model=CVResponse)
async def upload_cv(
    file: Optional[UploadFile] = File(None),
    cv_text: Optional[str] = Form(None)
):
    """
    Upload a CV either as a file or as text.
    Supports PDF, DOCX, DOC, and TXT formats.
    """
    try:
        if not file and not cv_text:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a file or CV text"
            )
        
        # Extract text from file or use provided text
        if file:
            file_content = await file.read()
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file_content)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file_content)
            elif filename.endswith('.doc'):
                text = extract_text_from_doc(file_content)
            elif filename.endswith('.txt'):
                text = file_content.decode('utf-8', errors='ignore').strip()
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Please use PDF, DOCX, DOC, or TXT"
                )
            
            logger.info(f"Extracted text from {filename}: {len(text)} characters")
        else:
            text = cv_text
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="CV text is too short or empty"
            )
        
        # Parse the CV
        parsed_data = parse_cv_text(text)
        
        # Generate CV ID
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        cv_id = f"cv_{timestamp}"
        
        # Save to storage
        cv_file_path = os.path.join(CV_STORAGE_DIR, f"{cv_id}.json")
        with open(cv_file_path, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        
        # Add to RAG vector store
        try:
            from ..services.rag_knowledge_base import get_rag_knowledge_base
            rag = get_rag_knowledge_base()
            rag.add_candidate(cv_id, parsed_data)
            logger.info(f"CV added to RAG vector store: {cv_id}")
        except Exception as e:
            logger.warning(f"Failed to add CV to RAG: {str(e)}")
            # Don't fail the upload if RAG addition fails
        
        logger.info(f"CV saved successfully: {cv_id}")
        
        return CVResponse(
            success=True,
            message="CV uploaded and parsed successfully",
            cv_id=cv_id,
            parsed_data=parsed_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload CV: {str(e)}"
        )


@router.get("/list")
async def list_cvs():
    """List all uploaded CVs"""
    try:
        cvs = []
        
        if not os.path.exists(CV_STORAGE_DIR):
            return {"success": True, "cvs": []}
        
        for filename in os.listdir(CV_STORAGE_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(CV_STORAGE_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    cv_id = filename.replace('.json', '')
                    file_stats = os.stat(file_path)
                    
                    # Handle different CV data structures
                    name = data.get("name", "Unknown")
                    email = data.get("email", "")
                    
                    # Check if data has parsed_data field (demo CVs)
                    if "parsed_data" in data and isinstance(data["parsed_data"], dict):
                        name = data["parsed_data"].get("name", name)
                        email = data["parsed_data"].get("email", email)
                    
                    cvs.append({
                        "cv_id": cv_id,
                        "name": name,
                        "email": email,
                        "uploaded_at": data.get("parsed_at", data.get("uploaded_at", datetime.fromtimestamp(file_stats.st_mtime).isoformat())),
                        "file_size": file_stats.st_size
                    })
                except Exception as e:
                    logger.error(f"Error reading CV {filename}: {e}")
                    continue
        
        # Sort by upload time (newest first)
        cvs.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return {"success": True, "cvs": cvs}
        
    except Exception as e:
        logger.error(f"Error listing CVs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list CVs: {str(e)}"
        )


@router.get("/{cv_id}")
async def get_cv(cv_id: str):
    """Get a specific CV by ID"""
    try:
        cv_file_path = os.path.join(CV_STORAGE_DIR, f"{cv_id}.json")
        
        if not os.path.exists(cv_file_path):
            raise HTTPException(status_code=404, detail="CV not found")
        
        with open(cv_file_path, 'r') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "cv_id": cv_id,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving CV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve CV: {str(e)}"
        )


@router.delete("/{cv_id}")
async def delete_cv(cv_id: str):
    """Delete a CV by ID"""
    try:
        cv_file_path = os.path.join(CV_STORAGE_DIR, f"{cv_id}.json")
        
        if not os.path.exists(cv_file_path):
            raise HTTPException(status_code=404, detail="CV not found")
        
        os.remove(cv_file_path)
        logger.info(f"CV deleted: {cv_id}")
        
        return {
            "success": True,
            "message": "CV deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete CV: {str(e)}"
        )


@router.post("/{cv_id}/generate-jd")
async def generate_jd_for_cv(cv_id: str):
    """
    Generate a suitable job description based on the CV.
    This JD can then be used to start an interview.
    """
    try:
        # Get CV data
        cv_file_path = os.path.join(CV_STORAGE_DIR, f"{cv_id}.json")
        
        if not os.path.exists(cv_file_path):
            raise HTTPException(status_code=404, detail="CV not found")
        
        with open(cv_file_path, 'r') as f:
            cv_data = json.load(f)
        
        logger.info(f"Generating JD for CV: {cv_id}")
        
        # Generate JD using the service
        jd_text = await generate_jd_from_cv(cv_data)
        
        return {
            "success": True,
            "cv_id": cv_id,
            "jd_text": jd_text,
            "message": "Job description generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating JD: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate job description: {str(e)}"
        )

