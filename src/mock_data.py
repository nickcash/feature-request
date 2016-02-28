"""Mock data to be replaced by a true database."""
# TODO: that

def get_all(data, **kargs):
    for key, value in kargs.items():
        data = [entry for entry in data
                if entry[key] == value]
    return data


def get_one(data, **kargs):
    return get_all(data, **kargs)[0]


feature_requests = [
    {
        "_id": 1,
        "title": "Request A.1",
        "description": "A request",
        "client_id": 1,
        "client_priority": 1,
        "target_date": "2016-02-27",
        "ticket_url": "http://bad.horse/",
        "product_area_id": 1,
    },
    {
        "_id": 2,
        "title": "Request A.2",
        "description": "Another request",
        "client_id": 1,
        "client_priority": 2,
        "target_date": "2016-03-01",
        "ticket_url": "http://bad.horse/",
        "product_area_id": 2,
    },
    {
        "_id": 3,
        "title": "Request B.1",
        "description": "A request from another client",
        "client_id": 2,
        "client_priority": 1,
        "target_date": "2017-01-01",
        "ticket_url": "http://www.google.com/",
        "product_area_id": 3
    },
]

clients = [
    {
        "_id": 1,
        "name": "Client A",
    },
    {
        "_id": 2,
        "name": "Client B",
    },
    {
        "_id": 3,
        "name": "Client C",
    }
]

product_areas = [
    {
        "_id": 1,
        "name": "Policies",
    },
    {
        "_id": 2,
        "name": "Billing",
    },
    {
        "_id": 3,
        "name": "Claims",
    },
    {
        "_id": 4,
        "name": "Reports",
    },
]
