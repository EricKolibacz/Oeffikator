CREATE EXTENSION postgis;
CREATE SCHEMA IF NOT EXISTS geo;
CREATE SCHEMA IF NOT EXISTS usage;
CREATE TABLE usage.requests(
    id SERIAL,
    date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT requests_pkey PRIMARY KEY(id)
);
CREATE TABLE geo.locations(
    id SERIAL,
    request_id INT,
    address TEXT,
    geom GEOMETRY(POINT, 4326) NOT NULL,
    CONSTRAINT requrest_id FOREIGN KEY(request_id) REFERENCES usage.requests(id),
    CONSTRAINT locations_pkey PRIMARY KEY (id)
);
CREATE TABLE geo.trips(
    id SERIAL,
    duration int NOT NULL,
    origin_id INT,
    destination_id INT,
    request_id INT,
    CONSTRAINT request_id FOREIGN KEY(request_id) REFERENCES usage.requests(id),
    CONSTRAINT origin_id FOREIGN KEY(origin_id) REFERENCES geo.locations(id),
    CONSTRAINT destination_id FOREIGN KEY(destination_id) REFERENCES geo.locations(id),
    CONSTRAINT trips_pkey PRIMARY KEY (id)
);