from pydantic import BaseModel, Field


class TestCasePayload(BaseModel):
    id: int
    input_data: str
    expected_output: str
    is_public: bool = False
    weight: int = 1


class SubmissionRequest(BaseModel):
    submission_id: int
    language: str = Field(pattern="^python$")
    source_code: str
    test_cases: list[TestCasePayload]
    limits: dict[str, int | float]


class CaseResult(BaseModel):
    test_case_id: int
    status: str
    stdout: str = ""
    stderr: str = ""
    runtime_ms: int | None = None
    memory_kb: int | None = None


class SubmissionResponse(BaseModel):
    submission_id: int
    status: str
    verdict: str
    runtime_ms: int | None = None
    memory_kb: int | None = None
    compile_output: str = ""
    case_results: list[CaseResult]
