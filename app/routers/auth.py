from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.testing.pickleable import User

from app.database import get_db
from app import models

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "dein-super-geheimer-schluessel-bitte-aendern"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


"""
SECRET_KEY damit werden Tokens signiert. Nur der Server kennt diesen Key
ALGORITHM HS256 ist der Standard für JWT
pwd_context bcrypt hasht passwörter sicher - niemals Passwörter Klartext speichern
oauth2_scheme sagt FastAPI wo der Token abgeholt wird (/auth/token)
"""

#Hilfsfunktionen
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ungeultig oder abgelaufen",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

"""
verify_password vergleicht eingegebenes PW mit dem Hash in der DB
get_password_hash wandelt Klartext in einen sicheren Hash um
create_access_token bait einen JWT Token mit Abluafzeit
authenticate_user prueft ob Username+PW korrekt sind
get_current_user liest den Token aus dem Request und gibt den eingeloggten User zurueck
"""

#Endpoints
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username bereits vergeben")

    hashed = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password = hashed)
    db.add(new_user)
    db.commit()
    return {"message": f"User '{user.username}' erfolgreich registriert"}


@router.post("/token")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Username oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "id" : current_user.id}

"""
POST /auth/register — neuen User anlegen, Passwort wird sofort gehasht
POST /auth/token — Login, gibt einen JWT Token zurück
GET /auth/me — gibt den aktuell eingeloggten User zurück — nur mit gültigem Token
"""