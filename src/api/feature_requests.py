"""CRUD API for managing feature requests."""

import uuid

from crud_controller import crud
import mock_data


@crud.create("feature_requests")
def create_feature_request(*, data):
    """Creates a new feature_request.

    Args:
        data: Must be a JSON object with the following keys:
            title: A short, descriptive name
            description: A long description
            client_id: The ID of the client
            client_priority: A numbered priority
            target_date: A string of the form "YYYY-mm-dd"
            ticket_url (optional): An arbitrary URL
            product_area_id: The ID of the product area
    """

    new_feature_request = {
        "_id": uuid.uuid1().hex,
        "title": data["title"],
        "description": data["description"],
        "client_id": data["client_id"],
        "client_priority": data["client_priority"],
        "target_date": data["target_date"],
        "ticket_url": data.get("ticket_url"),
        "product_area_id": data["product_area_id"],
    }

    mock_data.feature_requests.append(new_feature_request)


@crud.retrieve("feature_requests")
def retrieve_feature_requests():
    """Retrieves all feature requests"""

    return mock_data.get_all(mock_data.feature_requests)


@crud.retrieve("feature_requests")
def retrieve_feature_requests_for_client(client_id: int):
    """Retrieves all feature requests for a given client.

    Args:
        client_id: The ID of the client
    """

    return mock_data.get_all(mock_data.feature_requests,
                             client_id=client_id)


@crud.update("feature_requests")
def update_feature_request(_id: int, *, data):
    """Updates a single feature request.

    Args:
        _id: The ID of the feature request to update.
        data: A JSON object, the values of which will be used to update the
            feature request's values. Values that haven't changed need not be
            present.
    """

    request = mock_data.get_one(mock_data.feature_requests,
                                _id=_id)
    request.update(**data)


@crud.delete("feature_requests")
def delete_feature_request(_id: int):
    """Deletes a single feature request.

    Args:
        _id: The ID of the feature request to delete.
    """

    request = mock_data.get_one(mock_data.feature_requests,
                                _id=_id)
    mock_data.feature_requests.remove(request)
