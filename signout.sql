CREATE TABLE logins (
    id INTEGER PRIMARY KEY NOT NULL,
    login_email TEXT NOT NULL,
    login_salt TEXT NOT NULL,
    login_hash TEXT NOT NULL,
    config TEXT NOT NULL
);

CREATE TABLE signouts (
    id INTEGER PRIMARY KEY NOT NULL,
    school_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    location TEXT NOT NULL,
    time_out INTEGER NOT NULL,
    time_in INTEGER
);