CREATE TABLE game(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    count INTEGER,
    date DATE NOT NULL
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    date DATE NOT NULL,
    password TEXT NOT NULL
);


CREATE TABLE slowrun (
    id INTEGER PRIMARY KEY NOT NULL,
    time INTEGER NOT NULL,
    date DATE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES user (id),
    game_id INTEGER NOT NULL REFERENCES game (id),
    category_id INTEGER NOT NULL REFERENCES categories (id)
);

CREATE TABLE news (
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    game_id INTEGER NOT NULL REFERENCES game (id),
    user_id INTEGER NOT NULL REFERENCES user (id)
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    game_id INTEGER NOT NULL REFERENCES game (id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY NOT NULL,
    comment TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES user (id),
    run_id INTEGER NOT NULL REFERENCES slowrun (id)
);
-- Initiating db contents

INSERT INTO game (name, count, date)
VALUES
("NES Tetris", 4, "1989-05-06"),
("Minecraft", 3, "2011-11-18"),
("Trackmania 2020", 2, "2020-07-01"),
("Brawl Stars", 1, "2018-12-12"),
("Call Of Duty", 0, "2024-10-25"),
("Super Mario Bros", 10,"1985-06-03"),
("Super Mario 64", 7, "1996-06-23"),
("Mario Kart World", 15, "2025-06-05");


INSERT INTO categories (name, game_id)
VALUES
("Rebirth", 1),
("Maxout", 1),
("Rollover", 1),
("Any%", 2),
("All advancement", 2),
("How did we get here", 2),
("All Authors", 3),
("Max Rank", 4),
("Tea Bag%", 5),
("Any%", 6),
("0 Stars", 7),
("Great ? block ruins", 8);