import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    stocks = relationship("Stock", back_populates="owner", cascade="all, delete-orphan")


class Stock(Base):
    """Equivalent of a Stock Master row: one ticker a user tracks."""
    __tablename__ = "stocks"
    __table_args__ = (UniqueConstraint("user_id", "ticker", name="uq_user_ticker"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    owner = relationship("User", back_populates="stocks")
    buy_transactions = relationship("BuyTransaction", back_populates="stock", cascade="all, delete-orphan")
    sold_transactions = relationship("SoldTransaction", back_populates="stock", cascade="all, delete-orphan")
    price_entries = relationship("PriceEntry", back_populates="stock", cascade="all, delete-orphan")


class BuyTransaction(Base):
    """Equivalent of a Buy Transactions row."""
    __tablename__ = "buy_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    bought_price = Column(Float, nullable=False)
    units = Column(Float, nullable=False)
    date_of_buy = Column(Date, nullable=False)
    brok_rate = Column(Float, nullable=True, default=0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    stock = relationship("Stock", back_populates="buy_transactions")


class SoldTransaction(Base):
    """Equivalent of a Sold Transactions row."""
    __tablename__ = "sold_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    sold_price = Column(Float, nullable=False)
    units = Column(Float, nullable=False)
    date_of_sale = Column(Date, nullable=False)
    brok_rate = Column(Float, nullable=True, default=0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    stock = relationship("Stock", back_populates="sold_transactions")


class PriceEntry(Base):
    """
    Equivalent of Current Prices, but append-only with a real timestamp so
    multiple updates per day are all kept (this is what draws the growth curve).
    """
    __tablename__ = "price_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=dt.datetime.utcnow, index=True)
    source = Column(String, default="manual")  # "manual" or "auto" (phase 2)

    stock = relationship("Stock", back_populates="price_entries")
