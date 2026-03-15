from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import eingine, Base
from app.routers import expenses,summary, auth

Base.metadata.create_all(bind=eingine)

app = FastAPI(
    tittle= "Personal Finance Tracker",
    description= "Track your expenses and get monthly spending insights",
    version= "1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(expenses.router)
app.include_router(summary.router)

app.include_router(auth.router)

@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard():
    return FileResponse("static/dashboard.html")
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Personal Finance Tracker API",
        "docs" : "/docs",
        "dashboard" : "/dashboard",
    }

#Was diese Datei macht

"""
Base.metadata.create_all(bind=eingine) - beim Start wird automatisch die 'finance.db' Datei erstellt und alle Tabellen angelegt die ich in 'models.py' definiert habe
app = FastAPI(...) das ist die gesamte Anwendung. Alles hängt daran
app.include_router(...)  die Router aus 'expenses.py' und 'summary.py' werden eingehängt. FastAPI kennt jetzt alle Endpoints
def root() der einfachste Endpoint gibt eine Begrüßung zurück wenn man '/' aufruft
"""