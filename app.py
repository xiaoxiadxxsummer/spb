from decimal import Decimal

from flask import Flask, jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

# connect database

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
                                         password=connect.dbpass, host=connect.dbhost, \
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

# intercept"/"path to ensure user can enter to welcome_page
@app.route("/")
def home():
    return redirect("/welcomeHome")

# technician interface
# display incomplete job
@app.route("/technician/currentjobs")
def currentjobs():
    cursor = getCursor()
    cursor.execute("SELECT job_id,customer,job_date FROM job where completed=0;")
    jobList = cursor.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)

# display jobDetail
@app.route("/technician/jobDetail")
def jobDetail():
    cursor = getCursor()
    job_id = request.args.get('job_id', '')
    job_total_cost_str = request.args.get('job_total_cost', '0.0')
    try:
        job_total_cost = float(job_total_cost_str)
    except ValueError:
        job_total_cost = 0.0
    jobPartList, jobServiceList, partList, serviceList, job_total_cost, job = jobDetailDataPrepare(cursor, job_id)
    return render_template("jobDetail.html", job_total_cost = job_total_cost, jobPartList = jobPartList,partList = partList, jobServiceList = jobServiceList, serviceList = serviceList, job_id=job_id, job = job)

# prepare the data of jobDetail page
def jobDetailDataPrepare(cursor, job_id):
    cursor.execute(
        "Select * from (SELECT * FROM job_part where job_id=%s) A left join part on A.part_id = part.part_id",
        tuple(job_id))
    jobPartList = cursor.fetchall()
    cursor.execute("SELECT * FROM part ")
    partList = cursor.fetchall()
    cursor.execute(
        "Select * from (SELECT * FROM job_service where job_id=%s) A left join service on A.service_id = service.service_id",
        tuple(job_id))
    jobServiceList = cursor.fetchall()
    cursor.execute("SELECT * FROM service ")
    serviceList = cursor.fetchall()
    cursor.execute("select * from job where job_id = %s", tuple(job_id))
    job = cursor.fetchone()
    job_total_cost =  0 if job is None else job[3]
    print('jobPartList', jobPartList)
    print('job_List', job)
    print('job_total_cost', job_total_cost)
    print('partList', partList)
    print('jobServiceList', jobServiceList)
    print('serviceList', serviceList)
    return jobPartList, jobServiceList, partList, serviceList, job_total_cost, job

# Submit a request to modify job information
@app.route("/technician/jobDetailSubmit", methods=['POST'])
def jobDetailSubmit():
    try:
        job_id = request.args.get('job_id', '')
        job_total_cost_str = request.args.get('job_total_cost', '0.0')
        try:
            job_total_cost = float(job_total_cost_str)
        except ValueError:
            job_total_cost = 0.0
        newJobPartList = []
        newJobServiceList = []
        part_data = {}
        service_data = {}
        for key in request.form:
            if key.startswith('partSelect['):
                select_index = key.replace('partSelect[', '').replace(']', '')
                select_value = request.form[key]
                part_data[select_index] = {'part_id': select_value, 'part_number': None}
            elif key.startswith('partInput['):
                input_value = request.form[key]
                input_index = key.replace('partInput[', '').replace(']', '')
                if input_index in part_data:
                    part_data[input_index]['part_number'] = input_value
        for key in request.form:
            if key.startswith('serviceSelect['):
                select_value = request.form[key]
                select_index = key.replace('serviceSelect[', '').replace(']', '')
                service_data[select_index] = {'service_id': select_value, 'service_number': None}
            elif key.startswith('serviceInput['):
                input_index = key.replace('serviceInput[','').replace(']','')
                input_value = request.form[key]
                service_data[input_index]['service_number'] = input_value
        for index, data in part_data.items():
            select_value = data['part_id']
            input_value = data['part_number']
            if select_value and input_value:
                newJobPartList.append({"part_id": select_value, "part_number": input_value})
        for index, data in service_data.items():
            select_value = data['service_id']
            input_value = data['service_number']
            if select_value and input_value:
                newJobServiceList.append({"service_id": select_value, "service_number": input_value})
        print('job_PART_list', newJobPartList)
        print('job_service_list', newJobServiceList)
        print('job_id', job_id)
        print('job_total_cost', job_total_cost)
        if newJobPartList and newJobServiceList:
            return {
                "data": 'Something wrong,Please try again later',
                "code": 400
            }
        cursor = getCursor()
        values = [(job_id, part['part_id'], part['part_number'])for part in newJobPartList]
        query = "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)"
        cursor.executemany(query, values)
        connection.commit()
        values = [(job_id, service['service_id'], service['service_number'])for service in newJobServiceList]
        query = "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)"
        cursor.executemany(query, values)
        connection.commit()
        jobPartList, jobServiceList, partList, serviceList, job_total_cost, job = jobDetailDataPrepare(cursor, job_id)
        job_total_cost = countTotalCost(job_id, jobPartList,jobServiceList)
        return render_template("jobDetail.html", job_total_cost = job_total_cost, jobPartList = jobPartList,partList = partList, jobServiceList = jobServiceList, serviceList = serviceList, job_id=job_id, job = job)
    except Exception as e:
        connection.rollback()
        print('exception', e)
        return {
            "data": 'Something wrong,Please try again later',
            "code": 400
        }


