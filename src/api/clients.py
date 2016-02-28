"""CRUD API for managing clients."""

from crud_controller import crud
import mock_data


@crud.retrieve("clients")
def retrieve_clients():
    """Retrieves all clients."""

    return mock_data.get_all(mock_data.clients)


@crud.retrieve("clients")
def retrieve_client(_id: int):
    """Retrieves a single client by ID.

    Args:
        _id: The ID of the client to retrieve.
    """

    return mock_data.get_one(mock_data.clients,
                             _id=_id)
