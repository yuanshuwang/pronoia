-- Reset database for simplified World Observation OS (v1).
-- Run against `world_observation` when migrating from an older schema.
-- Then: python main.py init-db

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS experiment_events;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS founder_kpi_monthly;
DROP TABLE IF EXISTS opportunity_events;
DROP TABLE IF EXISTS contradictory_signals;
DROP TABLE IF EXISTS pattern_snapshots;
DROP TABLE IF EXISTS extracted_signals;
DROP TABLE IF EXISTS raw_comments;
DROP TABLE IF EXISTS raw_posts;
DROP TABLE IF EXISTS opportunity_patterns;
DROP TABLE IF EXISTS interviews;

DROP TABLE IF EXISTS product_inspirations;
DROP TABLE IF EXISTS pain_patterns;
DROP TABLE IF EXISTS founder_notes;
DROP TABLE IF EXISTS raw_signals;

SET FOREIGN_KEY_CHECKS = 1;
