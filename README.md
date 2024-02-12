 ## Web application structure

In practical applications, the frontend's requests are sent to the backend in the form of API calls. The backend first checks if the route path of the request exists. If it does, the corresponding business function for that path is invoked to execute the relevant business logic and return the results to the frontend. The core interfaces in the system are shown in the following table.

![Weixin Screenshot_20240210183516](https://github.com/xiaoxiadxxsummer/spb/assets/109004935/e054df78-c8a2-4996-83f0-743a27146570)




## Design decisions

Before designing this system, I studied the design ideas of many similar projects. After thorough research, I developed my own design decisions. My system design not only meets the basic requirement of treating technical staff and administrators separately but also satisfactorily supports a series of functions in the administrator interface.

**Routing:** The system creates different route paths for users of different roles (technical staff and administrators) and maps different functions and pages to different route paths, facilitating troubleshooting and future maintenance. I primarily differentiate routes based on user roles and entity objects. For instance, interfaces for technicians start with the /technician path, while those for administrators start with /manager. Differentiating routes in this way aids in future role-based permission management, allowing us to intercept different roles directly through their routes. Dividing routes based on entities helps avoid conflicts with route names or paths.

**Templates:**  It was my first encounter with server-rendering methods like {% extends %}{% block content %}{% endblock %}. Using this rendering approach, I can uniformly manage JavaScript and CSS code, significantly boosting my development efficiency. Templates are named based on the content they display, making it easier for users to understand the content within based on semantics. The system uses HTML templates to create a sufficient number of non-redundant template files, such as customer_test.html, parts_management.html, services_management.html, unpaid_bill_management.html, etc., to display different pages according to different route paths and data. Regarding the use of POST and GET methods, different functions in this system use different methods, and some functions can use either method. For example, searchCustomer is designated to use GET, while scheduleJob uses POST. GET requests are more suitable for query operations, and since the data in POST requests is not directly exposed in the URL, they are relatively more secure and thus suitable for data submission operations.

**In navigation and overall page layout design**, the primary principle is to "provide a better user experience." Navigation strives for clarity and ease of use. Page layout considers how to better interact with users, offering immediate feedback after user actions (e.g., indicating success or directly displaying data post-action). For instance, in our project, the "add user" feature can utilize modals or page redirects for input to maintain user focus and workflow continuity while reducing server load.

**Functionality design** must closely integrate with real-world usage. For example, while technicians view current jobs and can edit job information, there might be a need to review completed jobs. Thus, I added a feature to display completed job information. When editing job details, such as adding parts to a job, it's common for a job to require multiple parts or services. Therefore, our application should offer a single page where technicians can add multiple part or service details, making the application more aligned with reality and user-friendly.

Regarding **data requests**, some data is relatively private to users. When receiving user input, it's important to consider privacy protection. For such data, I use POST requests to the server, which helps secure data transmission and protect user privacy.

In **data handling**, the database may contain null values (e.g., None), and stores first names and family names separately. Considering user habits, I display this information in a user-friendly manner on the webpage. To avoid inconsistencies due to potential database update failures, I use try-except blocks for exception handling in database operations, rolling back data in case of errors.

## Database questions
### 1.  What SQL statement creates the job table and defines its fields/columns?  
The spb_pa.sql file creates 6 tables, which are customer, job, part, job_part, and job_service. The statements for creating tables and their fields/columns are as follows:

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
Now, let's analyze the last table, job_service. This table contains three columns: job_id, service_id, and qty, all of which are integers (INT). All three columns cannot be null, with qty having a default value of 1. The job_service table has a foreign key, job_id, which is the primary key of the job table; and service_id, which is the primary key of the service table. When the service_id in the service table is updated, the service_id in the job table is also updated.

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
The method of analyzing the column names included in the other tables is the same as above and will not be repeated here.
### 2. Which line of SQL code sets up the relationship between the customer and job tables?
```
FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON  UPDATE CASCADE
```
In the job table, the customer key is a foreign key, which is the primary key customer_id in the customer table. When the value of customer_id in the customer table changes, the customer in the job table changes simultaneously. This sets up the relationship between the customer and job tables.

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
`job_service`table:  
 Column name:  `added_date`
 Data type: `DATETIME`  or  `TIMESTAMP`
    
 `job_part`table:    
Column name: `added_date`
 Data type: `DATETIME`  or  `TIMESTAMP`

### 5. Suppose logins were implemented. Why is it important for technicians and the office administrator to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
The tasks of technicians are is updating customer jobs with parts and services. But The tasks of admin staff are updating, editing and adding data. Due to different tasks, it is important for technicians and the office administrator to access different routes. 
Data breaches, if everyone can access the database, could lead to the leakage of personal user information, important information being tampered with, and more.
Function misuse. Besides the threat to data confidentiality, if no distinction is made in the interface, every employee will face a complex system. They will have to choose the functions they need from a plethora of options and may inadvertently trigger some functions that are not part of their responsibilities. This exposes each employee to many redundant functions, reducing work efficiency.

