"""FastAPI application factory and PR-1 routes."""

from fastapi import FastAPI

from elite_team import __version__
from elite_team.contracts.task import HealthResponse, TaskRequest, TaskResponse
from elite_team.orchestration.state import create_task_foundation


def create_app() -> FastAPI:
    """Create an isolated FastAPI application instance."""

    application = FastAPI(
        title="Elite AI Agent Team",
        version=__version__,
        description="PR-1 deterministic task intake and mode-routing foundation.",
    )

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="elite-ai-agent-team",
            version=__version__,
        )

    @application.post("/tasks", response_model=TaskResponse, tags=["tasks"])
    def create_task(request: TaskRequest) -> TaskResponse:
        return create_task_foundation(request)

    return application


app = create_app()

__all__ = ["app", "create_app"]
