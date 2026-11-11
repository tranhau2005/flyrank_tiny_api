CREATE TABLE tasks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO tasks (title, done) VALUES
    ('Learn SQLite', FALSE), ('Build CRUD API', FALSE), ('Test persistence', FALSE);
