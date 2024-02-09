## Web application structure

在实际应用中，前端的请求将以调用接口的形式发送给后端，而后端将首先检查该请求的路由路径是否存在，若存在则调用的该路径所对应的业务函数，执行对应的业务逻辑处理并将结果返回到前端。系统中核心的接口如下表所示。


~~这里贴一个表格的截图~~



## Design decisions

在设计这个系统之前，我学习了许多类似项目的设计思路。经过充分的调研，我拥有了自己的设计决定。我的系统设计不仅能够满足技术人员与管理员分别对待这一基本要求，并且可以很好的满足管理员界面的一系列功能。
在 **路由** 方面，本系统不仅并为不同角色的用户（技术人员和管理员）创建不同的路由路径，并且将不同的功能和页面映射到不同的路由路径上，便于问题排查和后期维护。
在 **模版** 方面，本系统使用HTML模版，创建了足够多且不冗余的模板文件，如customer_test.html, parts_management.html, services_management.html, unpaid_bill_management.html等，以便根据不同的路由路径和数据呈现不同的页面。至于post和get方式的使用，在本系统中，不同的function使用不同的方式，甚至有些函数可以使用其中任意一种方式。例如searchCustomer指定使用get，scheduleJob使用post方式。GET请求更适用于查询操作，而由于POST请求的数据不会直接暴露在URL中，相对更安全，因此POST请求适用于发送数据操作。
在 **数据** 方面，本系统合理规划了数据库架构，以适应网站所需的数据实体和关系，例如客户、工作、服务、零件和账单等，并使用MySQL来存储和管理数据。同时，为保障数据的一致性和完整性，本系统具有数据输入验证、使用事务管理保障相关操作的原子性、验证和约束等机制。
在 **整体布局** 方面，本系统设计了侧方导航栏，使用户能够在不同的页面之间轻松导航；使用响应式设计，以确保网站在不同设备上的显示效果良好。

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

