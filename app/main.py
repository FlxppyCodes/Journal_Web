from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import daily, planning, finance, insights, analytics, journal

# Creates tables if they don't exist. Fine for a single-user app;
# swap for Alembic migrations if the schema starts changing often.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Journal API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://journal-web-g0i7.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(daily.router)
app.include_router(planning.router)
app.include_router(finance.router)
app.include_router(insights.router)
app.include_router(analytics.router)
app.include_router(journal.router)


@app.get("/health")
def health():
    return {"status": "ok"}
