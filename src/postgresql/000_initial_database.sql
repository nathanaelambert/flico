CREATE DATABASE "Flickr commons metadata";

\c "Flickr commons metadata";

CREATE ROLE crawler LOGIN PASSWORD 'crawler123';
CREATE ROLE server  LOGIN PASSWORD 'server123';
CREATE ROLE dev     LOGIN PASSWORD 'dev123';

GRANT CONNECT ON DATABASE "Flickr commons metadata" TO crawler, server, dev;
GRANT USAGE ON SCHEMA public TO crawler, server, dev;
GRANT SELECT, INSERT, UPDATE, DELETE ON institutions TO crawler;
GRANT SELECT, INSERT, UPDATE, DELETE ON photos       TO crawler;
GRANT SELECT ON institutions TO server;
GRANT SELECT ON photos       TO server;
GRANT ALL PRIVILEGES ON DATABASE "Flickr commons metadata" TO dev;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES    TO dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dev;

CREATE TABLE institutions (
    nsid TEXT PRIMARY KEY,
    name TEXT,
    date_launch BIGINT,
    website TEXT,
    license TEXT,
    flickr_page TEXT
);

CREATE TABLE photos (
    owner_nsid TEXT,
    id INT,
    secret TEXT,
    server INT,
    title TEXT,
    ispublic BOOLEAN,
    isfriend BOOLEAN,
    isfamily BOOLEAN,
    PRIMARY KEY (owner_nsid, id)
);
