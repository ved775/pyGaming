CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    u_name VARCHAR(10) NOT NULL,
    u_email VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(8) NOT NULL,
    role VARCHAR(10) DEFAULT 'user' NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME()
);

ALTER TABLE users ADD status VARCHAR(10) DEFAULT 'active';
ALTER TABLE users ADD profile_pic VARCHAR(255) DEFAULT 'default.png';

insert into users(u_name,u_email,password,role) values ('admin','admin@gmail.com','admin','admin')

CREATE TABLE audit (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL, 
    login_at DATETIME2 DEFAULT SYSDATETIME(),
    logout_at DATETIME2 NULL,  -- Allow NULL values
    role VARCHAR(10) DEFAULT 'user' NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)  
);

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
insert into games(id,game_name,game_type,profile_pic) values('car game','single','game5.gif')

CREATE TABLE score (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
	game_id INT NOT NULL,
    played_at DATETIME2 DEFAULT SYSDATETIME(),
	score INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

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

CREATE TABLE leaderboard (
    id INT IDENTITY(1,1) PRIMARY KEY,
	user_id INT NOT NULL,
	game_id INT NOT NULL,
	score INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

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