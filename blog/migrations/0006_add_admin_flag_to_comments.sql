/**
 * Add is_from_admin to Comments Table
 * with a default value of False
 * since SQLITE does not have a native BOOLEAN data type
 * we use 0 (true) and 1 (false)
 */
ALTER TABLE comments
    ADD COLUMN is_from_admin INTEGER NOT NULL DEFAULT 1;

PRAGMA user_version=6;