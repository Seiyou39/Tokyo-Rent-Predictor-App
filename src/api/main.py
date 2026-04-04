from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.model.predict import predict_single

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

class HouseInput(BaseModel):
    area: float
    walk: float
    age: float
    floor: float
    total_floors: float
    location: str
    layout: str

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/predict")
def predict(data: HouseInput):
    result = predict_single(data.model_dump())
    return {"predicted_rent": result}