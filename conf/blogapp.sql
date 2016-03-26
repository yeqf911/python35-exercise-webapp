-- schema.sql


DROP database if EXISTS awesome;

CREATE database awesome;

use awesome;

GRANT SELECT, UPDATE, INSERT, DELETE ON awesome.* TO root@localhost identified BY "123456";

CREATE TABLE users(
    id VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    admin VARCHAR(50) NOT NULL,
    image VARCHAR(500) NOT NULL,
    create_time REAL NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY idx_email (email),
    KEY idx_create_time (create_time)
) engine=innodb DEFAULT charset=utf8;

create table articles (
    id VARCHAR(50) not null,
    user_id VARCHAR(50) not null,
    user_name VARCHAR(50) not NULL,
    user_image VARCHAR(500) NOT NULL,
    title VARCHAR(50) NOT NULL,
    summary VARCHAR(200) NOT NULL,
    content mediumtext NOT NULL,
    create_time REAL NOT NULL,
    key idx_create_time (create_time),
    PRIMARY KEY (id)
) engine=innodb DEFAULT charset=utf8;

create table comments (
    id VARCHAR(50) not null,
    blog_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_image VARCHAR(500) NOT NULL,
    content mediumtext NOT NULL,
    create_time REAL NOT NULL,
    PRIMARY KEY (id),
    KEY idx_create_time (create_time)
) engine=innodb DEFAULT charset=utf8;

