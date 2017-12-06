/**
 * Create Virtual Table for FTS
 */
CREATE VIRTUAL TABLE IF NOT EXISTS full_text_search USING fts4(
	title TEXT,
	text TEXT
);

/**
 * Trigger to insert post content into FTS virtual table
 * when new post is created.
 */
CREATE TRIGGER IF NOT EXISTS trigger_insert_full_text AFTER INSERT ON posts
	BEGIN
		INSERT INTO full_text_search(docid, title, text)
		VALUES (NEW.id, NEW.title, NEW.text_raw);
	END;

/**
 * Trigger to insert post content into FTS virtual table
 * when new post is updated.
 */
CREATE TRIGGER IF NOT EXISTS trigger_update_full_text AFTER UPDATE ON posts
	BEGIN
		UPDATE full_text_search
		SET title=NEW.title,text=NEW.text_raw
		WHERE docid=OLD.id;
	END;

/**
 * Trigger to delete from full text search when
 * post is deleted.
 */
CREATE TRIGGER IF NOT EXISTS trigger_delete_full_text AFTER DELETE ON posts
	BEGIN
		DELETE FROM full_text_search
		WHERE docid = OLD.id;
	END;

PRAGMA user_version=3;