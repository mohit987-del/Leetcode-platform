import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
from pathlib import Path

from .schemas import SubmissionRequest


EXECUTOR_SCRIPT = """
import importlib.util
import json
import pathlib
import sys

workspace = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("user_solution", workspace / "solution.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
solve = getattr(module, "solve", None)
if solve is None:
    raise AttributeError("Expected a top-level solve(raw_input: str) function.")
payload = json.loads((workspace / "payload.json").read_text())
raw_input = payload["input_data"]
result = solve(raw_input)
if result is None:
    result = ""
print(str(result).strip())
"""


class LocalPythonRunner:
    def run(self, request: SubmissionRequest) -> dict:
        case_results = []
        max_runtime_ms = 0
        for test_case in request.test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                workspace = Path(temp_dir)
                (workspace / "solution.py").write_text(request.source_code, encoding="utf-8")
                (workspace / "payload.json").write_text(
                    json.dumps({"input_data": test_case.input_data}),
                    encoding="utf-8",
                )
                (workspace / "executor.py").write_text(textwrap.dedent(EXECUTOR_SCRIPT), encoding="utf-8")

                started_at = time.perf_counter()
                try:
                    completed = subprocess.run(
                        [shutil.which("python3") or "python3", str(workspace / "executor.py"), str(workspace)],
                        capture_output=True,
                        text=True,
                        timeout=float(request.limits.get("timeout_seconds", 2)),
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    return {
                        "submission_id": request.submission_id,
                        "status": "finished",
                        "verdict": "time_limit_exceeded",
                        "runtime_ms": int(request.limits.get("timeout_seconds", 2) * 1000),
                        "memory_kb": 0,
                        "compile_output": "",
                        "case_results": [
                            {
                                "test_case_id": test_case.id,
                                "status": "time_limit_exceeded",
                                "stdout": "",
                                "stderr": "",
                                "runtime_ms": int(request.limits.get("timeout_seconds", 2) * 1000),
                                "memory_kb": 0,
                            }
                        ],
                    }
                runtime_ms = int((time.perf_counter() - started_at) * 1000)
                max_runtime_ms = max(max_runtime_ms, runtime_ms)
                stdout = completed.stdout.strip()
                stderr = completed.stderr.strip()
                if completed.returncode != 0:
                    verdict = "runtime_error"
                    case_status = "runtime_error"
                elif stdout != test_case.expected_output.strip():
                    verdict = "wrong_answer"
                    case_status = "wrong_answer"
                else:
                    verdict = "accepted"
                    case_status = "accepted"
                case_results.append(
                    {
                        "test_case_id": test_case.id,
                        "status": case_status,
                        "stdout": stdout,
                        "stderr": stderr,
                        "runtime_ms": runtime_ms,
                        "memory_kb": 0,
                    }
                )
                if verdict != "accepted":
                    return {
                        "submission_id": request.submission_id,
                        "status": "finished",
                        "verdict": verdict,
                        "runtime_ms": runtime_ms,
                        "memory_kb": 0,
                        "compile_output": "",
                        "case_results": case_results,
                    }

        return {
            "submission_id": request.submission_id,
            "status": "finished",
            "verdict": "accepted",
            "runtime_ms": max_runtime_ms,
            "memory_kb": 0,
            "compile_output": "",
            "case_results": case_results,
        }


class DockerPythonRunner:
    image = os.getenv("JUDGE_DOCKER_IMAGE", "python:3.12-slim")

    def run(self, request: SubmissionRequest) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "solution.py").write_text(request.source_code, encoding="utf-8")
            (workspace / "executor.py").write_text(textwrap.dedent(EXECUTOR_SCRIPT), encoding="utf-8")
            results = []
            max_runtime_ms = 0
            for test_case in request.test_cases:
                (workspace / "payload.json").write_text(
                    json.dumps({"input_data": test_case.input_data}),
                    encoding="utf-8",
                )
                cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--memory",
                    f"{int(request.limits.get('memory_mb', 128))}m",
                    "--cpus",
                    "1",
                    "-v",
                    f"{workspace}:/workspace",
                    "-w",
                    "/workspace",
                    self.image,
                    "python",
                    "executor.py",
                    "/workspace",
                ]
                started_at = time.perf_counter()
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=float(request.limits.get("timeout_seconds", 2)) + 1,
                    check=False,
                )
                runtime_ms = int((time.perf_counter() - started_at) * 1000)
                max_runtime_ms = max(max_runtime_ms, runtime_ms)
                stdout = completed.stdout.strip()
                stderr = completed.stderr.strip()
                if completed.returncode != 0:
                    verdict = "runtime_error"
                    status = "runtime_error"
                elif stdout != test_case.expected_output.strip():
                    verdict = "wrong_answer"
                    status = "wrong_answer"
                else:
                    verdict = "accepted"
                    status = "accepted"
                results.append(
                    {
                        "test_case_id": test_case.id,
                        "status": status,
                        "stdout": stdout,
                        "stderr": stderr,
                        "runtime_ms": runtime_ms,
                        "memory_kb": 0,
                    }
                )
                if verdict != "accepted":
                    return {
                        "submission_id": request.submission_id,
                        "status": "finished",
                        "verdict": verdict,
                        "runtime_ms": runtime_ms,
                        "memory_kb": 0,
                        "compile_output": "",
                        "case_results": results,
                    }
        return {
            "submission_id": request.submission_id,
            "status": "finished",
            "verdict": "accepted",
            "runtime_ms": max_runtime_ms,
            "memory_kb": 0,
            "compile_output": "",
            "case_results": results,
        }
