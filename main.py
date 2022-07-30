import uvicorn
from fastapi import FastAPI
from routers.router import router
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================= Routers inclusion ===============
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app='main:app')
