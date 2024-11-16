CREATE TABLE feeds (
    url TEXT PRIMARY KEY,
    title TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TRIGGER update_updated_at
AFTER UPDATE ON feeds
FOR EACH ROW
BEGIN
    UPDATE feeds
    SET updated_at = CURRENT_TIMESTAMP
    WHERE rowid = NEW.rowid;
END;
