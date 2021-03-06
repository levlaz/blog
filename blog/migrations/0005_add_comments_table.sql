/**
 * Create Comments Table
 */
CREATE TABLE IF NOT EXISTS comments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    parent_id INTEGER,
	author TEXT NOT NULL,
    email TEXT,
    website TEXT,
    comment_body TEXT NOT NULL,
    is_visible INT NOT NULL DEFAULT 0,
    is_spam INT NOT NULL DEFAULT 0,
	created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(parent_id) REFERENCES comments(id) ON DELETE CASCADE ON UPDATE CASCADE
);


PRAGMA user_version=5;