import asyncio
import logging

from .persistance import InMemoryPersistence, ExecutionStatus

# Create worker logger with simple format (no request_id needed)
logger = logging.getLogger('lg_deploy.worker')
# Prevent propagation to root logger (which has request_id format)
logger.propagate = False
# Only add handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ExecutionWorker:
    def __init__(self, queue, persistence: InMemoryPersistence):
        self.queue = queue
        self.persistence = persistence
        self._running = False
        self._task = None
    
    async def start(self):  # noqa: WPS507
        """Start the worker - async required for task creation."""
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Execution worker started")
    
    async def stop(self):  # noqa: WPS507
        """Stop the worker - async required for await task completion."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("Execution worker task cancelled")
                raise
        logger.info("Execution worker stopped")
    
    async def _run(self):
        while self._running:
            try:
                execution_id = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                self._process_execution(execution_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def _process_execution(self, execution_id: str):
        """Process a single execution - sync until real LangGraph integration."""
        logger.info(f"Processing execution: {execution_id}")
        
        # Update status to RUNNING
        self.persistence.update_status(execution_id, ExecutionStatus.RUNNING)
        
        try:
            # Simulate work (replace with actual LangGraph execution later)
            import time
            time.sleep(2)
            
            # Mark as completed
            self.persistence.update_status(execution_id, ExecutionStatus.COMPLETED)
            self.persistence.set_result(execution_id, {"output": "Execution completed successfully"})
            logger.info(f"Execution completed: {execution_id}")
            
        except Exception as e:
            self.persistence.update_status(execution_id, ExecutionStatus.FAILED)
            self.persistence.set_error(execution_id, str(e))
            logger.error(f"Execution failed: {execution_id}, error: {e}")