def countTotalCost(job_id, jobPartList, jobServiceList):
    print('jobPartList', jobPartList)
    print('jobServiceList', jobServiceList)
    totalCost = 0
    for jobPart in jobPartList:
        totalCost = jobPart[5]*jobPart[2] + totalCost
    for jobService in jobServiceList:
        totalCost = jobService[5]*jobPart[2] + totalCost
    cursor = getCursor()
    query = "update job set total_cost=%s where job_id = %s"
    cursor.execute(query,(totalCost,job_id))
    return totalCost
@app.route('/technician/markJobDone')
def markJobDone():
    job_id = request.args.get('job_id', '')
    cursor = getCursor()
    query = "update job set completed = 1 where job_id = %s"
    cursor.execute(query,tuple(job_id))
    jobPartList, jobServiceList, partList, serviceList, job_total_cost, job = jobDetailDataPrepare(cursor, job_id)
    job_total_cost = countTotalCost(job_id, jobPartList, jobServiceList)
    return render_template("jobDetail.html", job_total_cost = job_total_cost, jobPartList = jobPartList,partList = partList, jobServiceList = jobServiceList, serviceList = serviceList, job_id=job_id, job = job)
@app.route('/technician/haveDoneJobs')
def haveDoneJobs():
    cursor = getCursor()
    cursor.execute("SELECT job_id,customer,job_date FROM job where completed=1;")
    jobList = cursor.fetchall()
    return render_template("jobsDone.html", job_list=jobList)
@app.route('/technician/haveDoneJob')
def haveDoneJob():
    job_id = request.args.get('job_id', '')
    cursor = getCursor()
    jobPartList, jobServiceList, partList, serviceList, job_total_cost, job = jobDetailDataPrepare(cursor, job_id)
    job_total_cost = countTotalCost(job_id, jobPartList, jobServiceList)
    return render_template("jobDone.html", job_total_cost=job_total_cost, jobPartList=jobPartList, partList=partList,
                           jobServiceList=jobServiceList, serviceList=serviceList, job_id=job_id, job=job)
# the homepage of the system
@app.route("/welcomeHome")
def welcome_home():
    return render_template('welcome_page.html')

# The route to the page for modifying user information.
@app.route("/manager/customer/customerManagaement")
def customerManagement():
    cursor = getCursor()
    cursor.execute("Select * from customer order by customer.family_name,customer.first_name")
    customer_list = cursor.fetchall()
    return render_template('customer_management.html', customer_list=customer_list)

# Response to the request to add a user.
@app.route("/manager/customer/addCustomer", methods=['GET', 'POST'])
def addCustomer():
    customer_info = request.get_json()
    cursor = getCursor()
    query = "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s)"
    values = (customer_info['firstname'], customer_info['familyname'], customer_info['email'], customer_info['phone'])
    cursor.execute(query, values)
    cursor.execute("Select * from customer order by customer.family_name,customer.first_name")
    newCustomerList = cursor.fetchall()
    return {
        "data": newCustomerList,
        "code": 200
    }

