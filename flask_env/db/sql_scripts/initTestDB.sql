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


INSERT INTO images (imgURL, sysLabel, verified) VALUES('1chicken.png', 'hen', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('2dino.png', 'hen', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('3dog.png', 'pufferfish', 0);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('4.jpg', 'cauliflower', 1);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('5.jpg', 'cauliflower', 1);
INSERT INTO images (imgURL, sysLabel, verified) VALUES('6.jpg', 'cauliflower', 1);



INSERT INTO models (versionNum, release) VALUES ('1.0.0', 1);

