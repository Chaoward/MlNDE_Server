
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
    release BIT DEFAULT 0,
    imgsTrained INT DEFAULT 0,
    id INTEGER PRIMARY KEY
);



CREATE TABLE IF NOT EXISTS model_label (
    modelID INTEGER NOT NULL,
    label TEXT NOT NULL
);