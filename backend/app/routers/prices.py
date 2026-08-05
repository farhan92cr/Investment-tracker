import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=list[schemas.PriceOut])
def list_prices(
    ticker: str | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.PriceEntry).join(models.Stock).filter(models.Stock.user_id == user.id)
    if ticker:
        q = q.filter(models.Stock.ticker == ticker)
    rows = q.order_by(models.PriceEntry.recorded_at.desc()).all()
    return [
        schemas.PriceOut(id=r.id, ticker=r.stock.ticker, price=r.price,
                          recorded_at=r.recorded_at, source=r.source)
        for r in rows
    ]


@router.get("/latest", response_model=list[schemas.PriceOut])
def latest_prices(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    """One row per stock: its most recently recorded price - the 'reference board'."""
    stocks = db.query(models.Stock).filter(models.Stock.user_id == user.id).all()
    out = []
    for stock in stocks:
        latest = max(stock.price_entries, key=lambda p: p.recorded_at, default=None)
        if latest:
            out.append(schemas.PriceOut(
                id=latest.id, ticker=stock.ticker, price=latest.price,
                recorded_at=latest.recorded_at, source=latest.source,
            ))
    return out


@router.post("", response_model=schemas.PriceOut, status_code=201)
def add_price(
    payload: schemas.PriceCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.user_id == user.id, models.Stock.ticker == payload.ticker)
        .first()
    )
    if not stock:
        raise HTTPException(status_code=404, detail=f"'{payload.ticker}' isn't in your Stock Master yet")

    row = models.PriceEntry(
        user_id=user.id, stock_id=stock.id, price=payload.price,
        recorded_at=payload.recorded_at or dt.datetime.utcnow(), source="manual",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.PriceOut(id=row.id, ticker=stock.ticker, price=row.price,
                             recorded_at=row.recorded_at, source=row.source)
