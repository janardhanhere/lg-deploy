from fastapi import FastAPI
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ready = True
    yield
    app.state.ready = False

    

def create_app() -> FastAPI:
    app = FastAPI(
        title="LG Deploy Service",
        version="0.1.0",
        lifespan=lifespan
        )


    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
    

app = create_app()