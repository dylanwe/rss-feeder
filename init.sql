CREATE TABLE feeds (
    url TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_updated_at_function()
RETURNS TRIGGER AS $$
BEGIN
    -- Set the updated_at column to the current timestamp
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
