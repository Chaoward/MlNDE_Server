CREATE TABLE IF NOT EXISTS images (
    imgURL TEXT,
    sysLabel TEXT,
    userLabel TEXT,
    verified INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS labels (
    classID INT,
    label TEXT
);


CREATE TABLE IF NOT EXISTS models (
    versionNum TEXT,
    isoDate TEXT,
    release BIT DEFAULT 0,
    imgsTrained INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS model_label (
    modelID INTEGER NOT NULL,
    labelID INTEGER NOT NULL,
    count INT DEFAULT 1
);

INSERT OR IGNORE INTO models (versionNum, isoDate, release, id) VALUES ('1.0.0', '2024-1-1', 1, 1);