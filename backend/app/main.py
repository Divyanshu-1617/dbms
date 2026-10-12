from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_database, DB_PATH
from .routes import auth, locations, vehicles, bookings, payments, inspections, incidents, maintenance, admin

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database initialized
    if not DB_PATH.exists():
        init_database(seed=True)
    yield

app = FastAPI(
    title="Peer-to-Peer Tourist Bike Rental Management System",
    description="A database-driven platform API implementing the 8-entity DBMS schema and 12 business lifecycle scenarios.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(vehicles.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(inspections.router)
app.include_router(incidents.router)
app.include_router(maintenance.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    return {
        "system": "Peer-to-Peer Tourist Bike Rental Management System",
        "phase": "Phase 1 - Backend & DBMS Core",
        "status": "Operational",
        "docs_url": "/docs",
        "entities": [
            "USER", "LOCATION", "VEHICLE", "BOOKING",
            "PAYMENT", "INSPECTION", "DAMAGE_PENALTY", "MAINTENANCE"
        ],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database_connected": DB_PATH.exists()}
