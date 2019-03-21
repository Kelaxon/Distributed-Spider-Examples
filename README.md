# Distributed-Spider-Examples

This project implements a couple of distributed website spiders builded with **Scrapy** and **Scrapy-Redis**. All text data are stored in a **MySQL** database in the remote server, while images are uploaded to  the **QiniuCloud** object storage. The crawling target (start_urls) are loads in **Redis** remote database. The project is deployed in the server using **Docker**. 

## Getting Started 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

```bash
pip install -r requirements.txt
```

## Running the examples

```bash
cd spiders/run
python run_spider.py
```

or

```
scrapy runspider spidername
```

## Deployment

using `docker/Dockerfile` to build an docker image and run on a container.

## ORM Design

### create database 

```mysql
# create database
create database miliashop_database;
use miliashop_database;

# create debug database
create database miliashop_database_test;
GRANT ALL PRIVILEGES ON miliashop_database_test.* To 'spider'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# create user
CREATE USER 'spider'@'%' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON miliashop_database.* To 'spider'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON miliashop_database_test.* To 'spider'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;


create database itacasa_database;
use itacasa_database;

# create debug database
create database itacasa_database_test;

# create user
GRANT ALL PRIVILEGES ON itacasa_database.* To 'spider'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON itacasa_database_test.* To 'spider'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```



**Deprecated:** 

```mysql
create table product
(
    product_id					int AUTO_INCREMENT,
    product_name				varchar(100) not null,
    product_price 				varchar(50),
    product_url 				varchar(2083),
    product_short_description 	text,
    product_full_description	text,
    product_more_info			text, # python dict/json format
    primary key (product_id)
)character set = UTF8MB4;
```

```mysql
# product - product_image : 1 - n
create table product_img
(
    product_id 					int AUTO_INCREMENT,
    product_img_checksum 		char(32) not null, # md5 hash
    product_img_url 			varchar(2083),
    product_img_path 			varchar(2083),
    primary key (product_img_checksum),
    foreign key (product_id) references product (product_id)
)character set = UTF8MB4;
```

```mysql
create table attribute
(
    product_id					int default null,
    attribute_id				int AUTO_INCREMENT,
 	attribute_name				varchar(100) not null,
    primary key (attribute_id),
    foreign key (product_id) references product (product_id)
)character set = UTF8MB4;
```

```mysql
# attribute - color : n - n
create table color
(
    color_id					int AUTO_INCREMENT,
    color_name					varchar(100) not null,
    color_img_checksum			char(32) not null, # md5 hash, may miss image
    color_img_url				varchar(2083),
    color_img_path 				varchar(2083),
    primary key (color_id)
)character set = UTF8MB4;
```

```mysql
# relationship: attribute - color
create table rlts_attribute_color
(
    rlts_attribute_color_id		int AUTO_INCREMENT,
    attribute_id				int default null,
    color_id					int default null,
    primary key (rlts_attribute_color_id),
    foreign key (attribute_id) references attribute(attribute_id),
    foreign key (color_id) references color(color_id)
)character set = UTF8MB4;
```



## Authors

- **Chris Young** - *Initial work* - [Kelaxon](https://github.com/Kelaxon)

