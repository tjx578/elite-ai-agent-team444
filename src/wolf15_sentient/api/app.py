"""FastAPI application factory for the deterministic PR-2 kernel."""

from fastapi import FastAPI

from wolf15_sentient import __version__
from wolf15_sentient.contracts import HealthResponse, TaskRequest, WorkflowResult
from wolf15_sentient.orchestration.workflow import run_workflow


def create_app() -> FastAPI:
    """Create an isolated FastAPI application instance."""

    application = FastAPI(
        title="WOLF15 Sentient",
        version=__version__,
        description="PR-2 deterministic, typed, bounded orchestration kernel.",
    )

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="wolf15-sentient",
            version=__version__,
        )

    @application.post("/tasks", response_model=WorkflowResult, tags=["tasks"])
    def create_task(request: TaskRequest) -> WorkflowResult:
        return run_workflow(request)

    return application


app = create_app()

__all__ = ["app", "create_app"]
