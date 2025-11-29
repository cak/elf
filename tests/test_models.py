from elf.models import OutputFormat, SubmissionResult, SubmissionStatus


def test_output_format_members_cover_known_values():
    # Your existing code uses TABLE, JSON, and MODEL.
    members = {fmt for fmt in OutputFormat}
    assert OutputFormat.JSON in members
    assert OutputFormat.MODEL in members
    # TABLE may or may not be used in the CLI yet, but it exists.
    assert OutputFormat.TABLE in members


def test_submission_status_has_known_members():
    # These are the statuses already referenced by your tests.
    members = {status for status in SubmissionStatus}

    assert SubmissionStatus.CORRECT in members
    assert SubmissionStatus.INCORRECT in members
    assert SubmissionStatus.TOO_LOW in members
    # WAIT is used in the CLI exit-code logic.
    assert SubmissionStatus.WAIT in members


def test_submission_result_correct_flag_consistency():
    """
    Sanity check: a SubmissionResult constructed with CORRECT should be marked
    as correct, and anything else should not be.
    (This matches how you already construct SubmissionResult in CLI tests.)
    """
    correct = SubmissionResult(
        guess="42",
        result=SubmissionStatus.CORRECT,
        message="ok",
        is_correct=True,
        is_cached=False,
    )
    wait = SubmissionResult(
        guess="42",
        result=SubmissionStatus.WAIT,
        message="wait",
        is_correct=False,
        is_cached=False,
    )

    assert correct.result == SubmissionStatus.CORRECT
    assert correct.is_correct is True

    assert wait.result == SubmissionStatus.WAIT
    assert wait.is_correct is False
