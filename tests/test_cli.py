from typer.testing import CliRunner

from elf.cli import app


def test_cache_command_reports_missing_directory(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("ELF_CACHE_DIR", str(cache_dir))

    runner = CliRunner()
    result = runner.invoke(app, ["cache"])

    assert result.exit_code == 0
    assert "No cache directory found yet" in result.stdout
    assert str(cache_dir) in result.stdout.replace("\n", "")
