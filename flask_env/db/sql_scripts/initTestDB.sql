DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS model_label;



CREATE TABLE images (
    imgURL TEXT,
    sysLabel TEXT,
    userLabel TEXT,
    verified INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE labels (
    classID INT,
    label TEXT
);


CREATE TABLE models (
    versionNum TEXT,
    release BIT DEFAULT 0,
    imgsTrained INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE model_label (
    modelID INTEGER NOT NULL,
    label TEXT NOT NULL
);


ATTACH DATABASE './db/labels.db' AS 'label_db';
INSERT INTO main.labels SELECT * FROM label_db.labels;


INSERT INTO images (imgURL, userLabel) VALUES('chicken.png', 'bird');
INSERT INTO images (imgURL, userLabel) VALUES('dino.png', 'jeep');
INSERT INTO images (imgURL, userLabel) VALUES('dog.png', 'pufferfish');


INSERT INTO models (versionNum) VALUES ('1.0.0'), ('1.2.9'), ('2.0.1');
INSERT INTO models (versionNum, release) VALUES ('2.2.2', 1);

