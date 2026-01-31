import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import asyncio

from .persistance import InMemoryPersistence
from .worker import ExecutionWorker


#logging configuration
logger = logging.getLogger('lg_deploy')
# Use simple format that works for all log messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize
    app.state.execution_queue = asyncio.Queue()
    app.state.persistence = InMemoryPersistence()
    app.state.worker = ExecutionWorker(
        app.state.execution_queue,
        app.state.persistence
    )

    # Start worker
    await app.state.worker.start()
    app.state.ready = True
    logger.info("Application started, worker running")

    yield

    # Cleanup
    app.state.ready = False
    await app.state.worker.stop()
    logger.info("Application shutdown, worker stopped")

    

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

    @app.post("/enqueue")
    async def enqueue(request: Request):
        execution_id = str(uuid.uuid4())

        # Create execution record in persistence
        request.app.state.persistence.create(execution_id)

        # Add to queue for processing
        await request.app.state.execution_queue.put(execution_id)

        return {"execution_id": execution_id}

    @app.get("/execute/{execution_id}")
    async def get_execution_status(execution_id: str, request: Request):
        execution = request.app.state.persistence.get(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "created_at": execution.created_at.isoformat() if execution.created_at else None,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "result": execution.result,
            "error": execution.error
        }
    
    return app
    

app = create_app()