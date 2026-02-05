import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
import json

from .persistance import InMemoryPersistence
from .worker import ExecutionWorker
from .graph_runner import GraphRunner


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
    app.state.runner = GraphRunner()
    app.state.worker = ExecutionWorker(
        app.state.execution_queue,
        app.state.persistence
    )

    # Start worker
    app.state.worker.start()
    app.state.ready = True
    logger.info("Application started, worker running")

    yield

    # Cleanup
    app.state.ready = False
    try:
        await app.state.worker.stop()
        app.state.runner.close()
    except asyncio.CancelledError:
        # Swallow CancelledError in lifespan - it's expected during shutdown
        logger.info("Worker task cancelled during shutdown")
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
    async def enqueue(request: Request, body: dict | None = None):
        execution_id = str(uuid.uuid4())
        input_data = body.get("input") if body else None

        # Create execution record in persistence
        request.app.state.persistence.create(execution_id, input_data)

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
    
    @app.get("/execute/{execution_id}/stream")
    async def stream_execution(execution_id: str, request: Request):
        """
        Stream graph execution using Server-Sent Events.
        
        This endpoint streams the execution results as they are generated,
        allowing real-time updates to the client.
        """
        # Verify execution exists
        execution = request.app.state.persistence.get(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Get input state
        input_state = request.app.state.persistence.get_input(execution_id)
        if input_state is None:
            raise HTTPException(status_code=400, detail="No input found for execution")
        
        async def generate():
            try:
                async for chunk in request.app.state.runner.astream(input_state):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.exception("Error during streamed execution for execution_id %s", execution_id)
                yield f"data: {json.dumps({'error': 'An internal error has occurred.'})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    return app
    

app = create_app()