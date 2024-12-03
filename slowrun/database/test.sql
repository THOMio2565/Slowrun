INSERT INTO game (name, count, date, categories)
VALUES
("NES Tetris", 4, "1989-05-06", "Rebirth"),
("Minecraft", 3, "2011-11-18", "Any%"),
("Trackmania 2020", 2, "2020-07-01", "Summer 2024 All Authors"),
("Brawl Stars", 1, "2018-12-12", "MAX Tier"),
("Call Of Duty: Black Ops 6", 0, "2024-10-25", "Tutorial%");

INSERT INTO user (name, date)
VALUES
("Toinoufu", "2023-06-10"),
("THOMio", "2023-07-05"),
("Dianakolo", "2023-12-03");

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
("Test-icule", 1, 1);