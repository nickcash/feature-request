CREATE SCHEMA feature_request
  AUTHORIZATION feature_request;


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
   FOREIGN KEY (client_id) REFERENCES feature_request.clients (_id) ON UPDATE NO ACTION ON DELETE NO ACTION,
   FOREIGN KEY (product_area_id) REFERENCES feature_request.product_areas (_id) ON UPDATE NO ACTION ON DELETE NO ACTION
);
