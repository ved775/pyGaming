CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    u_name VARCHAR(10) NOT NULL,
    u_email VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(8) NOT NULL,
    role VARCHAR(10) DEFAULT 'user' NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
SELECT u.u_email, a.login_at, a.logout_at, a.role
         FROM audit a
         JOIN users u ON a.user_id = u.id
         WHERE u.role = 'user'
         ORDER BY a.login_at DESC
drop table users
select * from users

insert into users(u_name,u_email,password,role) values ('admin','admin@gmail.com','admin','admin')

select @@servername

ALTER TABLE users ADD status VARCHAR(10) DEFAULT 'active';

CREATE TABLE audit (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL, 
    login_at DATETIME2 DEFAULT SYSDATETIME(),
    logout_at DATETIME2 NULL,  -- Allow NULL values
    role VARCHAR(10) DEFAULT 'user' NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)  
);
SELECT user_id FROM audit WHERE logout_at IS NULL AND role = 'user'

select * from audit
SELECT * FROM audit WHERE role = 'user'

DELETE FROM users WHERE id = 6

SELECT id, user_id, login_at, logout_at, role FROM audit WHERE user_id =2

ALTER TABLE users ADD profile_pic VARCHAR(255) DEFAULT 'default.png';

SELECT u_email, role, created_at, profile_pic, u_name FROM users WHERE id =2

ALTER TABLE audit
ADD CONSTRAINT FK_audit_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;


CREATE TABLE games (
    id INT IDENTITY(1,1) PRIMARY KEY,
	game_name varchar(40) NOT NULL,
	game_type varchar(20) NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME()   
);
ALTER TABLE games ADD profile_pic VARCHAR(255) DEFAULT 'default.png';

insert into games(game_name,game_type,profile_pic) values('Enemy spawner','single','game1.gif')
insert into games(game_name,game_type,profile_pic) values('rock paper scissors','multiplayer','game2.gif')
insert into games(game_name,game_type,profile_pic) values('doom','single','game3.gif')
insert into games(game_name,game_type,profile_pic) values('flappy bird','single','game4.gif')
insert into games(id,game_name,game_type,profile_pic) values(5,'car game','single','game4.gif')

SET IDENTITY_INSERT games ON;

INSERT INTO games(id, game_name, game_type, profile_pic)
VALUES (5, 'car game', 'single', 'game4.gif');

SET IDENTITY_INSERT games OFF;


update games set profile_pic = 'game5.gif' where id=5
delete  from games where id = 1004
update games set id = 5 where id=1004

drop table games

select * from games

CREATE TABLE score (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
	game_id INT NOT NULL,
    played_at DATETIME2 DEFAULT SYSDATETIME(),
	score INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

select * from score
select * from game_session

CREATE TABLE game_session (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
	game_id INT NOT NULL,
    start_at DATETIME2 DEFAULT SYSDATETIME(),
    end_at DATETIME2 NULL,  -- Allow NULL values
    outcome VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
drop table game_session
                                                      
CREATE TABLE leaderboard (
    id INT IDENTITY(1,1) PRIMARY KEY,
	user_id INT NOT NULL,
	game_id INT NOT NULL,
	score INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

select * from leaderboard

CREATE TABLE posts (
    post_id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    date_posted DATETIME2 DEFAULT SYSDATETIME(),
    admin_id INT,
	FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE comments (
    comment_id INT IDENTITY(1,1) PRIMARY KEY,
    post_id INT,
    user_id INT,
    comment_text TEXT,
    date DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE NO ACTION
);
drop table users
select * from posts
select * from comments

CREATE TABLE feedback (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
	game_id INT NOT NULL,
	content TEXT,
    crated_at DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (game_id) REFERENCES games(id)
);
ALTER TABLE feedback ADD is_considered BIT DEFAULT 0;
update feedback set is_considered = 0 where is_considered = 'NULL'


select * from feedback

SELECT f.id, u.u_name, g.game_name, f.content, f.crated_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            JOIN games g ON f.game_id = g.id
            ORDER BY f.crated_at DESC