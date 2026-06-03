from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


THIN_RUNNER_START = "# >>> THIN RUNNER MANAGED BLOCK >>>"
THIN_RUNNER_END = "# <<< THIN RUNNER MANAGED BLOCK <<<"
DISALLOWED_COMMAND_CHARS = [";", "&&", "||", "|", "`", "$(", ">", "<"]


class CronService:
    def __init__(self, backup_dir: str = "runs/cron_backups") -> None:
        self.backup_dir = backup_dir

    def validate_cron_expression(self, schedule: str) -> None:
        parts = schedule.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron schedule must contain exactly 5 fields.")

        allowed = re.compile(r"^[\d\*/,\-]+$")
        for part in parts:
            if not allowed.match(part):
                raise ValueError(f"Invalid cron field: {part}")

    def validate_command(self, command: str) -> None:
        if not (
            command.startswith("thin-runner run-skill")
            or command.startswith("thin-runner run-pipeline")
        ):
            raise ValueError(
                "Command must start with thin-runner run-skill or thin-runner run-pipeline."
            )

        if any(token in command for token in DISALLOWED_COMMAND_CHARS):
            raise ValueError("Command contains disallowed shell characters.")

    def read_crontab(self) -> str:
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("crontab command not found on this system") from exc

        if result.returncode != 0:
            return ""
        return result.stdout

    def write_crontab(self, content: str) -> None:
        try:
            subprocess.run(["crontab", "-"], input=content, text=True, check=True)
        except FileNotFoundError as exc:
            raise RuntimeError("crontab command not found on this system") from exc

    def backup_crontab(self, content: str) -> Path:
        path = Path(self.backup_dir)
        path.mkdir(parents=True, exist_ok=True)
        backup = path / f"crontab-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.txt"
        backup.write_text(content, encoding="utf-8")
        return backup

    def replace_managed_block(
        self,
        existing: str,
        schedule: str,
        command: str,
        enabled: bool = True,
    ) -> str:
        self.validate_cron_expression(schedule)
        self.validate_command(command)

        line = f"{schedule} {command}" if enabled else f"# disabled: {schedule} {command}"
        block = f"{THIN_RUNNER_START}\n{line}\n{THIN_RUNNER_END}"

        pattern = re.compile(
            rf"{re.escape(THIN_RUNNER_START)}.*?{re.escape(THIN_RUNNER_END)}",
            re.DOTALL,
        )

        if pattern.search(existing):
            return pattern.sub(block, existing).strip() + "\n"

        if not existing.strip():
            return block + "\n"

        return existing.strip() + "\n\n" + block + "\n"

    def get_managed_schedule(self) -> dict[str, Any]:
        existing = self.read_crontab()
        pattern = re.compile(
            rf"{re.escape(THIN_RUNNER_START)}\n(.*?)\n{re.escape(THIN_RUNNER_END)}",
            re.DOTALL,
        )
        match = pattern.search(existing)

        if not match:
            return {
                "managed": False,
                "enabled": False,
                "schedule": "",
                "command": "",
                "raw": "",
            }

        line = match.group(1).strip()
        enabled = not line.startswith("# disabled:")
        if not enabled:
            line = line.replace("# disabled:", "", 1).strip()

        parts = line.split(maxsplit=5)
        schedule = ""
        command = ""
        if len(parts) >= 6:
            schedule = " ".join(parts[:5])
            command = parts[5]

        return {
            "managed": True,
            "enabled": enabled,
            "schedule": schedule,
            "command": command,
            "raw": match.group(0),
        }

    def update_schedule(self, enabled: bool, schedule: str, command: str) -> dict[str, Any]:
        existing = self.read_crontab()
        backup_path = self.backup_crontab(existing)
        updated = self.replace_managed_block(
            existing=existing,
            schedule=schedule,
            command=command,
            enabled=enabled,
        )
        self.write_crontab(updated)

        return {
            "status": "updated",
            "backup_path": str(backup_path),
            "enabled": enabled,
            "schedule": schedule,
            "command": command,
        }
