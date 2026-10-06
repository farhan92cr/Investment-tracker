import datetime as dt

import psxdata
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

PUBLIC_TICKERS = ["FFC", "OGDC", "MARI", "LUCK", "SYS"]


@router.get("/public-latest")
def public_latest_prices():
    """Latest public PSX prices for the landing-page ticker."""
    results = []

    for ticker in PUBLIC_TICKERS:
        try:
            quote = psxdata.quote(ticker)

            if quote.empty:
                continue

            raw_price = quote.iloc[0].get("price")

            if raw_price is None:
                continue

            price = float(raw_price)

            if price <= 0:
                continue

            results.append({
                "ticker": ticker,
                "price": price,
            })

        except Exception:
            continue

    return results


@router.post("/update-market")
def update_market_prices(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    stocks = db.query(models.Stock).filter(models.Stock.user_id == user.id).all()

    if not stocks:
        raise HTTPException(
            status_code=404,
            detail="No stocks found in your Stock Master"
        )

    results = []

    for stock in stocks:
        try:
            quote = psxdata.quote(stock.ticker)

            # PSX returned no data
            if quote.empty:
                results.append({
                    "ticker": stock.ticker,
                    "status": "failed",
                    "reason": "No market data returned by PSX",
                })
                continue

            # Get the price from the quote
            raw_price = quote.iloc[0].get("price")

            # Price is missing
            if raw_price is None:
                results.append({
                    "ticker": stock.ticker,
                    "status": "failed",
                    "reason": "Price was not returned by PSX",
                })
                continue

            # Make sure the price is a valid number
            try:
                price = float(raw_price)
            except (TypeError, ValueError):
                results.append({
                    "ticker": stock.ticker,
                    "status": "failed",
                    "reason": f"Invalid price returned by PSX: {raw_price}",
                })
                continue

            # Don't save zero or negative prices
            if price <= 0:
                results.append({
                    "ticker": stock.ticker,
                    "status": "failed",
                    "reason": f"Invalid price returned by PSX: {price}",
                })
                continue

            # Only valid prices reach the database
            row = models.PriceEntry(
                user_id=user.id,
                stock_id=stock.id,
                price=price,
                recorded_at=dt.datetime.utcnow(),
                source="psx",
            )

            db.add(row)

            results.append({
                "ticker": stock.ticker,
                "status": "updated",
                "price": price,
                "source": "psx",
            })

        except Exception as e:
            results.append({
                "ticker": stock.ticker,
                "status": "failed",
                "reason": str(e),
            })

    db.commit()

    updated_count = sum(
        1 for result in results
        if result["status"] == "updated"
    )

    failed_count = sum(
        1 for result in results
        if result["status"] == "failed"
    )

    return {
        "message": "Market price update completed",
        "updated_count": updated_count,
        "failed_count": failed_count,
        "results": results,
    }

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
