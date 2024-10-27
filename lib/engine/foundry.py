from utils.paths import run_cli_can_failed, run_cli_must_succeed


def format_code(_path: str) -> str:
    diff = run_cli_can_failed(f"forge fmt {_path} --check")[0]
    if diff:
        run_cli_must_succeed(f"forge fmt {_path}")
    return diff
