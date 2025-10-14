-- Drop and recreate exam_db (run on MySQL server as a user with privileges)
-- WARNING: This will permanently delete the current database. Run only on test/dev environments.

DROP DATABASE IF EXISTS `exam_db`;
CREATE DATABASE `exam_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `exam_db`;

-- After creating the DB, run Django migrations to create schema.
