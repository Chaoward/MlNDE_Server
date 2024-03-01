DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS labels;


CREATE TABLE images (
    imgURL TEXT,
    labelID INT,
    id INTEGER PRIMARY KEY
);

CREATE TABLE labels (
    label TEXT,
    id INTEGER PRIMARY KEY
);

CREATE TABLE verification (
    imageID INT NOT NULL,
    verified INT DEFAULT 0
);



INSERT INTO labels (label) VALUES('dog');
INSERT INTO labels (label) VALUES('bird');
INSERT INTO labels (label) VALUES('frog');

INSERT INTO images (imgURL, labelID) VALUES('chicken.png', 2);
INSERT INTO images (imgURL, labelID) VALUES('dino.png', 0);
INSERT INTO images (imgURL, labelID) VALUES('dog.png', 0);



INSERT INTO verification (imageID)
    SELECT i.id FROM images i LEFT JOIN verification v ON i.id = v.imageID
    WHERE v.imageID IS NULL;