from themis.exit_codes import compute_exit_code


def test_exit_code_success_no_findings() -> None:
    assert compute_exit_code([]) == 0


def test_exit_code_block_on_critical() -> None:
    findings = [{"severity": "critical"}]
    assert compute_exit_code(findings, block_threshold="critical") == 2


def test_exit_code_error() -> None:
    assert compute_exit_code([], error=True) == 1
