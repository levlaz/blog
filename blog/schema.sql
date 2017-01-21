/**
 * Create Posts Table
 */
CREATE TABLE posts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT NOT NULL,
	slug TEST NOT NULL,
	text_raw TEXT NOT NULL,
	text_compiled TEXT NOT NULL,
	created_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/** 
 * Create index for slug, title, and text_raw
 */
CREATE INDEX slug_idx ON posts(slug);
CREATE INDEX title_idx ON posts(title);
CREATE INDEX text_raw_idx ON posts(text_raw);

/**
 * Create Posts Triggers to handle updates
 */
CREATE TRIGGER trigger_update_post AFTER UPDATE ON posts
	BEGIN
		UPDATE posts
		SET updated_date = CURRENT_TIMESTAMP
		WHERE id = OLD.id;
	END;

/**
 * Create Tags Table
 */
CREATE TABLE tags (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	tag TEXT NOT NULL,
	created_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/**
 * Create Index on tag
 */
CREATE INDEX tag_idx ON tags(tag);

/**
 * Create Tags Triggers to handle updates
 */
CREATE TRIGGER trigger_update_tag AFTER UPDATE ON tags
	BEGIN
		UPDATE tags
		SET updated_date = CURRENT_TIMESTAMP
		WHERE id = OLD.id;
	END;

/**
 * Create Association Table 
 * between posts and tags to 
 * resolve their M:M relationship
 */
CREATE TABLE posts_tags (
	post_id INTEGER,
	tag_id INTEGER,
	FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(tag_id) REFERENCES tags(id)
);


