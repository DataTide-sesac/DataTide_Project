CREATE DATABASE data_tide_db;
USE data_tide_db;

-- 품목 테이블 생성
CREATE TABLE item (
    item_pk   INT PRIMARY KEY,
    item_name VARCHAR(20)
);

-- 품목별 생산/수입/판매 테이블 생성
CREATE TABLE item_retail (
    retail_pk   BIGINT PRIMARY KEY,
    item_pk     INT,
    production  INT,
    inbound     INT,
    sales       INT,
    month_date  DATE,
    FOREIGN KEY (item_pk) REFERENCES item(item_pk) -- 외래 키 설정
);

-- 해양 날씨 테이블 생성
CREATE TABLE sea_weather (
    sea_pk        BIGINT PRIMARY KEY,
    month_date    DATE,
    local         VARCHAR(10),
    temperature   FLOAT,
    wind          FLOAT,
    rain          FLOAT,
    snow          FLOAT
);

-- 지상 날씨 테이블 생성
CREATE TABLE ground_weather (
    ground_pk     BIGINT PRIMARY KEY,
    month_date    DATE,
    temperature   FLOAT,
    rain          FLOAT,
    snow          FLOAT
);