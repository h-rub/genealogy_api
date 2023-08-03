from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router as routes_router


app = FastAPI()

app.include_router(routes_router)

# Configurar los orígenes permitidos (en este caso, permitimos todo)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)