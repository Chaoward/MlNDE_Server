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
    isoDate TEXT,
    release BIT DEFAULT 0,
    imgsTrained INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE model_label (
    modelID INTEGER NOT NULL,
    labelID INTEGER NOT NULL,
    count INT DEFAULT 1
);


ATTACH DATABASE './db/labels.db' AS 'label_db';
INSERT INTO main.labels SELECT * FROM label_db.labels;


INSERT INTO images (imgURL, sysLabel, verified) VALUES('1.jpg', 'hen', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('2.jpg', 'hen', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('3.jpg', 'pufferfish', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('4.jpg', 'cauliflower', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('5.jpg', 'cauliflower', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('6.jpg', 'cauliflower', 0);

INSERT INTO models (versionNum, isoDate, release) VALUES ('1.0.0', '2024-1-1', 1);