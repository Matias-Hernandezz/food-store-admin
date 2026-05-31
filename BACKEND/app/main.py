from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# CORREGIDO: Importamos la función real de tu archivo app/core/db.py
from app.core.db import create_all_tables 
from fastapi.middleware.cors import CORSMiddleware
import os
from app.modules.dominio_1.Usuarios.routers import router as router_auth
from app.modules.dominio_2.Categoria.routers import router as router_categoria
from app.modules.dominio_2.Producto.routers import router as router_producto
from app.modules.dominio_2.Ingrediente.routers import router as router_ingrediente
from app.modules.dominio_3.Pedidos.routers import router as router_pedidos
from fastapi.responses import JSONResponse
import traceback
from fastapi import Request
import logging

app = FastAPI(title="Food Store")

@app.on_event("startup")
def on_startup():
    create_all_tables()

if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()  # imprime en la consola del uvicorn
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.include_router(router_auth)
app.include_router(router_categoria)
app.include_router(router_producto)
app.include_router(router_ingrediente)
app.include_router(router_pedidos)

origins = [
    "http://localhost:5173",  
    "http://localhost:5174",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174","http://localhost:5173", "http://[IP_ADDRESS]"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.DEBUG)
@app.get("/")
def home():
    return {"status": "ok"}