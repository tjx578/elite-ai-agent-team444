"""FastAPI application factory for the deterministic PR-2 kernel."""

from fastapi import FastAPI

from elite_team import __version__
from elite_team.contracts import HealthResponse, TaskRequest, WorkflowResult
from elite_team.orchestration.workflow import run_workflow


def create_app() -> FastAPI:
    """Create an isolated FastAPI application instance."""

    application = FastAPI(
        title="Elite AI Agent Team",
        version=__version__,
        description="PR-2 deterministic, typed, bounded orchestration kernel.",
    )

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="elite-ai-agent-team",
            version=__version__,
        )

    @application.post("/tasks", response_model=WorkflowResult, tags=["tasks"])
    def create_task(request: TaskRequest) -> WorkflowResult:
        return run_workflow(request)

    return application


app = create_app()

__all__ = ["app", "create_app"]
