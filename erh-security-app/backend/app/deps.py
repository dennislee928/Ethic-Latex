import logging
import os
from collections.abc import Generator
from typing import Optional

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from .core.db import get_db_session

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy Session for request handlers.
    """
    yield from get_db_session()


# ---------------------------------------------------------------------------
# VUL-003: Authentication stub
# ---------------------------------------------------------------------------
# Full JWT-based authentication requires additional infrastructure:
#   - A User model with password hashing (e.g., bcrypt)
#   - A token-issuing /auth/login endpoint
#   - A JWT library (python-jose or PyJWT)
#   - Ownership filters on every resource query
#
# Until that is implemented, REQUIRE_AUTH=true (env var) causes every
# protected endpoint to reject requests with 401, making the gap visible
# rather than silently allowing unauthenticated access.
# Set REQUIRE_AUTH=false only for local development / PoC demos.
# ---------------------------------------------------------------------------

_REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "false").lower() in ("1", "true", "yes")


def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> int:
    """
    Dependency that returns the authenticated user ID.

    Current state: stub — returns a hardcoded user ID of 1.
    When REQUIRE_AUTH=true, rejects requests without an Authorization header.

    TODO (VUL-003): Replace with real JWT validation:
        1. Install python-jose[cryptography]
        2. Decode the Bearer token and extract the 'sub' claim
        3. Look up the user in the database
        4. Return user.id
    """
    if _REQUIRE_AUTH:
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("Unauthenticated request blocked (REQUIRE_AUTH=true)")
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Provide a valid Bearer token.",
            )
        # TODO: validate the JWT token and extract real user_id
        logger.warning(
            "VUL-003: REQUIRE_AUTH is enabled but JWT validation is not yet implemented. "
            "Falling back to user_id=1 for all authenticated requests."
        )
    else:
        logger.debug(
            "VUL-003: Authentication is disabled (REQUIRE_AUTH=false). "
            "All requests are treated as user_id=1."
        )
    return 1


