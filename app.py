from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

username = os.getenv("DBUSERNAME")
password = os.getenv("PASSWORD")
DB_host = os.getenv("HOST")
DATABASE_NAME = os.getenv("DATABASE")

conn = mysql.connector.connect(
    host=DB_host,
    user=username,
    password=password,
    database=DATABASE_NAME
)

cursor = conn.cursor()

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.json
    print("Add Employee API Called")
    print(data)
    sql = "INSERT INTO Employees (FirstName, LastName, Email, PhoneNumber, EmploymentStartDate) VALUES (%s, %s, %s, %s, %s)"
    values = (data['FirstName'], data['LastName'], data['Email'], data['PhoneNumber'], data['EmploymentStartDate'])
    cursor.execute(sql, values)
    conn.commit()
    return jsonify({"message": "Employee added successfully"}), 200


@app.route('/add_employee_shift', methods=['POST'])
def add_employee_shift():
    data = request.json
    sql = "INSERT INTO EmployeeShifts (EmployeeID, EmployeeName, StartTime, EndTime, Date) VALUES (%s, %s, %s, %s, %s)"
    values = (data['EmployeeID'], data['EmployeeName'], data['StartTime'], data['EndTime'], data['Date'])
    cursor.execute(sql, values)
    conn.commit()
    return jsonify({"message": "Employee shift added successfully"}), 200


@app.route('/add_availability', methods=['POST'])
def add_availability():
    data = request.json
    sql = "INSERT INTO Availability (EmployeeID, DayOfWeek, StartTime1, EndTime1, StartTime2, EndTime2) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (data['EmployeeID'], data['DayOfWeek'], data['StartTime1'], data['EndTime1'], data['StartTime2'], data['EndTime2'])
    cursor.execute(sql, values)
    conn.commit()
    return jsonify({"message": "Availability added successfully"}), 200

@app.route('/find_available_employees', methods=['POST'])
def find_available_employees():
    data = request.json
    start_time = data.get('StartTime')
    end_time = data.get('EndTime')
    day_Of_Week = data.get('DayOfWeek')

    sql = """
        SELECT e.ID, e.FirstName, e.LastName
        FROM Employees e
        LEFT JOIN Availability a ON e.ID = a.EmployeeID
        WHERE (a.DayOfWeek = %s) AND (a.StartTime1 <= %s AND a.EndTime1 >= %s) OR (a.StartTime2 <= %s AND a.EndTime2 >= %s)
    """
    values = (day_Of_Week, start_time, end_time, start_time, end_time)
    cursor.execute(sql, values)
    available_employees = cursor.fetchall()

    if available_employees:
        result = [{"EmployeeID": emp[0], "FirstName": emp[1], "LastName": emp[2]} for emp in available_employees]
        return jsonify({"message": "Available employees for the provided shift timings", "employees": result}), 200
    else:
        return jsonify({"message": "No available employees for the provided shift timings"}), 404
    
@app.route('/change_employee_for_shift', methods=['PUT'])
def change_employee_for_shift():
    data = request.json
    shift_id = data.get('ShiftID')
    new_employee_id = data.get('NewEmployeeID')
    new_employee_name = data.get('NewEmployeeName')

    # Update the EmployeeID for the specified shift
    sql = "UPDATE EmployeeShifts SET EmployeeID = %s, EmployeeName = %s WHERE ID = %s"
    values = (new_employee_id, new_employee_name, shift_id)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({"message": "Employee for the shift updated successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Failed to update employee for the shift: {err}"}), 500
    
@app.route('/get_user_by_id', methods=['GET'])
def get_user_by_id():
    user_id = request.args.get('UserID')

    # Query to retrieve user data by ID
    sql = "SELECT * FROM Employees WHERE ID = %s"
    values = (user_id,)

    cursor.execute(sql, values)
    user_data = cursor.fetchone()

    if user_data:
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
@app.route('/get_all_shifts', methods=['GET'])
def get_all_shifts():
    # Query to fetch all shifts
    sql = "SELECT * FROM EmployeeShifts"
    cursor.execute(sql)
    shifts = cursor.fetchall()
    shifts_data = []

    if shifts:
        for shift in shifts:
            # Create a dictionary representing the shift object
            shift_data = {
                "ShiftID": shift[0],
                "EmployeeID": shift[1],
                "EmployeeName": shift[2],
                "StartTime": str(shift[3]),
                "EndTime": str(shift[4]),
                "Date": str(shift[5])
            }
            # Append the dictionary to the list
            shifts_data.append(shift_data)
        return jsonify({"message": "All shifts retrieved successfully", "shifts": shifts_data}), 200
    else:
        return jsonify({"message": "No shifts found"}), 404
    
@app.route('/get_shifts_for_individual', methods=['GET'])
def get_shifts_for_individual():
    user_id = request.args.get('UserID')

    sql = "SELECT * FROM EmployeeShifts WHERE ID = %s"
    values = (user_id,)
    cursor.execute(sql,values)
    shifts = cursor.fetchall()

    if shifts:
        shifts_data = [{"ShiftID": shift[0], "EmployeeID": shift[1], "EmployeeName": shift[2], "StartTime": shift[3], "EndTime": shift[4], "Date": shift[5]} for shift in shifts]
        return jsonify({"message": "All shifts retrieved successfully", "shifts": shifts_data}), 200
    else:
        return jsonify({"message": "No shifts found"}), 404
    
@app.route('/get_availabilities_for_individual', methods=['GET'])
def get_availabilities_for_individual():
    user_id = request.args.get('UserID')

    sql = "SELECT * FROM Availability WHERE EmployeeID = %s"
    values = (user_id,)
    cursor.execute(sql, values)
    availabilities = cursor.fetchall()
    availability_data_array = []

    if availabilities:
        for availability in availabilities:
            availability_data = {
                "Date": str(availability[0]),
                "EmployeeID": str(availability[1]),
                "EmployeeName": availability[2],
                "StartTime": str(availability[3]),
                "EndTime": str(availability[4]),
                "DayOfWeek": availability[5]
            }
            # Append the dictionary to the list
            availability_data_array.append(availability_data)
        return jsonify({"message": "All availabilities retrieved successfully", "availabilities": availability_data_array}), 200
    else:
        return jsonify({"message": "No availabilities found"}), 404
    

@app.route('/get_email_by_id', methods=['GET'])
def get_email_by_id():
    user_id = request.args.get('UserID')

    # Query to retrieve user email by ID
    sql = "SELECT Email FROM Employees WHERE ID = %s"
    values = (user_id,)

    cursor.execute(sql, values)
    email = cursor.fetchone()

    if email:
        return jsonify({"message": "Email retrieved successfully", "email": email[0]}), 200
    else:
        return jsonify({"message": "User not found"}), 404



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
