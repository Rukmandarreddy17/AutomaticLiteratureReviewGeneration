from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import research as research_schema
from app.services.research import research_client

router = APIRouter()

@router.post("/search", response_model=research_schema.ResearchResponse)
async def search_papers(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    request: research_schema.ResearchRequest,
) -> Any:
    try:
        papers = await research_client.search(request.query, max_results=request.max_results)
        return {"papers": papers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research engine error: {str(e)}")

class AnalyzeRequest(BaseModel):
    idea: str
    abstract: str

@router.post("/analyze")
async def analyze_research(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    request: AnalyzeRequest,
) -> Any:
    # 1. Search Papers
    papers = await research_client.search(request.idea, max_results=5)
    
    # 2. Extract Text (Optional - for this MVP we use abstracts to save time/bandwidth)
    # Ideally: for p in papers: if p.pdf_url: text = doc_processor.download_and_extract(p.pdf_url)
    
    # 3. Generate Report
    from app.services.ai import ai_service
    report_content = await ai_service.generate_report(request.idea, request.abstract, papers)
    
    # 4. Save as new Chat
    from app.db.models import Chat, Message
    from datetime import datetime
    
    # Update Chat title logic
    chat_title = request.idea[:50]
    new_chat = Chat(title=chat_title, user_id=current_user.id, created_at=datetime.utcnow().isoformat())
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    # Save User Message
    msg_user = Message(chat_id=new_chat.id, sender="user", content=f"Idea: {request.idea}\nAbstract: {request.abstract}", timestamp=datetime.utcnow().isoformat())
    db.add(msg_user)
    
    # Save AI Report as Message
    msg_ai = Message(chat_id=new_chat.id, sender="ai", content=report_content, timestamp=datetime.utcnow().isoformat())
    db.add(msg_ai)
    
    db.commit()
    
    return {
        "chat_id": new_chat.id,
        "report": report_content,
        "papers": papers
    }
