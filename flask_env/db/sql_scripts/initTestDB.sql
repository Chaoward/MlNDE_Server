DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS models;



CREATE TABLE images (
    imgURL TEXT,
    label TEXT,
    id INTEGER PRIMARY KEY
);

CREATE TABLE labels (
    label TEXT NOT NULL PRIMARY KEY,
);

CREATE TABLE verification (
    imageID INT NOT NULL,
    verified BIT DEFAULT 0
);

CREATE TABLE models (
    versionNum TEXT,
    release BIT DEFAULT 0,
    id INTEGER PRIMARY KEY
);



INSERT INTO labels VALUES('dog');
INSERT INTO labels VALUES('bird');
INSERT INTO labels VALUES('frog');

INSERT INTO images (imgURL, label) VALUES('chicken.png', 'bird');
INSERT INTO images (imgURL, label) VALUES('dino.png', 'dog');
INSERT INTO images (imgURL, label) VALUES('dog.png', 'dog');


INSERT INTO models (versionNum) VALUES ('1.0.0'), ('1.2.9'), ('2.0.1')
INSERT INTO models (versionNum, release) VALUES('2.2.2', 1)


INSERT INTO verification (imageID)
    SELECT i.id FROM images i LEFT JOIN verification v ON i.id = v.imageID
    WHERE v.imageID IS NULL;