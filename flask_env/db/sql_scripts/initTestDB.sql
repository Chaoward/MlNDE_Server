DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS model_label;



CREATE TABLE images (
    imgURL TEXT,
    label TEXT,
    verified INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE labels (
    label TEXT PRIMARY KEY
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



INSERT INTO labels VALUES('dog');
INSERT INTO labels VALUES('bird');
INSERT INTO labels VALUES('frog');
INSERT INTO labels VALUES('popcorn');
INSERT INTO labels VALUES('burger');
INSERT INTO labels VALUES('cat');
INSERT INTO labels VALUES('chair');


INSERT INTO images (imgURL, label) VALUES('chicken.png', 'bird');
INSERT INTO images (imgURL, label) VALUES('dino.png', 'dog');
INSERT INTO images (imgURL, label) VALUES('dog.png', 'dog');


INSERT INTO models (versionNum) VALUES ('1.0.0'), ('1.2.9'), ('2.0.1');
INSERT INTO models (versionNum) VALUES ('2.2.2');

INSERT INTO model_label (modelID, label) VALUES (2, 'popcorn'), (2, 'burger'), (2, 'cat');
INSERT INTO model_label (modelID, label) VALUES (3, 'chair');
