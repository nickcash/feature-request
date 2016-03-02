"""API for logging in."""

import authentication
from crud_controller import crud


@crud.create("login", requires_authn=False)
def login(*, data):
    """Creates a user session for user with supplied username and password."""

    if not data.get("username") or not data.get("password"):
        raise authentication.AuthenticationException(
                  "Username and password are required!")

    user = authentication.get_user_for_login(data["username"],
                                             data["password"])
    user["token"] = authentication.create_session_for_user(user["username"])

    return user


@crud.create("logout")
def logout(*, user):
    """Removes user's session."""

    authentication.destroy_session_for_user(user["username"])
