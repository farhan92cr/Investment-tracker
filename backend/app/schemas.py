import datetime as dt
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Stock Master ----------
class StockCreate(BaseModel):
    ticker: str
    company: str
    sector: str


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticker: str
    company: str
    sector: str


# ---------- Buy transactions ----------
class BuyCreate(BaseModel):
    ticker: str
    bought_price: float
    units: float
    date_of_buy: dt.date
    brok_rate: Optional[float] = 0


class BuyOut(BaseModel):
    id: int
    ticker: str
    company: str
    sector: str
    bought_price: float
    units: float
    date_of_buy: dt.date
    brok_rate: float
    total_amount: float
    brok_amount: float
    net_rate: float
    sst_amount: float
    levies_charges: float
    total_charges: float
    net_amount_paid: float


# ---------- Sold transactions ----------
class SoldCreate(BaseModel):
    ticker: str
    sold_price: float
    units: float
    date_of_sale: dt.date
    brok_rate: Optional[float] = 0


class SoldOut(BaseModel):
    id: int
    ticker: str
    company: str
    sector: str
    sold_price: float
    units: float
    date_of_sale: dt.date
    brok_rate: float
    gross_amount: float
    brok_amount: float
    sst_amount: float
    levies_charges: float
    total_charges: float
    net_amount_received: float


# ---------- Price entries ----------
class PriceCreate(BaseModel):
    ticker: str
    price: float
    recorded_at: Optional[dt.datetime] = None


class PriceOut(BaseModel):
    id: int
    ticker: str
    price: float
    recorded_at: dt.datetime
    source: str


# ---------- Summary / Dashboard ----------
class StockSummary(BaseModel):
    ticker: str
    company: str
    sector: str
    units_bought: float
    total_invested: float
    avg_cost: float
    units_sold: float
    net_amount_received: float
    units_remaining: float
    cost_basis_remaining: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    unrealized_gain_loss: Optional[float] = None
    unrealized_gain_loss_pct: Optional[float] = None
    pct_of_portfolio: Optional[float] = None


class SectorSummary(BaseModel):
    sector: str
    total_invested: float
    pct_of_portfolio: float


class ValuationPoint(BaseModel):
    recorded_at: dt.datetime
    total_invested: float
    total_current_value: float


class DashboardOut(BaseModel):
    total_invested: float
    total_current_value: float
    unrealized_gain_loss: float
    unrealized_gain_loss_pct: Optional[float]
    total_charges_paid: float
    net_received_from_sales: float
    holdings: int
    sectors: int
    by_stock: list[StockSummary]
    by_sector: list[SectorSummary]
    growth: list[ValuationPoint]
