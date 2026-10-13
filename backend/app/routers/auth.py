
import datetime as dt
import hashlib
import secrets
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

VERIFICATION_HOURS = 24
PASSWORD_RESET_MINUTES = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.smtp_username or not settings.smtp_password:
        raise HTTPException(
            status_code=503,
            detail="Email service is not configured yet.",
        )

    message = EmailMessage()
    message["From"] = settings.email_from or settings.smtp_username
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to send email right now. Please try again later.",
        )


def _send_verification_email(user: models.User, db: Session) -> None:
    token = secrets.token_urlsafe(32)
    user.verification_token_hash = _hash_token(token)
    user.verification_token_expires_at = (
        dt.datetime.utcnow() + dt.timedelta(hours=VERIFICATION_HOURS)
    )
    db.commit()

    link = (
        f"{settings.frontend_url.rstrip('/')}/verify-email"
        f"?token={token}&email={user.email}"
    )
    _send_email(
        user.email,
        "Verify your ShariahMate email",
        f"Welcome to ShariahMate!\n\n"
        f"Verify your email using this link:\n{link}\n\n"
        f"This link expires in {VERIFICATION_HOURS} hours.",
    )


@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists",
        )

    user = models.User(
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _send_verification_email(user, db)
    return user


@router.get("/verify-email")
def verify_email(token: str, email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.is_verified:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    if (
        not user.verification_token_hash
        or not user.verification_token_expires_at
        or user.verification_token_expires_at < dt.datetime.utcnow()
        or not secrets.compare_digest(
            user.verification_token_hash, _hash_token(token)
        )
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user.is_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None
    db.commit()
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in.",
        )

    token = auth.create_access_token(subject=str(user.id))
    return schemas.Token(access_token=token)


@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    # Always return the same response to avoid revealing registered addresses.
    if user and user.is_verified:
        token = secrets.token_urlsafe(32)
        user.password_reset_token_hash = _hash_token(token)
        user.password_reset_token_expires_at = (
            dt.datetime.utcnow() + dt.timedelta(minutes=PASSWORD_RESET_MINUTES)
        )
        db.commit()

        link = (
            f"{settings.frontend_url.rstrip('/')}/reset-password"
            f"?token={token}&email={user.email}"
        )
        _send_email(
            user.email,
            "Reset your ShariahMate password",
            f"Use this link to reset your password:\n{link}\n\n"
            f"This link expires in {PASSWORD_RESET_MINUTES} minutes.",
        )

    return {"message": "If that email is registered, password reset instructions will be sent."}


@router.post("/reset-password")
def reset_password(
    payload: schemas.PasswordReset,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if (
        not user
        or not user.password_reset_token_hash
        or not user.password_reset_token_expires_at
        or user.password_reset_token_expires_at < dt.datetime.utcnow()
        or not secrets.compare_digest(
            user.password_reset_token_hash, _hash_token(payload.token)
        )
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired password reset link")

    user.hashed_password = auth.hash_password(payload.new_password)
    user.password_reset_token_hash = None
    user.password_reset_token_expires_at = None
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
