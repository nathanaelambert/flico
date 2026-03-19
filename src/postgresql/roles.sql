\c "flickr_commons_metadata";

SET password_encryption = 'scram-sha-256';

CREATE ROLE crawler LOGIN PASSWORD 'xxx';
CREATE ROLE dev     LOGIN PASSWORD 'yyy';
CREATE ROLE server  LOGIN PASSWORD 'zzz';

GRANT CONNECT ON DATABASE "flickr_commons_metadata" TO crawler, server, dev;
GRANT USAGE ON SCHEMA public TO crawler, server, dev;

GRANT SELECT, INSERT, UPDATE, DELETE ON institution TO crawler;
GRANT SELECT, INSERT, UPDATE, DELETE ON photo       TO crawler;
GRANT SELECT, INSERT, UPDATE, DELETE ON license       TO crawler;

GRANT SELECT ON institution TO server;
GRANT SELECT ON photo       TO server;
GRANT SELECT ON license     TO server;
-- DEV is meant for dev to modify 
GRANT ALL PRIVILEGES ON DATABASE "flickr_commons_metadata" TO dev;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES    TO dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dev;
