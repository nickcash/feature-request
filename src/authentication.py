"""Authentication """

import base64
import bcrypt
import datetime
from hmac import compare_digest
import os

import database


DEFAULT_TOKEN_SIZE = 32  # bytes
SESSION_TIMEOUT = datetime.timedelta(hours=1)


def compare_passwords(entered_password, password_hash):
    """Compares a user-entered password with a hash of the actual password.

    Hashed passwords must be hashed using bcrypt. Passwords are compared
    using a method designed to prevent timing attacks.

    Args:
        entered_password: The password the user entered as a string.
        password_hash: The hashed, correct password, as either string or bytes.

    Returns:
        A boolean indicating whether it matched or not.
    """

    if isinstance(password_hash, str):
        password_hash = password_hash.encode("utf8")

    return compare_digest(bcrypt.hashpw(entered_password.encode("utf8"),
                                        password_hash),
                          password_hash)


def generate_token(size=DEFAULT_TOKEN_SIZE):
    """Generates a secure session token.

    Tokens are generated using the OS's high-quality,
    crytpographically-suitable randomness source.

    Args:
        size (optional): Number of bytes of randomness to use.

    Returns:
        The token, as a base64-encoded string.
    """

    return base64.b64encode(os.urandom(size)).decode("ascii")


def get_user_for_login(username, password):
    """Authenticates a user with a given username, password combination.

    Args:
        username: The user's username.
        password: The user's password, unhashed.

    Returns:
        The user, as a dict.

    Raises:
        AuthenticationException: The username, password combination
            is invalid.
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT username, full_name, password_hash, administrator
                          FROM feature_request.users
                          WHERE username = %s
                       """,
                       (username,))

        user = cursor.fetchone()

    if not user or not compare_passwords(password, user["password_hash"]):
        raise AuthenticationException("Incorrect username or password.")

    user.pop("password_hash")  # don't leak secure data

    return user


def create_session_for_user(username):
    """Creates a session for a user in the database.

    Args:
        username: The username for which to create session.

    Returns:
        The session token.
    """

    token = generate_token()

    destroy_session_for_user(username)  # remove any previous sessions

    with database.connection.cursor() as cursor:
        session = cursor.execute("""INSERT INTO feature_request.sessions
                                    (username, token)
                                    VALUES(%s, %s);
                                 """,
                                 (username, token))

    return token


def destroy_session_for_user(username):
    """Destroys a session for a user in the database.

    Args:
        username: The username who's session is to be removed.
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""DELETE FROM feature_request.sessions
                          WHERE username = %s
                       """,
                       (username,))


def get_user_for_session(token):
    """Authenticates user associated with a given session token.

    Args:
        token: A login token

    Returns:
        The user, as a dict.

    Raises:
        AuthenticationException: The session token is invalid.
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT users.username, full_name, administrator
                          FROM feature_request.sessions
                          JOIN feature_request.users
                              ON users.username = sessions.username
                          WHERE token = %s
                              AND now() - sessions.created < %s
                       """,
                       (token, SESSION_TIMEOUT))
        user = cursor.fetchone()

    if not user:
        raise AuthenticationException("Invalid session token.",
                                      token=token)

    return user


class AuthenticationException(Exception):
    """Exception raised during user authentication.

    Attributes:
        message: A string indicating what went wrong.
        username: If authenticating by username, the username that failed.
        token: If authenticating by session token, the token that failed.
    """

    def __init__(self, message, username=None, token=None):
        """Initializes AuthenticationException."""

        self.message = message
        self.username = username
        self.token = token

    def __str__(self):
        return self.status
