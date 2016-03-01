"""CRUD API for managing clients."""

from crud_controller import crud
import database


@crud.retrieve("clients")
def retrieve_clients():
    """Retrieves all clients."""

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT _id, name
                          FROM feature_request.clients
                          ORDER BY _id
                       """)
        return cursor.fetchall()


@crud.retrieve("clients")
def retrieve_client(_id: int):
    """Retrieves a single client by ID.

    Args:
        _id: The ID of the client to retrieve.
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT _id, name
                          FROM feature_request.clients
                          WHERE _id = %s
                       """,
                       (id,))
        return cursor.fetchone()
