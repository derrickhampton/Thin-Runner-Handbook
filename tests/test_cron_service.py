from pathlib import Path

import pytest

from api.services.cron_service import CronService


def test_validate_cron_expression_rejects_invalid_field_count() -> None:
    service = CronService()
    with pytest.raises(ValueError, match="exactly 5 fields"):
        service.validate_cron_expression("0 7 * *")


def test_validate_command_rejects_unsafe_shell_chars() -> None:
    service = CronService()
    with pytest.raises(ValueError, match="disallowed shell characters"):
        service.validate_command("thin-runner run-skill hello_world --json '{}' && rm -rf /")


def test_replace_managed_block_preserves_unrelated_entries() -> None:
    service = CronService()
    existing = "0 5 * * * /usr/bin/backup\n"

    updated = service.replace_managed_block(
        existing=existing,
        schedule="0 7 * * *",
        command="thin-runner run-pipeline pipelines/hello_pipeline.yaml",
        enabled=True,
    )

    assert "0 5 * * * /usr/bin/backup" in updated
    assert "# >>> THIN RUNNER MANAGED BLOCK >>>" in updated
    assert "0 7 * * * thin-runner run-pipeline pipelines/hello_pipeline.yaml" in updated


def test_backup_crontab_creates_file(tmp_path: Path) -> None:
    service = CronService(backup_dir=str(tmp_path))
    backup = service.backup_crontab("0 5 * * * /usr/bin/backup\n")

    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "0 5 * * * /usr/bin/backup\n"
