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


DEMO_PORTFOLIO = {
    "total_invested": 389745,
    "total_current_value": 391885,
    "unrealized_gain_loss": 2140,
    "unrealized_gain_loss_pct": 0.55,
    "holdings": [
        {"ticker": "FFC", "invested": 50231, "current_value": 52400},
        {"ticker": "OGDC", "invested": 32808, "current_value": 31600},
        {"ticker": "MARI", "invested": 90600, "current_value": 96200},
        {"ticker": "LUCK", "invested": 37936, "current_value": 36900},
    ],
    "sectors": [
        {"name": "Fertilizer", "value": 50231},
        {"name": "Oil & Gas", "value": 103928},
        {"name": "Tech", "value": 20263},
        {"name": "ETFs", "value": 158189},
    ],
}


@router.post("/demo-chat")
def ai_demo_chat(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    try:
        prompt = f"""
You are a demo AI investment assistant for a PSX portfolio tracking application.

This is SAMPLE portfolio data for demonstration only:

{json.dumps(DEMO_PORTFOLIO, indent=2)}

Visitor's question:
{request.message}

Answer the visitor's actual question directly.

Important:
- You are a general-purpose AI investment assistant.
- Answer general questions normally, including questions about investing, personal finance, PSX, stocks, economics, technology, DevOps, or other general topics.
- Do NOT automatically discuss, summarize, or mention the sample portfolio.
- Use the sample portfolio only when the visitor specifically asks about the demo/sample portfolio or when the sample numbers are directly relevant to the question.
- If the visitor asks about a specific stock or market topic, answer using the information available to you.
- Do not invent current/live prices, market movements, or other unavailable facts.
- If real-time information is required but not available, clearly say that live data is not available.
- Use sample portfolio numbers accurately when they are relevant.
- Do not invent portfolio data.
- If information needed to answer is not available, say so clearly.
- Do not present your response as guaranteed financial advice.
- Keep answers concise, useful, and beginner-friendly.
"""

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return {
            "answer": response.text
        }

    except Exception as e:
	print(f"AI service error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=502,
            detail="AI service is temporarily unavailable because the daily AI limit has been reached. Please try again later."
        )


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

Answer the user's actual question directly.

Important:
- You are a general-purpose AI investment assistant.
- Answer general questions normally, including questions about investing, personal finance, PSX, stocks, economics, technology, DevOps, or other general topics.
- Use the authenticated user's portfolio data only when the question is about the user's portfolio, holdings, transactions, performance, allocation, gains/losses, or another portfolio-specific matter.
- Do NOT automatically summarize or mention the user's portfolio for general questions.
- If the user asks about a specific stock or market topic, answer using the information available to you.
- Do not invent current/live prices, market movements, or other unavailable facts.
- If real-time information is required but not available, clearly say that live data is not available.
- Use the provided portfolio numbers accurately when they are relevant.
- Do not invent portfolio data.
- If information needed to answer is not available, say so clearly.
- Do not present your response as guaranteed financial advice.
- Keep answers concise, useful, and beginner-friendly.
"""

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
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
