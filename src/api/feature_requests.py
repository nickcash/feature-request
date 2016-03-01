"""CRUD API for managing feature requests."""

import uuid

from crud_controller import crud
import database


@crud.create("feature_requests")
def create_feature_request(*, data):
    """Creates a new feature_request.

    Args:
        data: Must be a dict with the following keys:
            title: A short, descriptive name
            description: A long description
            client_id: The ID of the client
            client_priority: A numbered priority
            target_date: A string of the form "YYYY-mm-dd"
            ticket_url (optional): An arbitrary URL
            product_area_id: The ID of the product area
    """

    data["_id"] = str(uuid.uuid1())
    with database.connection.cursor() as cursor:
        cursor.execute("""INSERT INTO feature_request.feature_requests
                              (_id, title, description, client_id,
                               client_priority, target_date,
                               ticket_url, product_area_id)

                          VALUES(%(_id)s, %(title)s, %(description)s, %(client_id)s,
                                 %(client_priority)s, %(target_date)s,
                                 %(ticket_url)s, %(product_area_id)s)
                       """,
                       data)

    return data


@crud.retrieve("feature_requests")
def retrieve_feature_requests():
    """Retrieves all feature requests"""

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT _id::text, title, description, client_id,
                              client_priority, target_date::text,
                              ticket_url, product_area_id
                          FROM feature_request.feature_requests
                          ORDER BY client_id, client_priority
                       """)

        return cursor.fetchall()


@crud.retrieve("feature_requests")
def retrieve_feature_requests_for_client(client_id: int):
    """Retrieves all feature requests for a given client.

    Args:
        client_id: The ID of the client
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT _id::text, title, description, client_id,
                              client_priority, target_date::text,
                              ticket_url, product_area_id
                          FROM feature_request.feature_requests
                          WHERE client_id = %s
                          ORDER BY client_priority
                       """,
                       (client_id,))

        return cursor.fetchall()


@crud.update("feature_requests")
def update_feature_request(_id, *, data):
    """Updates a single feature request.

    Args:
        _id: The ID of the feature request to update.
        data: A dict, the values of which will be used to update the
            feature request's values.
    """

    data["_id"] = _id
    with database.connection.cursor() as cursor:
        cursor.execute("""UPDATE feature_request.feature_requests
                          SET title = %(title)s,
                              description = %(description)s,
                              client_id = %(client_id)s,
                              client_priority = %(client_priority)s,
                              target_date = %(target_date)s,
                              ticket_url = %(ticket_url)s,
                              product_area_id = %(product_area_id)s
                          WHERE _id = %(_id)s
                       """,
                       data)

    return data


@crud.update("feature_requests_priority")
def update_feature_request_priority(_id, *, data):
    """Updates the priority of a single feature request.

    Args:
        _id: The ID of the feature request to update.
        data: A dict containing the key 'client_priority'
    """

    data["_id"] = _id
    with database.connection.cursor() as cursor:
        cursor.execute("""UPDATE feature_request.feature_requests
                          SET client_priority = %(client_priority)s
                          WHERE _id = %(_id)s
                       """,
                       data)

    return data


@crud.delete("feature_requests")
def delete_feature_request(_id):
    """Deletes a single feature request.

    Args:
        _id: The ID of the feature request to delete.
    """

    with database.connection.cursor() as cursor:
        cursor.execute("""DELETE
                          FROM feature_request.feature_requests
                          WHERE _id = %s
                       """,
                       (_id,))
