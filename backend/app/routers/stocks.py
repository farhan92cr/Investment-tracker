from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=list[schemas.StockOut])
def list_stocks(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Stock).filter(models.Stock.user_id == user.id).order_by(models.Stock.id).all()


@router.post("", response_model=schemas.StockOut, status_code=201)
def add_stock(
    payload: schemas.StockCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    existing = (
        db.query(models.Stock)
        .filter(models.Stock.user_id == user.id, models.Stock.ticker == payload.ticker)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail=f"{payload.ticker} is already in your Stock Master")

    stock = models.Stock(user_id=user.id, **payload.model_dump())
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.delete("/{stock_id}", status_code=204)
def delete_stock(
    stock_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    stock = db.query(models.Stock).filter(models.Stock.id == stock_id, models.Stock.user_id == user.id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    db.delete(stock)
    db.commit()
