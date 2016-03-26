-- test.sql


DROP database if EXISTS test;

CREATE database test;

use test;

GRANT SELECT, UPDATE, INSERT, DELETE ON test.* TO root@localhost identified BY "123456";

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


CREATE TABLE blogs(
    id VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    admin VARCHAR(50) NOT NULL,
    image mediumtex NOT NULL,
    create_time REAL NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY idx_email (email),
    KEY idx_create_time (create_time)
) engine=innodb DEFAULT charset=utf8;