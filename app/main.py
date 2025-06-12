from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="MacMenuScraper API",
    description="API to retrieve nutritional info of McDonald's products",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the MacMenuScraper API"}
