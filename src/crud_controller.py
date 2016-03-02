"""Controller for dispatching HTTP requests to CRUD actions.

Attributes:
    crud: A singleton CRUD controller with which all other modules will
        register their API methods.
    CRUDException: An exception class for errors occurred during dispatching
        a request to an API method.
"""

import inspect
import json

import authentication


class _CRUDController():
    """Dispatches HTTP requests to defined CRUD actions.

    Usage:
        create, retrieve, update, and delete methods are used to register
        a function to an API endpoint.
        Each can take any number of positional arguments corresponding to
        the number of path segments in the URL it expects. Args may be
        annotated with a type they'll automatically be coerced to.

        Functions may also have certain keyword-only arguments:
            data: the decoded JSON document it'll use to create or replace
                a reasource.
            user: the currently authenticated user (or None)

    Examples:
        @crud.create("foo")
        def make_foo(*, data):
            # create a foo with given data

        @crud.retrieve("foo")
        def get_foo(id: int):
            # retrieve a foo with corresponding id

        crud.handle("POST", "/foo", '{"id": 1}')
        # creates a foo with id=1

        crud.handle("GET", "/foo/1")
        # returns JSON document corresponding to foo with id=1
    """

    def __init__(self):
        """Initializes controller's method registry"""

        self._registry = {
            "PUT": {},
            "GET": {},
            "POST": {},
            "DELETE": {}
        }

    def _register(self, method, endpoint, requires_authn):
        """Registers a CRUD function.

        Creates a decorator to register a function with a given
        HTTP method, URL endpoint, and required parameters.

        Args:
            method: An HTTP method: POST, GET, PUT, or DELETE.
            endpoint: The base of the URL to register.
            requires_authn: If True (default), requires a valid session cookie
                when calling the API.

        Returns:
            A decorator function that will register a function it is
            applied to.
        """

        def decorator(function):
            spec = inspect.getfullargspec(function)
            self._registry[method][endpoint, len(spec.args)] = (function,
                                                                spec,
                                                                requires_authn)
            return function
        return decorator

    def create(self, endpoint, requires_authn=True):
        """Registers a create endpoint."""
        return self._register("POST", endpoint,
                              requires_authn=requires_authn)

    def retrieve(self, endpoint, requires_authn=True):
        """Registers a retrieve endoint."""
        return self._register("GET", endpoint,
                              requires_authn=requires_authn)

    def update(self, endpoint, requires_authn=True):
        """Registers an update endpoint."""
        return self._register("PUT", endpoint,
                              requires_authn=requires_authn)

    def delete(self, endpoint, requires_authn=True):
        """Registers a delete endpoint."""
        return self._register("DELETE", endpoint,
                              requires_authn=requires_authn)

    def handle(self, method, path, data=None, cookie=None):
        """Handle an HTTP request using the registers handler for that URL endpoint
            and parameters.

        Args:
            method: An HTTP method: POST, GET, etc.
            path: The URL path segment
            data: For POST and PUT (create/update) endpoints, the JSON document
                with which to create or replace the resource.
            cookie: An http.cookies Cookie, if the user sent one.

        Returns:
            A str or bytes content for the response.

        Raises:
            CRUDException: An error occurred accessing that resource.
            AuthenticationException: A request was made for a secure resource
                without a valid session token.
        """

        _, endpoint, *args = path.split("/")

        # Lookup corresponding API method or bailout
        if method not in self._registry:
            raise CRUDException("405 Method Not Allowed",
                                "Unknown method '{}'".format(method))
        elif (endpoint, len(args)) not in self._registry[method]:
            raise CRUDException("404 Not Found",
                                "Unknown path '{}'".format(path))

        function, spec, requires_authn = self._registry[method][endpoint, len(args)]

        if cookie and "session" in cookie:
            user = authentication.get_user_for_session(cookie["session"].value)
        else:
            user = None

        if requires_authn and not user:
            raise authentication.AuthenticationException("Authentication required.")

        # Coerce all args to the required type, if the API method function
        # has corresponding annotations.
        args = [spec.annotations.get(name, str)(arg)
                for (arg, name) in zip(args, spec.args)]

        # Pass data arg, if function wants it
        kwargs = {}
        if "data" in spec.kwonlyargs:
            kwargs["data"] = json.loads(data)
        if "user" in spec.kwonlyargs:
            kwargs["user"] = user

        response = function(*args, **kwargs)

        return json.dumps(response if response is not None else {"status": "OK"})


class CRUDException(Exception):
    """Exception raised during CRUD controller handling a request.

    Attributes:
        status: A full HTTP status code response as a string
            (ex. "404 Not Found" or "418 I'm a teapot")
        message: A str or bytes content for the response.
    """

    def __init__(self, status, message):
        """Initializes CRUDException with status and message."""

        self.status = status
        self.message = message

    def __str__(self):
        return self.status


# Singleton _CRUDController
crud = _CRUDController()
