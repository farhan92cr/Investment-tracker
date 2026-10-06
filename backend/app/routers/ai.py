import os
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from google import genai
from sqlalchemy.orm import Session

from app import auth, models
from app.calculations import build_dashboard
from app.database import get_db


router = APIRouter(prefix="/ai", tags=["AI"])


class ChatRequest(BaseModel):
    message: str


@router.get("/test")
def ai_test():
    return {"message": "AI router is working"}


def build_ai_portfolio_summary(db: Session, user_id: int) -> dict:
    dashboard = build_dashboard(db, user_id)

    return {
        "total_invested": dashboard["total_invested"],
        "total_current_value": dashboard["total_current_value"],
        "unrealized_gain_loss": dashboard["unrealized_gain_loss"],
        "unrealized_gain_loss_pct": dashboard["unrealized_gain_loss_pct"],
        "total_charges_paid": dashboard["total_charges_paid"],
        "net_received_from_sales": dashboard["net_received_from_sales"],
        "holdings": dashboard["holdings"],
        "sectors": dashboard["sectors"],
        "by_stock": dashboard["by_stock"],
        "by_sector": dashboard["by_sector"],
    }


@router.get("/portfolio")
def ai_portfolio(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    return build_ai_portfolio_summary(db, user.id)


@router.post("/chat")
def ai_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    try:
        portfolio = build_ai_portfolio_summary(db, user.id)

        prompt = f"""
You are an AI investment assistant.

The following is the authenticated user's portfolio data:

{json.dumps(portfolio, indent=2, default=str)}

User's question:
{request.message}

Answer the user's question using the portfolio data above.

Important:
- Use the provided portfolio numbers accurately.
- Explain calculations in simple language when useful.
- Do not invent portfolio data.
- If the question requires information that is not present, clearly say that the information is not available.
- Do not present your response as guaranteed financial advice.
"""

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return {
            "answer": response.text
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(e)}"
        )