CREATE TABLE IF NOT EXISTS configurations (
    id SERIAL PRIMARY KEY,
    service TEXT NOT NULL,
    version INTEGER NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (service, version)
);
