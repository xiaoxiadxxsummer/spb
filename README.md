## Web application structure

In practical applications, the frontend's requests are sent to the backend in the form of API calls. The backend first checks if the route path of the request exists. If it does, the corresponding business function for that path is invoked to execute the relevant business logic and return the results to the frontend. The core interfaces in the system are shown in the following table.

~~这里贴一个表格的截图~~



## Design decisions

Before designing this system, I studied the design ideas of many similar projects. After thorough research, I developed my own design decisions. My system design not only meets the basic requirement of treating technical staff and administrators separately but also satisfactorily supports a series of functions in the administrator interface.

**Routing:** The system creates different route paths for users of different roles (technical staff and administrators) and maps different functions and pages to different route paths, facilitating troubleshooting and future maintenance.

**Templates:** The system uses HTML templates to create a sufficient number of non-redundant template files, such as customer_test.html, parts_management.html, services_management.html, unpaid_bill_management.html, etc., to display different pages according to different route paths and data. Regarding the use of POST and GET methods, different functions in this system use different methods, and some functions can use either method. For example, searchCustomer is designated to use GET, while scheduleJob uses POST. GET requests are more suitable for query operations, and since the data in POST requests is not directly exposed in the URL, they are relatively more secure and thus suitable for data submission operations.

**Data:** The system has a well-planned database architecture to accommodate the data entities and relationships needed for the website, such as customers, jobs, services, parts, and bills, using MySQL for data storage and management. To ensure data consistency and integrity, the system employs mechanisms for data input validation, transaction management to ensure the atomicity of related operations, and validation and constraints.

**Overall Layout:** The system features a sidebar navigation, enabling users to easily navigate between different pages; it uses responsive design to ensure the website displays well on various devices.

## Database questions
### 1.  What SQL statement creates the job table and defines its fields/columns?  
spb_pa.sql文件creates了6个表，他们分别为customer、job、part、job_part、job_service。创建table和其fields/columns的语句如下：

```
CREATE TABLE IF NOT EXISTS customer
(
customer_id INT auto_increment PRIMARY KEY NOT NULL,
first_name varchar(25),
family_name varchar(25) not null,
email varchar(320) not null,
phone varchar(11) not null
);
  
CREATE TABLE IF NOT EXISTS job
(
job_id INT auto_increment PRIMARY KEY NOT NULL,
job_date date NOT NULL,
customer int NOT NULL,
total_cost decimal(6,2) default null,
completed tinyint default 0,
paid tinyint default 0,

FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS part
(
part_id INT auto_increment PRIMARY KEY NOT NULL,
part_name varchar(25) not null ,
cost decimal(5,2) not null
);

CREATE TABLE IF NOT EXISTS service
(
service_id INT auto_increment PRIMARY KEY NOT NULL,
service_name varchar(25) not null ,
cost decimal(5,2) not null
);

CREATE TABLE IF NOT EXISTS job_part
(
job_id INT NOT NULL,
part_id INT not null ,
qty INT not null DEFAULT 1,

FOREIGN KEY (job_id) REFERENCES job(job_id)
ON UPDATE CASCADE,

FOREIGN KEY (part_id) REFERENCES part(part_id)
ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS job_service
(
job_id INT NOT NULL,
service_id INT not null ,
qty INT not null DEFAULT 1,

FOREIGN KEY (job_id) REFERENCES job(job_id)
ON UPDATE CASCADE,

FOREIGN KEY (service_id) REFERENCES service(service_id)
ON UPDATE CASCADE
);
```
现我来分析最后一个表job_service，这个表包含了job_id, service_id, qty三个列(columns)，它们都是整型(INT)，他们三个都不能为空，qty默认值为1。表job_service有外键job_id，它是job表的主键；有service_id，是service表的主键。service表的service_id更新时，job表中的service_id也更新。
```
CREATE TABLE IF NOT EXISTS job_service
(
job_id INT NOT NULL,
service_id INT not null ,
qty INT not null DEFAULT 1,

FOREIGN KEY (job_id) REFERENCES job(job_id)
ON UPDATE CASCADE,

FOREIGN KEY (service_id) REFERENCES service(service_id)
ON UPDATE CASCADE
);
```
其余表中具体包含的列名的分析方法同上，在此不再赘述。
### 2. Which line of SQL code sets up the relationship between the customer and job tables?
```
FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON  UPDATE CASCADE
```
job表中的customer键是外键，它是customer表的主键customer_id，当customer表中customer_id的值改变时，job表中的customer同时改变。这就sets up the relationship between the customer and job tables。

### 3. Which lines of SQL code insert details into the parts table?
```
INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Wiper blade', '12.43');
INSERT INTO part (`part_name`, `cost`) VALUES ('Left fender', '260.76');
INSERT INTO part (`part_name`, `cost`) VALUES ('Right fender', '260.76');
INSERT INTO part (`part_name`, `cost`) VALUES ('Tail light', '120.54');
INSERT INTO part (`part_name`, `cost`) VALUES ('Hub Cap', '22.89');
```
### 4. Suppose that as part of an audit trail, the time and date a service or part was added to a job needed to be recorded, what fields/columns would you need to add to which tables? Provide the table name, new column name and the data type. 
`job_service`表： 
 列名：`added_date`
 数据类型：`DATETIME`  或  `TIMESTAMP`
    
 `job_part`表：   
 列名：`added_date`
数据类型：`DATETIME`  或  `TIMESTAMP`

### 5. Suppose logins were implemented. Why is it important for technicians and the office administrator to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
The tasks of technicians are is updating customer jobs with parts and services. But The tasks of admin staff are updating, editing and adding data. Due to different tasks, it is important for technicians and the office administrator to access different routes. 
数据泄露，如果谁都能访问数据库，那可能造成用户个人信息泄露、重要信息被篡改、。。。
功能滥用。除了数据的保密性会收到威胁，如果不进行接口的区分，每个员工都会面对着繁杂的系统，他们不得不从一堆功能中选出自己用得上的功能，并且可能会误触一些本不是他职责内的功能。这使得每个员工需要面对许多冗余的功能，降低工作效率。

