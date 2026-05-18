from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import perf_counter

from app import models


@dataclass
class ExecutionOutput:
    status: str
    command: str | None
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int
    output_json: dict


async def execute_task(task: models.TaskNode) -> ExecutionOutput:
    if task.executor_type == "command":
        return await _execute_command(task)
    return await _execute_mock(task)


async def _execute_mock(task: models.TaskNode) -> ExecutionOutput:
    await asyncio.sleep(float(task.executor_config_json.get("delay_seconds", 0.25)))
    should_fail = bool(task.executor_config_json.get("should_fail", False))
    exit_code = 1 if should_fail else 0
    return ExecutionOutput(
        status="FAILED" if should_fail else "SUCCEEDED",
        command=None,
        stdout=f"Mock executor completed task: {task.title}\n",
        stderr="Configured mock failure.\n" if should_fail else "",
        exit_code=exit_code,
        duration_ms=int(float(task.executor_config_json.get("delay_seconds", 0.25)) * 1000),
        output_json={"expected_outputs": task.expected_outputs, "mock": True},
    )


async def _execute_command(task: models.TaskNode) -> ExecutionOutput:
    command = task.executor_config_json.get("command")
    if not command:
        return ExecutionOutput(
            status="FAILED",
            command=None,
            stdout="",
            stderr="CommandExecutor requires executor_config_json.command.",
            exit_code=2,
            duration_ms=0,
            output_json={},
        )
    started = perf_counter()
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=task.executor_config_json.get("cwd") or None,
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    duration_ms = int((perf_counter() - started) * 1000)
    return ExecutionOutput(
        status="SUCCEEDED" if process.returncode == 0 else "FAILED",
        command=command,
        stdout=stdout_bytes.decode(errors="replace"),
        stderr=stderr_bytes.decode(errors="replace"),
        exit_code=process.returncode,
        duration_ms=duration_ms,
        output_json={"command": command},
    )

