"""CRUD API for managing product areas."""

from crud_controller import crud
import mock_data


@crud.retrieve("product_areas")
def retrieve_product_areas():
    """Retrieves all product areas."""

    return mock_data.get_all(mock_data.product_areas)
