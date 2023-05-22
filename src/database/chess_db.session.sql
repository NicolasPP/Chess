-- @Block
CREATE TABLE Users(
    u_id INT PRIMARY KEY AUTO_INCREMENT,
    elo INT DEFAULT 1200,
    u_pass VARCHAR(255) NOT NULL,
    u_name VARCHAR(255) NOT NULL UNIQUE
);


-- @Block
CREATE TABLE Games(
    g_id INT AUTO_INCREMENT,
    white_id INT NOT NULL,
    black_id INT NOT NULL,
    moves TEXT NOT NULL,
    result VARCHAR(7) NOT NULL,
    time_config VARCHAR(20) NOT NULL,
    PRIMARY KEY (g_id),
    FOREIGN KEY (white_id) REFERENCES Users(u_id),
    FOREIGN KEY (black_id) REFERENCES Users(u_id)
);


-- @Block
ALTER TABLE Users AUTO_INCREMENT=1;
-- @Block
ALTER TABLE Games AUTO_INCREMENT=1;


-- @Block
DROP TABLE Users;
-- @Block
DROP TABLE Games;



-- @Block
SELECT * FROM Users;
-- @Block
SELECT * FROM Games;