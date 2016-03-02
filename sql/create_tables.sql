CREATE SCHEMA feature_request;


CREATE TABLE feature_request.clients
(
   _id integer NOT NULL,
   name text NOT NULL,
   PRIMARY KEY (_id)
);


CREATE TABLE feature_request.product_areas
(
  _id integer NOT NULL,
  name text NOT NULL,
  CONSTRAINT product_areas_pkey PRIMARY KEY (_id)
);


CREATE TABLE feature_request.feature_requests
(
   _id uuid NOT NULL,
   title text NOT NULL,
   description text NOT NULL,
   client_id integer NOT NULL,
   client_priority integer NOT NULL DEFAULT 1,
   target_date date NOT NULL,
   ticket_url text,
   product_area_id integer NOT NULL,
   PRIMARY KEY (_id),
   FOREIGN KEY (client_id)
       REFERENCES feature_request.clients (_id)
       ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (product_area_id)
       REFERENCES feature_request.product_areas (_id)
       ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE feature_request.users
(
   username text NOT NULL,
   full_name text,
   password_hash text NOT NULL,
   administrator boolean NOT NULL DEFAULT false,
   PRIMARY KEY (username)
);


CREATE TABLE feature_request.sessions
(
   username text NOT NULL,
   token bytea NOT NULL,
   created timestamp without time zone NOT NULL DEFAULT now(),
   PRIMARY KEY (username),
   FOREIGN KEY (username)
       REFERENCES feature_request.users (username)
       ON UPDATE CASCADE ON DELETE CASCADE
);
