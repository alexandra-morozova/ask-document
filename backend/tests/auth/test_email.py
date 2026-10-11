from app.auth.email import is_allowed_email


def test_any_email_allowed_when_domain_unset() -> None:
    assert is_allowed_email("anyone@example.com", None) is True


def test_matching_domain_is_allowed() -> None:
    assert is_allowed_email("Analyst@Example.com", "example.com") is True


def test_other_domain_is_rejected() -> None:
    assert is_allowed_email("analyst@other.com", "example.com") is False
