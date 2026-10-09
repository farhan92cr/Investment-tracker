from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.calculations import build_dashboard

router = APIRouter(tags=["summary"])


@router.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return build_dashboard(db, user.id)
