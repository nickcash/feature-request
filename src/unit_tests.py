#!/usr/bin/python3

import inspect
import json
import unittest
import requests
import sys
import threading
import time
import wsgiref.simple_server

import app
from crud_controller import crud, CRUDException
import database


class TestCRUDController(unittest.TestCase):
    TEST_JSON = '{"foo": "bar"}'

    def test_crud_registry_methods(self):
        self.assertTrue("PUT" in crud._registry)
        self.assertTrue("GET" in crud._registry)
        self.assertTrue("POST" in crud._registry)
        self.assertTrue("DELETE" in crud._registry)

    def test_crud_registry_no_args(self):
        @crud.retrieve("test")
        def test_api_function():
            pass

        function_spec = inspect.getfullargspec(test_api_function)

        self.assertEqual(crud._registry["GET"]["test", 0],
                         (test_api_function, function_spec))

    def test_crud_registry_with_args(self):
        @crud.delete("test")
        def test_api_function(a, b, c):
            pass

        function_spec = inspect.getfullargspec(test_api_function)

        self.assertEqual(crud._registry["DELETE"]["test", 3],
                         (test_api_function, function_spec))

    def test_crud_handle_json(self):
        @crud.retrieve("test")
        def test_api_function(a):
            return {"foo": a}

        self.assertEqual(crud.handle("GET", "/test/bar"),
                         self.TEST_JSON)

    def test_crud_handle_data(self):
        @crud.create("test")
        def test_api_function(*, data):
            return data

        self.assertEqual(crud.handle("POST", "/test", self.TEST_JSON),
                         self.TEST_JSON)

    def test_crud_handle_unknown_method(self):
        with self.assertRaisesRegex(CRUDException, "405 .*"):
            crud.handle("BORK", "/test")

    def test_crud_handle_unknown_path(self):
        with self.assertRaisesRegex(CRUDException, "404 .*"):
            crud.handle("GET", "/bork/bork/bork")


class TestDatabase(unittest.TestCase):
    def test_database_connection(self):
        self.assertTrue(database.connection)

    def test_database_cursor(self):
        self.assertTrue(database.connection.cursor())

    def test_database_autocommit(self):
        self.assertTrue(database.connection.autocommit)

    def test_database_fetchone(self):
        with database.connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS result")
            self.assertEqual(cursor.fetchone(),
                             {"result": 1})

    def test_database_fetchall(self):
        with database.connection.cursor() as cursor:
            cursor.execute("SELECT UNNEST(ARRAY[1, 2, 3]) AS result")
            self.assertEqual(cursor.fetchall(),
                             [{"result": 1}, {"result": 2}, {"result": 3}])


class TestServer(unittest.TestCase):
    """Spawn a WSGI server and run tests against it"""

    FOO = {"id": 1, "foo": "bar"}
    FOO2 = {"id": 1, "foo": "foobar"}

    @classmethod
    def setUpClass(cls):
        class ServerThread(threading.Thread):
            def run(self):
                foo_data = {}

                @crud.create("foo")
                def create_foo(*, data):
                    foo_data[data["id"]] = data
                    return data

                @crud.retrieve("foo")
                def retrieve_foo(id: int):
                    return foo_data.get(id, {})

                @crud.update("foo")
                def update_foo(id: int, *, data):
                    foo = foo_data[id]
                    foo.update(data)
                    return foo

                @crud.delete("foo")
                def update_foo(id: int):
                    return foo_data.pop(id)

                server = wsgiref.simple_server.make_server(
                    "", 8000, app.app)
                server.serve_forever()

        server_thread = ServerThread()
        server_thread.daemon = True
        server_thread.start()
        time.sleep(1)  # give time for server to startup

    def test_404(self):
        with self.assertRaisesRegex(requests.exceptions.HTTPError, "404 .*"):
            response = requests.get("http://localhost:8000/bork")
            response.raise_for_status()

    def test_405(self):
        with self.assertRaisesRegex(requests.exceptions.HTTPError, "405 .*"):
            response = requests.request("BORK", "http://localhost:8000/bork")
            response.raise_for_status()

    # These tests must be run in order:
    def test_1_create(self):
        created_foo = requests.post("http://localhost:8000/foo",
                                    data=json.dumps(self.FOO)).json()
        self.assertEqual(created_foo, self.FOO)

    def test_2_retrieve(self):
        retrieved_foo = requests.get("http://localhost:8000/foo/%s" % self.FOO["id"]).json()
        self.assertEqual(retrieved_foo, self.FOO)

    def test_3_update(self):
        updated_foo = requests.put("http://localhost:8000/foo/%s" % self.FOO["id"],
                                   data=json.dumps(self.FOO2)).json()
        self.assertEqual(updated_foo, self.FOO2)
        self.assertNotEqual(updated_foo, self.FOO)

    def test_4_delete(self):
        requests.delete("http://localhost:8000/foo/%s" % self.FOO["id"])
        retrieved_deleted_foo = requests.get("http://localhost:8000/foo/%s" % self.FOO["id"]).json()
        self.assertEqual(retrieved_deleted_foo, {})
        self.assertNotEqual(retrieved_deleted_foo, self.FOO)
        self.assertNotEqual(retrieved_deleted_foo, self.FOO2)


if __name__ == '__main__':
    unittest.main()
