from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import schemas, crud
from app.auth_utils import verify_password, get_password_hash, create_access_token, verify_token
from app.database import get_db
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str, db: Session = Depends(get_db)):
    print(token)
    payload = verify_token(token.split("Bearer ")[1])
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.get("/signup")
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/register", response_model=schemas.User)
def register_user(
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
        response: Response = None):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered")

    hashed_password = get_password_hash(password)
    user_data = schemas.UserCreate(email=email, password=hashed_password)
    created_user = crud.create_user(db=db, user=user_data)

    access_token = create_access_token(data={"sub": email})

    response = RedirectResponse(
        url="/landing",
        status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=True)

    return response


@router.post("/token", response_model=dict)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
        response: Response = None):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(
            form_data.password,
            user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email},
        expires_delta=access_token_expires)

    response = RedirectResponse(
        url="/landing",
        status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=True)

    return response


@router.get("/users/me", response_model=schemas.User)
def read_users_me(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):
    return get_current_user(token=token, db=db)


@router.get("/reset-password")
def reset_password_form(request: Request):
    return templates.TemplateResponse(
        "reset_password.html", {
            "request": request})


@router.post("/reset-password")
def reset_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found")

    reset_token = create_access_token(
        data={
            "sub": user.email},
        expires_delta=timedelta(
            hours=1))
    reset_link = f"http://localhost:8000/change-password?token={reset_token}&email={email}"

    print(f"Reset link: {reset_link}")
    return {"message": "Reset link has been sent to your email."}


@router.get("/change-password")
def change_password_form(token: str, email: str, request: Request):
    return templates.TemplateResponse(
        "change_password.html", {
            "request": request, "token": token, "email": email})


@router.post("/change-password")
def change_password(
        token: str = Form(...),
        email: str = Form(...),
        new_password: str = Form(...),
        db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload or payload.get("sub") != email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token")

    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