# Response to the request to search user information
@app.route('/manager/customer/searchCustomer', methods=['GET'])
def searchCustomer():
    search_keyword = request.args.get('search_keyword', '')
    cursor = getCursor()
    query = "select * from customer where customer.first_name like  %s or customer.family_name like  %s"
    values = ("%" + search_keyword + "%", "%" + search_keyword + "%")
    cursor.execute(query, values)
    customer_list = cursor.fetchall()
    return {
        "data": customer_list,
        "code": 200
    }

# The route to the page for modifying part information.
@app.route('/manager/part/partsManagement')
def partsManagement():
    cursor = getCursor()
    cursor.execute("Select * from part order by part.part_name")
    part_list = cursor.fetchall()
    print('part_list', part_list)
    return render_template('parts_management.html', part_list=part_list)

# response to the request to add Part
@app.route('/manager/part/addPart', methods=['GET', 'POST'])
def addPart():
    try:
        part_info = request.get_json()
        print('part_info', part_info)
        cursor = getCursor()
        query = "insert into part(part_name,cost) values (%s,%s)"
        part_cost = float(part_info['part_cost'])
        # solve the problem of cost exceeding the range when inserted into the database
        if part_cost>=1000.00:
            return {
                "data": 'the cost of a part should be lower than 1000',
                "code": 400
            }
        value = (part_info['part_name'], part_cost)
        cursor.execute(query, value)
        connection.commit()
        cursor.execute("Select * from part order by part.part_name")
        connection.close()
        newPartList = cursor.fetchall()
        return {
            "data": newPartList,
            "code": 200
        }
    except Exception as e:
        connection.rollback()
        print('exception', e)
        return {
            "data": 'Something wrong,Please try again later',
            "code": 400
        }

# The route to the page for modifying service information.
@app.route('/manager/service/servicesManagement')
def servicesManagement():
    cursor = getCursor()
    cursor.execute("Select * from service order by service.service_name")
    service_list = cursor.fetchall()
    print('service_list', service_list)
    return render_template('services_management.html', service_list=service_list)

# response to the request to add Service
@app.route('/manager/service/addService', methods=['GET', 'POST'])
def addService():
    try:
        service_info = request.get_json()
        cursor = getCursor()
        query = "insert into service(service_name,cost) values (%s,%s)"
        service_cost = float(service_info['service_cost'])
        # solve the problem of cost exceeding the range when inserted into the database
        if service_cost>=1000:
             return {
                "data": 'The cost of a service should be lower than 1000',
                "code": 400
            }
        value = (service_info['service_name'], service_cost)
        print('value', value)
        cursor.execute(query, value)
        connection.commit()
        cursor.execute("Select * from service order by service.service_name")
        connection.close()
        newServiceList = cursor.fetchall()
        print('return information')
        return {
            "data": newServiceList,
            "code": 200
        }
    except Exception as e:
        connection.rollback()
        print('addService', e)
        return {
            "data": 'Something wrong,Please try again later',
            "code": 400
        }

# The route to the page for modifying bill information.
@app.route('/manager/manager/manager/unpaidBill/searchUnpaidBillByName')
def unpaidBillManagement():
    cursor = getCursor()
    # displaying both family name and first name sitmultaneously is more friendly
    cursor.execute(
        "select job.*,CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name from job left join customer on job.customer= customer.customer_id where job.paid = 0 order by job.job_date ")
    unpaid_bill_list = cursor.fetchall()
    print('unpaid_bill_list', unpaid_bill_list)
    cursor.execute(
        "select distinct customer_id, CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name from customer ")
    unpaid_bill_user = cursor.fetchall()
    return render_template('unpaid_bill_management.html', unpaid_bill_list=unpaid_bill_list,
                           unpaid_bill_user=unpaid_bill_user)

# response to the request to search unpaid bill
@app.route('/manager/unpaidBill/searchUnpaidBillByName', methods=['GET', 'POST'])
def searchUnpaidBillByName():
    request_data = request.get_json()
    print('customer_id', request_data['customer_id'])
    cursor = getCursor()
    query = "select job.*,CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name from job left join  customer   on job.customer = customer.customer_id where job.paid = 0 and customer.customer_id = %s"
    value = [request_data['customer_id']]
    cursor.execute(query, value)
    userUnpaidBill = cursor.fetchall()
    print('userUnpaidBill', userUnpaidBill)
    return {
        "data": userUnpaidBill,
        "code": 200
    }

