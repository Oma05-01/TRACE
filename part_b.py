from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Literal

app = FastAPI()
farmers = {}


class StatusUpdate(BaseModel):
    status: Literal["VERIFIED", "PENDING", "FLAGGED"]


# Using a standard REST path parameter for identifying the resource
@app.put("/farmers/{farmer_id}/status")
def update_status(farmer_id: str, update: StatusUpdate):
    if farmer_id not in farmers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )

    farmer = farmers[farmer_id]
    farmer["status"] = update.status
    farmers[farmer_id] = farmer

    # Return the updated resource for client-side state reconciliation
    return farmer