# sqlite3 에서 routine_db 생성하는 .sql 파일

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS routines (
    id INTEGER PRIMARY KEY,
    completed INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    duration_hours INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    icon TEXT,
    routine_name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    group_routine_name TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS timers (
    id INTEGER PRIMARY KEY,
    completed INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    duration_hours INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    icon TEXT,
    timer_name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
