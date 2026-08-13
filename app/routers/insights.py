from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app import models, schemas

router = APIRouter(prefix="/insights", tags=["insights"], dependencies=[Depends(verify_token)])


@router.post("/")
def create_insight(payload: schemas.AIInsightIn, db: Session = Depends(get_db)):
    row = models.AIInsight(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.get("/")
def list_insights(scope: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.AIInsight).order_by(models.AIInsight.generated_at.desc())
    if scope:
        q = q.filter(models.AIInsight.scope == scope)
    rows = q.limit(limit).all()
    return [
        {"id": r.id, "scope": r.scope, "content": r.content, "generated_at": r.generated_at}
        for r in rows
    ]
