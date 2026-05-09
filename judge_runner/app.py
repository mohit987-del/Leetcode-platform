import os

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .runner import DockerPythonRunner, LocalPythonRunner
from .schemas import SubmissionRequest, SubmissionResponse

app = FastAPI(title="CodeArena Judge Runner")


def verify_bearer_token(authorization: str = Header(default="")):
    expected = os.getenv("JUDGE_RUNNER_TOKEN", "codearena-judge-9x4k2m8p1q")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid runner token.")


def get_runner():
    mode = os.getenv("JUDGE_RUNNER_MODE", "local")
    if mode == "docker":
        return DockerPythonRunner()
    return LocalPythonRunner()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/internal/judge/submissions/", response_model=SubmissionResponse, dependencies=[Depends(verify_bearer_token)])
def judge_submission(payload: SubmissionRequest):
    return get_runner().run(payload)
