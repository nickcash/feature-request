#!/usr/bin/python3

import base64
import bcrypt
import inspect
import json
import unittest
import requests
import sys
import threading
import time
import wsgiref.simple_server

import app
import authentication
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
        @crud.retrieve("test", requires_authn=False)
        def test_api_function():
            pass

        function_spec = inspect.getfullargspec(test_api_function)

        self.assertEqual(crud._registry["GET"]["test", 0],
                         (test_api_function, function_spec, False))

    def test_crud_registry_with_args(self):
        @crud.delete("test", requires_authn=False)
        def test_api_function(a, b, c):
            pass

        function_spec = inspect.getfullargspec(test_api_function)

        self.assertEqual(crud._registry["DELETE"]["test", 3],
                         (test_api_function, function_spec, False))

    def test_crud_registry_with_requires_authn(self):
        @crud.retrieve("test", requires_authn=True)
        def test_api_function():
            pass

        function_spec = inspect.getfullargspec(test_api_function)

        self.assertEqual(crud._registry["GET"]["test", 0],
                         (test_api_function, function_spec, True))

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


class TestAuthn(unittest.TestCase):
    USERNAME = "__test"
    PASSWORD = "test"

    TOKEN_SIZE = 32

    @classmethod
    def setUpClass(cls):
        # Add a test user to the database
        with database.connection.cursor() as cursor:
            password_hash = bcrypt.hashpw(cls.PASSWORD.encode("utf8"),
                                          bcrypt.gensalt()).decode("utf8")
            cursor.execute("""INSERT INTO feature_request.users
                              (username, full_name, password_hash, administrator)
                              VALUES(%s, %s, %s, %s)
                           """,
                           (cls.USERNAME, "Test User", password_hash, False))

    @classmethod
    def tearDownClass(cls):
        # Remove that test user
        with database.connection.cursor() as cursor:
            cursor.execute("""DELETE FROM feature_request.users
                              WHERE username = %s
                           """,
                           (cls.USERNAME,))

    def test_compare_passwords(self):
        hashed_password = bcrypt.hashpw(self.PASSWORD.encode("utf8"),
                                        bcrypt.gensalt())
        self.assertTrue(authentication.compare_passwords(self.PASSWORD,
                                                         hashed_password))

    def test_generate_token(self):
        token = authentication.generate_token(self.TOKEN_SIZE)
        self.assertTrue(len(base64.b64decode(token)) == self.TOKEN_SIZE)

    def test_get_user_for_login(self):
        user = authentication.get_user_for_login(self.USERNAME, self.PASSWORD)
        self.assertTrue(user["username"] == self.USERNAME)

    def test_get_user_for_login_bad_login(self):
        with self.assertRaises(authentication.AuthenticationException):
            authentication.get_user_for_login("bad", "login")

    def test_create_session_for_user(self):
        self.assertTrue(authentication.create_session_for_user(self.USERNAME))

    def test_user_session(self):
        user = authentication.get_user_for_login(self.USERNAME, self.PASSWORD)
        token = authentication.create_session_for_user(self.USERNAME)
        self.assertTrue(authentication.get_user_for_session(token) == user)

    def test_bad_user_session(self):
        with self.assertRaises(authentication.AuthenticationException):
            authentication.get_user_for_session("bad token")


class TestServer(unittest.TestCase):
    """Spawn a WSGI server and run tests against it"""

    FOO = {"id": 1, "foo": "bar"}
    FOO2 = {"id": 1, "foo": "foobar"}

    @classmethod
    def setUpClass(cls):
        class ServerThread(threading.Thread):
            def run(self):
                foo_data = {}

                @crud.create("foo", requires_authn=False)
                def create_foo(*, data):
                    foo_data[data["id"]] = data
                    return data

                @crud.retrieve("foo", requires_authn=False)
                def retrieve_foo(id: int):
                    return foo_data.get(id, {})

                @crud.update("foo", requires_authn=False)
                def update_foo(id: int, *, data):
                    foo = foo_data[id]
                    foo.update(data)
                    return foo

                @crud.delete("foo", requires_authn=False)
                def update_foo(id: int):
                    return foo_data.pop(id)

                server = wsgiref.simple_server.make_server(
                    "", 8001, app.app)
                server.serve_forever()

        server_thread = ServerThread()
        server_thread.daemon = True
        server_thread.start()
        time.sleep(1)  # give time for server to startup

    def test_404(self):
        with self.assertRaisesRegex(requests.exceptions.HTTPError, "404 .*"):
            response = requests.get("http://localhost:8001/bork")
            response.raise_for_status()

    def test_405(self):
        with self.assertRaisesRegex(requests.exceptions.HTTPError, "405 .*"):
            response = requests.request("BORK", "http://localhost:8001/bork")
            response.raise_for_status()

    # These tests must be run in order:
    def test_1_create(self):
        created_foo = requests.post("http://localhost:8001/foo",
                                    data=json.dumps(self.FOO)).json()
        self.assertEqual(created_foo, self.FOO)

    def test_2_retrieve(self):
        retrieved_foo = requests.get("http://localhost:8001/foo/%s" % self.FOO["id"]).json()
        self.assertEqual(retrieved_foo, self.FOO)

    def test_3_update(self):
        updated_foo = requests.put("http://localhost:8001/foo/%s" % self.FOO["id"],
                                   data=json.dumps(self.FOO2)).json()
        self.assertEqual(updated_foo, self.FOO2)
        self.assertNotEqual(updated_foo, self.FOO)

    def test_4_delete(self):
        requests.delete("http://localhost:8001/foo/%s" % self.FOO["id"])
        retrieved_deleted_foo = requests.get("http://localhost:8001/foo/%s" % self.FOO["id"]).json()
        self.assertEqual(retrieved_deleted_foo, {})
        self.assertNotEqual(retrieved_deleted_foo, self.FOO)
        self.assertNotEqual(retrieved_deleted_foo, self.FOO2)


if __name__ == '__main__':
    unittest.main()
