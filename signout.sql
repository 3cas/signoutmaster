CREATE TABLE users (
    id INTEGER PRIMARY KEY NOT NULL,
    email TEXT NOT NULL UNIQUE,
    schoolname TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    config TEXT NOT NULL DEFAULT "{}"
);

CREATE TABLE signouts (
    id INTEGER PRIMARY KEY NOT NULL,
    school_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    location TEXT NOT NULL,
    time_out INTEGER NOT NULL,
    time_in INTEGER
);