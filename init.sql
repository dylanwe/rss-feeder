CREATE TABLE users (
    pocket_access_token TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE feeds (
    url TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    user_token TEXT,
    FOREIGN KEY (user_token) REFERENCES users(pocket_access_token)
);

