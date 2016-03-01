"""CRUD API for managing product areas."""

from crud_controller import crud
import database


@crud.retrieve("product_areas")
def retrieve_product_areas():
    """Retrieves all product areas."""

    with database.connection.cursor() as cursor:
        cursor.execute("""SELECT _id, name
                          FROM feature_request.product_areas
                          ORDER BY _id
                       """)
        return cursor.fetchall()
