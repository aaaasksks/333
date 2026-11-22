-- Выполните этот файл от пользователя MySQL с правом создавать базы и пользователей.
-- Пароль study_pass подходит только для учебной базы на своем компьютере.

CREATE DATABASE IF NOT EXISTS study_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'student'@'localhost'
    IDENTIFIED BY 'study_pass';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
    ON study_db.* TO 'student'@'localhost';

USE study_db;

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
