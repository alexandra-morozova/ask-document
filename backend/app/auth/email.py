def is_allowed_email(email: str, domain: str | None) -> bool:
    if domain is None:
        return True
    return email.strip().lower().endswith(f"@{domain}")
