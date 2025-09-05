# main.py
from fastapi import FastAPI
from DataTide_back.routers import ground_weather, items, sample
from DataTide_back.back.routers import location, sea_weather, item_retail # Added

app = FastAPI()

app.include_router(ground_weather.router)
app.include_router(items.router)
app.include_router(sample.router, prefix="/sample")
app.include_router(location.router) # Added
app.include_router(sea_weather.router) # Added
app.include_router(item_retail.router) # Added

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "DataTide Backend API에 오신걸 환영합니다!"}
