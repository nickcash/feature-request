import cgi
import json

from crud_controller import crud, CRUDException

import api.clients
import api.feature_requests
import api.product_areas


def app(environ, start_response):
    """WSGI handler that delegates to our CRUD controller."""

    method = environ["REQUEST_METHOD"].upper()
    path = environ["PATH_INFO"]

    if "CONTENT-TYPE" in environ:
        content_type, options = cgi.parse_header(environ["CONTENT-TYPE"])
        content_encoding = options.get("charset", "iso-8859-1")
    else:
        content_encoding = "iso-8859-1"
    data = environ["wsgi.input"].read().decode(content_encoding)

    try:
        response = crud.handle(method, path, data)
        status = "200 OK"

    except CRUDException as err:
        # No API method matching this request was found.
        response = json.dumps({"status": "ERR",
                               "message": err.message})
        status = err.status

    except Exception as err:
        # Any unexpected error and we give a generic Internal Server Error
        response = json.dumps({"status": "ERR",
                               "message": str(err)})
        status = "500 Internal Server Error"

    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response)))
    ]

    start_response(status, headers)
    return [bytes(response, "utf-8")]
