import logging
import uuid
from fastapi import FastAPI , Request
from contextlib import asynccontextmanager


#logging configuration
logger = logging.getLogger('lg_deploy')
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s %(request_id)s %(method)s %(path)s"
)



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

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = request.headers.get('X-Request-ID',str(uuid.uuid4()))
        request.state.request_id = request_id 

        logger.info(
            "request_started",
            extra={
                'request_id': request_id,
                "method": request.method,
                'path': request.url.path,
            }
        )
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        
        logger.info(
            'request_completed',
            extra={
                'request_id': request_id,
                'method' : request.method,
                'path': request.url.path,
                'status_code' : response.status_code,
            }
        )

        return response


    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
    

app = create_app()