# pay bill
@app.route('/manager/unpaidBill/payBill', methods=['POST'])
def payBill():
    request_data = request.get_json()
    print('customer_id', request_data['customer_id'])
    print('job_date', request_data['job_date'])
    cursor = getCursor()
    query= "update job set paid = 1 where customer = %s and job_date = %s"
    value = (request_data['customer_id'], request_data['job_date'])
    cursor.execute(query,value)
    return {
        "data": 'already paid success',
        "code": 200
    }
# get overdue bill information
@app.route('/manager/unpaidBill/getOverdueBill')
def getOverdueBill():
    customer_bills = {}
    cursor = getCursor()
    # Calculate the difference between the currentdate and the job date in 'job' table, where the difference is greater than or equal to 14 days, using DATEDIFF(CURDATE(), job.job_date)
    # To find the customer_id associated with jobs that have not been paid for more than 14 days and sort them based on the job_date
    cursor.execute("""    
        SELECT customer_id    
        FROM (    
            SELECT customer.customer_id, job.job_date    
            FROM job    
            LEFT JOIN customer ON job.customer = customer.customer_id    
            WHERE job.paid = 0 AND DATEDIFF(CURDATE(), job.job_date) > 14    
        ) AS subquery    
        GROUP BY customer_id    
        ORDER BY MIN(job_date)    
    """)
    overdue_bill_customer_ids = cursor.fetchall()
    print('overdue_bill_customer_id', overdue_bill_customer_ids)
    customer_id_placeholders = ', '.join(['%s'] * len(overdue_bill_customer_ids))
    query = f"""  
        SELECT job.*, CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name, customer.customer_id, customer.email, customer.phone  
        FROM job  
        LEFT JOIN customer ON job.customer = customer.customer_id  
        WHERE job.customer IN ({customer_id_placeholders}) AND job.paid = 0  AND DATEDIFF(CURDATE(), job.job_date) > 14 
    """
    cursor.execute(query, [customer_id[0] for customer_id in overdue_bill_customer_ids])
    overdue_bills = cursor.fetchall()
    print('overdue_bills', overdue_bills)
    # Convert data structure
    customer_ids = [customer_id[0] for customer_id in overdue_bill_customer_ids]
    print('customer_ids', customer_ids)
    for bill in overdue_bills:
        customer_id = bill[7]
        if customer_id in customer_ids:
            if customer_id not in customer_bills:
                customer_bills[customer_id] = []
            customer_bills[customer_id].append(bill)
    print('customer_bills', customer_bills)
    return render_template('overdue_bill_management.html', customer_bills = customer_bills)
# display schedulejob page
@app.route('/manager/bill/getScheduleJobPage')
def getScheduleJobPage():
    cursor = getCursor()
    cursor.execute(
        "select job.*, customer.customer_id, CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name from job left join customer on job.customer= customer.customer_id order by job.job_date ")
    bill_list = cursor.fetchall()
    print('bill_list', bill_list)
    cursor.execute(
        "select distinct customer_id,CONCAT_WS(' ', COALESCE(customer.first_name, ''), COALESCE(customer.family_name, '')) AS full_name from customer ")
    user_list = cursor.fetchall()
    return render_template('schedule_job.html', bill_list=bill_list,
                           user_list=user_list)

# schedule job
@app.route('/manager/bill/scheduleJob', methods=['POST'])
def scheduleJob():
    request_data = request.get_json()
    print(request_data['customer_id'])
    print(request_data['schedule_date'])
    cursor = getCursor()
    cursor.execute("insert into job(customer,job_date) values(%s,%s)",
                   (request_data['customer_id'], request_data['schedule_date']))
    connection.commit()
    cursor.execute(
        "select job.*,CONCAT(customer.first_name,' ',customer.family_name)as full_name from job left join customer on job.customer= customer.customer_id order by job.job_date ")
    bill_list = cursor.fetchall()
    cursor.execute(
        "select distinct customer_id, CONCAT(customer.first_name,' ',customer.family_name)as full_name from customer ")
    user_list = cursor.fetchall()
    return {
        "code": 200,
        "data": {
            "bill_list": bill_list,
            "user_list": user_list
        }
    }
