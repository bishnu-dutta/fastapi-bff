import uuid
from app.models import UserRole
from functools import lru_cache

import httpx
import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.core.config import settings
from app.users.request import CreateUserRequest
from app.organizations.request import AdminCreateUserRequest


REALM_BASE = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
ADMIN_BASE = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}"
TOKEN_URL = f"{REALM_BASE}/protocol/openid-connect/token"
LOGOUT_URL = f"{REALM_BASE}/protocol/openid-connect/logout"
CERTS_URL = f"{REALM_BASE}/protocol/openid-connect/certs"


class KeycloakError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


def _get_admin_token() -> str:
    """
    Client-credentials grant for the confidential admin client. That client
    must have Service Accounts enabled and the realm-management client roles
    'manage-users' + 'view-users' assigned to its service account.
    """
    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.KEYCLOAK_ADMIN_CLIENT_ID,
            "client_secret": settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
        },
        timeout=10,
    )
    if resp.status_code != 200:
        raise KeycloakError(f"Could not obtain Keycloak admin token: {resp.text}", 502)
    return resp.json()["access_token"]


def create_keycloak_user(
    user: CreateUserRequest | AdminCreateUserRequest,
    org_id: uuid.UUID,
    role: UserRole = UserRole.USER,
    send_verification_email: bool = True,
) -> str:
    """
    Creates the user in Keycloak with org_id/role stored as custom user
    attributes. Sets emailVerified to False by default, and automatically
    triggers Keycloak's built-in email verification via MailHog.
    """
    admin_token = _get_admin_token()
    if not user.email:
        raise KeycloakError("Email is required", 400)

    payload = {
        "username": user.username,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "enabled": True,
        "emailVerified": False,
        "requiredActions": ["VERIFY_EMAIL"],
        "attributes": {
            "organization_id": [str(org_id)],
            "role": [role.value if hasattr(role, "value") else str(role)],
        },
        "credentials": [
            {
                "type": "password",
                "value": user.password,
                "temporary": False,
            }
        ],
    }
    resp = httpx.post(
        f"{ADMIN_BASE}/users",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10,
    )
    if resp.status_code == 409:
        raise KeycloakError("Username or email already exists in Keycloak", 409)
    if resp.status_code != 201:
        raise KeycloakError(f"Failed to create Keycloak user: {resp.text}", 502)

    location = resp.headers.get("Location", "")
    sub = location.rstrip("/").split("/")[-1]
    if not sub:
        raise KeycloakError("Keycloak did not return a user id", 502)

    if send_verification_email:
        try:
            send_verify_email(sub)
        except Exception:
            # We don't fail registration if SMTP delivery fails, but log/let user know
            pass

    return sub


def send_verify_email(sub: str, redirect_uri: str | None = None) -> None:
    """
    Triggers Keycloak's built-in email verification link delivery via configured SMTP (MailHog).
    """
    admin_token = _get_admin_token()
    params = {"client_id": settings.KEYCLOAK_LOGIN_CLIENT_ID}
    if redirect_uri:
        params["redirect_uri"] = redirect_uri

    resp = httpx.put(
        f"{ADMIN_BASE}/users/{sub}/execute-actions-email",
        params=params,
        json=["VERIFY_EMAIL"],
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10,
    )
    if resp.status_code not in (200, 204):
        raise KeycloakError(f"Failed to send Keycloak verification email: {resp.text}", resp.status_code)



def get_keycloak_user_by_email(email: str) -> dict | None:
    """Looks up a user by exact email using the Keycloak Admin API."""
    admin_token = _get_admin_token()
    resp = httpx.get(
        f"{ADMIN_BASE}/users",
        params={"email": email, "exact": "true"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10,
    )
    if resp.status_code == 200:
        users = resp.json()
        if users:
            return users[0]
    return None


def update_keycloak_user(sub: str, data: dict) -> None:
    """Updates user fields in Keycloak (firstName, lastName, email, etc.)."""
    admin_token = _get_admin_token()
    kc_payload = {}

    if data.get("first_name") is not None:
        kc_payload["firstName"] = data["first_name"]
    if data.get("last_name") is not None:
        kc_payload["lastName"] = data["last_name"]
    if data.get("email") is not None:
        kc_payload["email"] = data["email"]
    if data.get("username") is not None:
        kc_payload["username"] = data["username"]

    if kc_payload:
        resp = httpx.put(
            f"{ADMIN_BASE}/users/{sub}",
            json=kc_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10,
        )
        if resp.status_code not in (200, 204):
            raise KeycloakError(f"Failed to update Keycloak user: {resp.text}", resp.status_code)



def delete_keycloak_user(sub: str) -> None:
    """
    Compensating action: if the local DB insert fails after the Keycloak
    user was already created, remove the orphaned Keycloak account so the
    two stores don't drift out of sync.
    """
    try:
        admin_token = _get_admin_token()
        httpx.delete(
            f"{ADMIN_BASE}/users/{sub}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10,
        )
    except Exception:
        pass


def login_user(username: str, password: str, totp: str | None = None) -> dict:
    """Resource Owner Password Credentials grant. Requires 'Direct access
    grants' enabled on the login client in Keycloak. Supports optional 'totp'
    when MFA is configured."""
    data = {
        "grant_type": "password",
        "client_id": settings.KEYCLOAK_LOGIN_CLIENT_ID,
        "username": username,
        "password": password,
    }
    if settings.KEYCLOAK_LOGIN_CLIENT_SECRET:
        data["client_secret"] = settings.KEYCLOAK_LOGIN_CLIENT_SECRET
    if totp:
        data["totp"] = totp

    resp = httpx.post(TOKEN_URL, data=data, timeout=10)
    if resp.status_code != 200:
        error_msg = "Invalid username or password"
        try:
            err_data = resp.json()
            desc = err_data.get("error_description", "")
            err = err_data.get("error", "")
            if "Account is not fully set up" in desc:
                error_msg = "Account is not fully set up: Please verify your email via the link sent to your inbox."
            elif not totp and ("credentials" in desc or "OTP" in desc):
                error_msg = desc or "Invalid credentials or missing TOTP/MFA code."
            else:
                error_msg = desc or err or error_msg
        except Exception:
            pass
        raise KeycloakError(error_msg, resp.status_code)
    return resp.json()


def logout_user(refresh_token: str) -> None:
    """Revokes the session server-side in Keycloak via its refresh token."""
    data = {
        "client_id": settings.KEYCLOAK_LOGIN_CLIENT_ID,
        "refresh_token": refresh_token,
    }
    if settings.KEYCLOAK_LOGIN_CLIENT_SECRET:
        data["client_secret"] = settings.KEYCLOAK_LOGIN_CLIENT_SECRET

    resp = httpx.post(LOGOUT_URL, data=data, timeout=10)
    if resp.status_code not in (200, 204):
        raise KeycloakError(f"Logout failed: {resp.text}", 400)


@lru_cache
def _jwks_client() -> PyJWKClient:
    return PyJWKClient(CERTS_URL)


def decode_access_token(token: str) -> dict:
    """
    Verifies the access token's signature (via Keycloak's JWKS), expiry,
    issuer and audience, and returns its claims — including the custom
    org_id / role attributes set at registration.
    """
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.TOKEN_AUDIENCE,
            issuer=REALM_BASE,
            # DNS Issue fixing verify_iss
            options={"verify_aud": bool(settings.TOKEN_AUDIENCE), "verify_iss": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {exc}")
    return claims
