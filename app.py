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


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
                                         password=connect.dbpass, host=connect.dbhost, \
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return redirect("/welcomeHome")


# @app.route("/currentjobs")
# def currentjobs():
#     cursor = getCursor()
#     cursor.execute("SELECT job_id,customer,job_date FROM job where completed=0;")
#     jobList = cursor.fetchall()
#     return render_template("currentjoblist.html", job_list=jobList)
#
#
# @app.route("/basehtml")
# def login():
#     return render_template('base.html')


# @app.route("/customer/listCustomer")
# def listCustomer():
#     cursor = getCursor()
#     cursor.execute("Select * from customer")
#     customer_list = cursor.fetchall()
#     return render_template('customer_management.html', customer_list=customer_list)


@app.route("/welcomeHome")
def welcome_home():
    return render_template('welcome_page.html')


@app.route("/customer/customerTest")
def customerTest():
    cursor = getCursor()
    cursor.execute("Select * from customer order by customer.family_name,customer.first_name")
    customer_list = cursor.fetchall()
    return render_template('customer_test.html', customer_list=customer_list)


@app.route("/customer/addCustomer", methods=['GET', 'POST'])
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


@app.route('/customer/searchCustomer', methods=['GET'])
def searchCustomer():
    search_keyword = request.args.get('search_keyword', '')
    cursor = getCursor()
    query = "select * from customer where customer.first_name like  %s or customer.family_name like  %s "
    values = ("%" + search_keyword + "%", "%" + search_keyword + "%")
    cursor.execute(query, values)
    customer_list = cursor.fetchall()
    return {
        "data": customer_list,
        "code": 200
    }


@app.route('/part/partsManagement')
def partsManagement():
    cursor = getCursor()
    cursor.execute("Select * from part order by part.part_name")
    part_list = cursor.fetchall()
    print('part_list', part_list)
    return render_template('parts_management.html', part_list=part_list)


@app.route('/part/addPart', methods=['GET', 'POST'])
def addPart():
    part_info = request.get_json()
    print('part_info', part_info)
    cursor = getCursor()
    query = "insert into part(part_name,cost) values (%s,%s)"
    value = (part_info['part_name'], part_info['part_cost'])
    cursor.execute(query, value)
    connection.commit()
    cursor.execute("Select * from part order by part.part_name")
    newPartList = cursor.fetchall()
    return {
        "data": newPartList,
        "code": 200
    }


@app.route('/service/servicesManagement')
def servicesManagement():
    cursor = getCursor()
    cursor.execute("Select * from service order by service.service_name")
    service_list = cursor.fetchall()
    print('service_list', service_list)
    return render_template('services_management.html', service_list=service_list)


@app.route('/service/addService', methods=['GET', 'POST'])
def addService():
    service_info = request.get_json()
    print('service_info', service_info)
    cursor = getCursor()
    query = "insert into service(service_name,cost) values (%s,%s)"
    value = (service_info['service_name'], service_info['service_cost'])
    cursor.execute(query, value)
    connection.commit()
    cursor.execute("Select * from service order by service.service_name")
    newServiceList = cursor.fetchall()
    return {
        "data": newServiceList,
        "code": 200
    }


@app.route('/unpaidBill/unpaidBillManagement')
def unpaidBillManagement():
    cursor = getCursor()
    cursor.execute(
        "select job.*,CONCAT(customer.first_name,' ',customer.family_name)as full_name from job left join customer on job.customer= customer.customer_id where job.paid = 0 order by job.job_date ")
    unpaid_bill_list = cursor.fetchall()
    print('unpaid_bill_list', unpaid_bill_list)
    cursor.execute(
        "select distinct customer_id, CONCAT(customer.first_name,' ',customer.family_name)as full_name from customer ")
    unpaid_bill_user = cursor.fetchall()
    return render_template('unpaid_bill_management.html', unpaid_bill_list=unpaid_bill_list,
                           unpaid_bill_user=unpaid_bill_user)


@app.route('/unpaidBill/searchUnpaidBillByName', methods=['GET', 'POST'])
def searchUnpaidBillByName():
    request_data = request.get_json()
    print('customer_id', request_data['customer_id'])
    cursor = getCursor()
    query = "select job.*,CONCAT(customer.first_name,' ',customer.family_name)as full_name from job left join  customer   on job.customer = customer.customer_id where job.paid = 0 and customer.customer_id = %s"
    value = [request_data['customer_id']]
    cursor.execute(query, value)
    userUnpaidBill = cursor.fetchall()
    print('userUnpaidBill', userUnpaidBill)
    return {
        "data": userUnpaidBill,
        "code": 200
    }


@app.route('/bill/getScheduleJobPage')
def getScheduleJobPage():
    cursor = getCursor()
    cursor.execute(
        "select job.*,CONCAT(customer.first_name,' ',customer.family_name)as full_name from job left join customer on job.customer= customer.customer_id order by job.job_date ")
    bill_list = cursor.fetchall()
    print('bill_list', bill_list)
    cursor.execute(
        "select distinct customer_id, CONCAT(customer.first_name,' ',customer.family_name)as full_name from customer ")
    user_list = cursor.fetchall()
    return render_template('schedule_job.html', bill_list=bill_list,
                           user_list=user_list)


@app.route('/bill/scheduleJob', methods=['POST'])
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
