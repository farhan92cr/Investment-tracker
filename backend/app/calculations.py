"""
All money-math lives here, in one place, so the same rule (e.g. "SST is 15%
of brokerage") is never duplicated across routers. This mirrors the formulas
from the original spreadsheet version of this tracker.
"""
import datetime as dt
from collections import defaultdict

from sqlalchemy.orm import Session

from app import models

SST_RATE = 0.15
LEVIES_RATE = 0.06


def buy_fields(bought_price: float, units: float, brok_rate: float) -> dict:
    brok_rate = brok_rate or 0
    total_amount = bought_price * units
    brok_amount = brok_rate * units
    net_rate = bought_price + brok_rate
    sst_amount = brok_amount * SST_RATE
    levies_charges = brok_amount * LEVIES_RATE
    total_charges = brok_amount + sst_amount + levies_charges
    net_amount_paid = total_amount + total_charges
    return dict(
        total_amount=total_amount, brok_amount=brok_amount, net_rate=net_rate,
        sst_amount=sst_amount, levies_charges=levies_charges,
        total_charges=total_charges, net_amount_paid=net_amount_paid,
    )


def sold_fields(sold_price: float, units: float, brok_rate: float) -> dict:
    brok_rate = brok_rate or 0
    gross_amount = sold_price * units
    brok_amount = brok_rate * units
    sst_amount = brok_amount * SST_RATE
    levies_charges = brok_amount * LEVIES_RATE
    total_charges = brok_amount + sst_amount + levies_charges
    net_amount_received = gross_amount - total_charges
    return dict(
        gross_amount=gross_amount, brok_amount=brok_amount,
        sst_amount=sst_amount, levies_charges=levies_charges,
        total_charges=total_charges, net_amount_received=net_amount_received,
    )


def build_dashboard(db: Session, user_id: int) -> dict:
    stocks = db.query(models.Stock).filter(models.Stock.user_id == user_id).all()

    by_stock = []
    total_invested = 0.0
    total_current_value = 0.0
    total_charges_paid = 0.0
    net_received_from_sales = 0.0
    sector_totals: dict[str, float] = defaultdict(float)

    for stock in stocks:
        buys = stock.buy_transactions
        sells = stock.sold_transactions
        prices = sorted(stock.price_entries, key=lambda p: p.recorded_at)

        units_bought = sum(b.units for b in buys)
        invested = sum(buy_fields(b.bought_price, b.units, b.brok_rate)["net_amount_paid"] for b in buys)
        charges = sum(buy_fields(b.bought_price, b.units, b.brok_rate)["total_charges"] for b in buys)
        avg_cost = (invested / units_bought) if units_bought else 0.0

        units_sold = sum(s.units for s in sells)
        received = sum(sold_fields(s.sold_price, s.units, s.brok_rate)["net_amount_received"] for s in sells)

        units_remaining = units_bought - units_sold
        cost_basis_remaining = avg_cost * units_remaining

        current_price = prices[-1].price if prices else None
        current_value = current_price * units_remaining if current_price is not None else None
        gain_loss = (current_value - cost_basis_remaining) if current_value is not None else None
        gain_loss_pct = (gain_loss / cost_basis_remaining) if (gain_loss is not None and cost_basis_remaining) else None

        total_invested += invested
        total_charges_paid += charges
        net_received_from_sales += received
        if current_value is not None:
            total_current_value += current_value
        sector_totals[stock.sector] += invested

        by_stock.append(dict(
            ticker=stock.ticker, company=stock.company, sector=stock.sector,
            units_bought=units_bought, total_invested=invested, avg_cost=avg_cost,
            units_sold=units_sold, net_amount_received=received,
            units_remaining=units_remaining, cost_basis_remaining=cost_basis_remaining,
            current_price=current_price, current_value=current_value,
            unrealized_gain_loss=gain_loss, unrealized_gain_loss_pct=gain_loss_pct,
            pct_of_portfolio=None,  # filled in below once total_invested is known
        ))

    for row in by_stock:
        row["pct_of_portfolio"] = (row["total_invested"] / total_invested) if total_invested else None

    by_sector = [
        dict(sector=sector, total_invested=amount,
             pct_of_portfolio=(amount / total_invested) if total_invested else 0.0)
        for sector, amount in sector_totals.items()
    ]

    growth = _build_growth_curve(stocks)

    unrealized = total_current_value - sum(r["cost_basis_remaining"] for r in by_stock)
    cost_basis_total = sum(r["cost_basis_remaining"] for r in by_stock)
    unrealized_pct = (unrealized / cost_basis_total) if cost_basis_total else None

    return dict(
        total_invested=total_invested,
        total_current_value=total_current_value,
        unrealized_gain_loss=unrealized,
        unrealized_gain_loss_pct=unrealized_pct,
        total_charges_paid=total_charges_paid,
        net_received_from_sales=net_received_from_sales,
        holdings=len(stocks),
        sectors=len(sector_totals),
        by_stock=by_stock,
        by_sector=by_sector,
        growth=growth,
    )


def _build_growth_curve(stocks: list[models.Stock]) -> list[dict]:
    """
    One point per distinct price-entry timestamp across all of a user's
    stocks: total invested up to that date, and total current value using
    the latest known price for each stock as of that timestamp.
    """
    timestamps: set[dt.datetime] = set()
    for stock in stocks:
        for p in stock.price_entries:
            timestamps.add(p.recorded_at)

    if not timestamps:
        return []

    points = []
    for ts in sorted(timestamps):
        invested_asof = 0.0
        value_asof = 0.0
        for stock in stocks:
            buys_asof = [b for b in stock.buy_transactions if b.date_of_buy <= ts.date()]
            sells_asof = [s for s in stock.sold_transactions if s.date_of_sale <= ts.date()]
            units_bought = sum(b.units for b in buys_asof)
            units_sold = sum(s.units for s in sells_asof)
            invested = sum(buy_fields(b.bought_price, b.units, b.brok_rate)["net_amount_paid"] for b in buys_asof)
            invested_asof += invested

            prices_asof = [p for p in stock.price_entries if p.recorded_at <= ts]
            if prices_asof:
                latest_price = max(prices_asof, key=lambda p: p.recorded_at).price
                value_asof += latest_price * (units_bought - units_sold)

        points.append(dict(recorded_at=ts, total_invested=invested_asof, total_current_value=value_asof))

    return points
