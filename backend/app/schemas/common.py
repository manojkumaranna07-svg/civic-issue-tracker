"""Email validation that also accepts documentation/demo domains (example.com).

DNS deliverability checks are disabled because demo accounts deliberately use
the reserved example.com domain, and real deployments validate syntax here too.
"""
from typing import Annotated

from email_validator import validate_email, EmailNotValidError
from pydantic import AfterValidator


def _check_email(v: str) -> str:
    try:
        validate_email(v.strip(), check_deliverability=False, globally_deliverable=False)
    except EmailNotValidError as e:
        raise ValueError(str(e))
    return v.strip().lower()


Email = Annotated[str, AfterValidator(_check_email)]
