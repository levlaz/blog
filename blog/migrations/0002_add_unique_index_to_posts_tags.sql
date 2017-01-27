/**
 * Add unique index on posts_tags table
 * that ensures that combination of values
 * is unique.
 */
CREATE UNIQUE INDEX IF NOT EXISTS posts_tags_idx ON posts_tags(post_id, tag_id);
