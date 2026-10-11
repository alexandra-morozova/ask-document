from app.config import Settings


def test_split_origins_from_csv() -> None:
    assert Settings.split_origins("http://localhost:5173, https://app.example") == [
        "http://localhost:5173",
        "https://app.example",
    ]


def test_split_origins_leaves_lists_unchanged() -> None:
    origins = ["http://localhost:5173"]
    assert Settings.split_origins(origins) is origins


def test_normalize_email_domain_strips_and_lowercases() -> None:
    assert Settings.normalize_email_domain(" @Driftwood.com ") == "driftwood.com"


def test_normalize_email_domain_treats_blank_as_unset() -> None:
    assert Settings.normalize_email_domain("") is None
    assert Settings.normalize_email_domain("   ") is None
