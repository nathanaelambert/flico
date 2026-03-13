SET password_encryption = 'scram-sha-256';

ALTER ROLE crawler PASSWORD 'mypassword';
ALTER ROLE dev PASSWORD 'mypassword';
ALTER ROLE server PASSWORD 'mypassword';