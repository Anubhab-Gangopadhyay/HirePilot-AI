from __future__ import annotations

import asyncio
from collections import defaultdict

from models.workflow_models import LogLevel, WorkflowLog, WorkflowState


class WorkflowLogService:
    """In-memory log bus with polling and websocket-friendly queues."""

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[WorkflowLog]]] = defaultdict(list)

    async def emit(
        self,
        state: WorkflowState,
        agent: str,
        message: str,
        level: LogLevel = LogLevel.info,
        metadata: dict | None = None,
    ) -> WorkflowLog:
        log = WorkflowLog(
            workflow_id=state.workflow_id,
            agent=agent,
            message=message,
            level=level,
            metadata=metadata or {},
        )
        state.logs.append(log)

        stale_queues: list[asyncio.Queue[WorkflowLog]] = []
        for queue in self._queues[state.workflow_id]:
            try:
                queue.put_nowait(log)
            except asyncio.QueueFull:
                stale_queues.append(queue)

        for queue in stale_queues:
            self.unregister(state.workflow_id, queue)

        return log

    def get_logs(self, state: WorkflowState, after: int = 0) -> list[WorkflowLog]:
        return state.logs[max(after, 0):]

    def register(self, workflow_id: str) -> asyncio.Queue[WorkflowLog]:
        queue: asyncio.Queue[WorkflowLog] = asyncio.Queue(maxsize=100)
        self._queues[workflow_id].append(queue)
        return queue

    def unregister(self, workflow_id: str, queue: asyncio.Queue[WorkflowLog]) -> None:
        if workflow_id in self._queues and queue in self._queues[workflow_id]:
            self._queues[workflow_id].remove(queue)


log_service = WorkflowLogService()
