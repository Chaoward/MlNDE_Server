ATTACH DATABASE './db/debug_copy.db' AS 'copy_db';

DROP TABLE IF EXISTS copy_db.images;
DROP TABLE IF EXISTS copy_db.labels;
DROP TABLE IF EXISTS copy_db.models;
DROP TABLE IF EXISTS copy_db.model_label;

CREATE TABLE  copy_db.images (
    imgURL TEXT,
    label TEXT,
    verified INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);



CREATE TABLE  copy_db.labels (
    label TEXT PRIMARY KEY
);



CREATE TABLE  copy_db.models (
    versionNum TEXT,
    release BIT DEFAULT 0,
    imgsTrained INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);



CREATE TABLE  copy_db.model_label (
    modelID INTEGER NOT NULL,
    label TEXT NOT NULL
);


INSERT INTO copy_db.images SELECT * FROM main.images;
INSERT INTO copy_db.labels SELECT * FROM main.labels;
INSERT INTO copy_db.models SELECT * FROM main.models;
INSERT INTO copy_db.model_label SELECT * FROM main.model_label;