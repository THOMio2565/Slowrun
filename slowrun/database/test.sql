CREATE TABLE game(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    count INTEGER,
    date DATE NOT NULL
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    password TEXT NOT NULL
);


CREATE TABLE slowrun (
    id INTEGER PRIMARY KEY NOT NULL,
    time INTEGER NOT NULL,
    date DATE NOT NULL,
    register_id INTEGER NOT NULL REFERENCES register (id)
);


CREATE TABLE register (
    id INTEGER PRIMARY KEY NOT NULL,
    game_id INTEGER NOT NULL REFERENCES game (id),
    user_id INTEGER NOT NULL REFERENCES user (id)
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

-- Initiating db contents

INSERT INTO game (name, count, date)
VALUES
("NES Tetris", 4, "1989-05-06"),
("Minecraft", 3, "2011-11-18"),
("Trackmania 2020", 2, "2020-07-01"),
("Brawl Stars", 1, "2018-12-12"),
("Call Of Duty: Black Ops 6", 0, "2024-10-25");

INSERT INTO user (name, date, password)
VALUES
("Toinoufu", "2023-06-10", "password"),
("THOMio", "2023-07-05", "password"),
("Dianakolo", "2023-12-03", "password");

INSERT INTO slowrun (time, date, register_id)
VALUES
(4600,"2024-02-02", 1),
(7200, "2024-03-25", 2),
(10800, "2024-04-29", 3);

INSERT INTO register (game_id, user_id)
VALUES
(5, 3),
(1, 2),
(2, 1);

INSERT INTO news (title, game_id, user_id)
VALUES
("Lag strat on level 5", 1, 2),
("Going for another category mid-run", 5, 3),
("New seed for a slowrun", 2, 1),
("Test en carton", 1, 1);

INSERT INTO categories (name, game_id)
VALUES
("Rebirth", 1),
("Maxout", 1),
("Rollover", 1),
("Any%", 2),
("All advancement", 2),
("how did we get here", 2);