from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict
from uuid import uuid4, UUID
from datetime import datetime, timezone
import re

app = FastAPI(title="TRACE Ingestion API")

# In-memory store: {farmer_id: farm_record}
db_farms: Dict[str, dict] = {}


# Custom exception handler to provide field-level granularity for the Mobile App UI
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {".".join(str(loc) for loc in err["loc"][1:]): err["msg"] for err in exc.errors()}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors}
    )


class FarmRegistration(BaseModel):
    farmer_name: str = Field(..., min_length=2, max_length=100, description="Farmer name")
    farmer_id: str = Field(..., description="Unique national ID format: NG-XXXXXXXXXX")
    latitude: float = Field(..., ge=-90, le=90, description="Valid GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Valid GPS longitude")
    farm_size_hectares: float = Field(..., gt=0, lt=10000, description="Farm size must be positive and < 10000")
    commodity: Literal["cocoa", "cashew", "coffee", "shea", "sesame"]
    agent_id: str = Field(..., min_length=1, description="Field agent identifier")
    submitted_at: datetime = Field(..., description="Client-side timestamp")

    @field_validator("farmer_id")
    def validate_national_id(cls, v):
        if not re.match(r"^NG-\d{10}$", v):
            raise ValueError("Must match format: NG-XXXXXXXXXX (e.g., NG-1234567890)")
        return v


@app.post("/api/v1/farms/register", status_code=status.HTTP_201_CREATED)
async def register_farm(payload: FarmRegistration):
    if payload.farmer_id in db_farms:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Farmer with ID {payload.farmer_id} is already registered."
        )

    farm_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    farm_record = {
        "farm_id": farm_id,
        "passport_status": "PENDING",
        "created_at": created_at,
        **payload.model_dump()
    }

    # Store in memory
    db_farms[payload.farmer_id] = farm_record

    return farm_record