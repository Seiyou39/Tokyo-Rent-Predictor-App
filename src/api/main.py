from fastapi import FastAPI
from pydantic import BaseModel
from src.model.predict import predict_single

app = FastAPI()

class HouseInput(BaseModel):
    area: float
    walk: float
    age: float
    floor: float
    total_floors: float
    location: str
    layout: str


@app.post("/predict")
def predict(data: HouseInput):
    result = predict_single(data.model_dump())
    return {"predicted_rent": result}