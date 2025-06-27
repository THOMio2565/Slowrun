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

CREATE TABLE commentaires (
    id INTEGER PRIMARY KEY NOT NULL,
    commentaire TEXT NOT NULL,
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

INSERT INTO user (name, email, date, password)
VALUES
("Toinoufu", "toinoufu28@gmail.com","2023-06-10", "password"),
("THOMio", "thomio@gmail.com","2023-07-05", "password"),
("Dianakolo", "dianakolo@gmail.com","2023-12-03", "password");

INSERT INTO slowrun (time, date, user_id, game_id, category_id)
VALUES
(4600,"2024-02-02", 3, 5, 5),
(7200, "2024-03-25", 2, 1, 1),
(10800, "2024-04-29", 1, 2, 4);

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
("how did we get here", 2),
("All Authors", 3),
("Max Rank", 4),
("Tea Bag%", 5),
("any%", 6),
("0 Stars", 7),
("Great ? block ruins", 8);