from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.calculations import buy_fields, sold_fields

router = APIRouter(tags=["transactions"])


def _get_stock(db: Session, user_id: int, ticker: str) -> models.Stock:
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.user_id == user_id, models.Stock.ticker == ticker)
        .first()
    )
    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"'{ticker}' isn't in your Stock Master yet - add it there first",
        )
    return stock


def _buy_out(b: models.BuyTransaction) -> dict:
    return dict(
        id=b.id, ticker=b.stock.ticker, company=b.stock.company, sector=b.stock.sector,
        bought_price=b.bought_price, units=b.units, date_of_buy=b.date_of_buy,
        brok_rate=b.brok_rate or 0, **buy_fields(b.bought_price, b.units, b.brok_rate),
    )


def _sold_out(s: models.SoldTransaction) -> dict:
    return dict(
        id=s.id, ticker=s.stock.ticker, company=s.stock.company, sector=s.stock.sector,
        sold_price=s.sold_price, units=s.units, date_of_sale=s.date_of_sale,
        brok_rate=s.brok_rate or 0, **sold_fields(s.sold_price, s.units, s.brok_rate),
    )


# ---------- Buy ----------
@router.get("/buy-transactions", response_model=list[schemas.BuyOut])
def list_buys(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    rows = (
        db.query(models.BuyTransaction)
        .filter(models.BuyTransaction.user_id == user.id)
        .order_by(models.BuyTransaction.date_of_buy)
        .all()
    )
    return [_buy_out(b) for b in rows]


@router.post("/buy-transactions", response_model=schemas.BuyOut, status_code=201)
def add_buy(
    payload: schemas.BuyCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    stock = _get_stock(db, user.id, payload.ticker)
    row = models.BuyTransaction(
        user_id=user.id, stock_id=stock.id,
        bought_price=payload.bought_price, units=payload.units,
        date_of_buy=payload.date_of_buy, brok_rate=payload.brok_rate or 0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _buy_out(row)


@router.delete("/buy-transactions/{row_id}", status_code=204)
def delete_buy(row_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    row = db.query(models.BuyTransaction).filter(
        models.BuyTransaction.id == row_id, models.BuyTransaction.user_id == user.id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Buy transaction not found")
    db.delete(row)
    db.commit()


# ---------- Sold ----------
@router.get("/sold-transactions", response_model=list[schemas.SoldOut])
def list_sold(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    rows = (
        db.query(models.SoldTransaction)
        .filter(models.SoldTransaction.user_id == user.id)
        .order_by(models.SoldTransaction.date_of_sale)
        .all()
    )
    return [_sold_out(s) for s in rows]


@router.post("/sold-transactions", response_model=schemas.SoldOut, status_code=201)
def add_sold(
    payload: schemas.SoldCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    stock = _get_stock(db, user.id, payload.ticker)
    row = models.SoldTransaction(
        user_id=user.id, stock_id=stock.id,
        sold_price=payload.sold_price, units=payload.units,
        date_of_sale=payload.date_of_sale, brok_rate=payload.brok_rate or 0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _sold_out(row)


@router.delete("/sold-transactions/{row_id}", status_code=204)
def delete_sold(row_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    row = db.query(models.SoldTransaction).filter(
        models.SoldTransaction.id == row_id, models.SoldTransaction.user_id == user.id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Sold transaction not found")
    db.delete(row)
    db.commit()
