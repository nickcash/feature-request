INSERT INTO feature_request.clients
    (_id, name)
    VALUES (1, 'Client A'),
           (2, 'Client B'),
           (3, 'Client C');

INSERT INTO feature_request.product_areas
    (_id, name)
    VALUES (1, 'Policies'),
           (2, 'Billing'),
           (3, 'Claims'),
           (4, 'Reports');

INSERT INTO feature_request.users
    (username, full_name, password_hash, administrator)
    VALUES ('admin', 'Administrator User',
            --hash of "admin_pass"
            '$2b$12$AWkDb2vMQz1v0OdUsKKF1eyjHsuAxnvVLdGgLrOF13XBroDF58G6q',
            true),

           ('user', 'Regular User',
            --hash of "user_pass"
            '$2b$12$Bs3dlx9m9HuHhXt8wxe/l.HCliO/5T2Pe3Fd3dOTWswBuZMLCgHKu',
            false);
