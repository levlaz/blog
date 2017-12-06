/**
 * Add isStaticPage to Posts Table
 * with a default value of False
 * since SQLITE does not have a native BOOLEAN data type
 * we use 0 (true) and 1 (false)
 */
ALTER TABLE posts
    ADD COLUMN is_static_page INTEGER DEFAULT 1;

PRAGMA user_version=4;