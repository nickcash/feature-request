"""API for logging in."""

import authentication
from crud_controller import crud


@crud.create("login", requires_authn=False)
def login(*, data):
    """Creates a user session for user with supplied username and password."""

    user = authentication.get_user_for_login(data["username"],
                                             data["password"])
    user["token"] = authentication.create_session_for_user(user["username"])

    return user


@crud.create("logout")
def logout(*, user):
    """Removes user's session."""

    authentication.destroy_session_for_user(user["username"])
