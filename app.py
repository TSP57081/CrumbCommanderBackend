from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_NAME = "your_database.db"  # Change this to your desired SQLite database name

# Function to establish SQLite connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Function to create necessary tables in SQLite database
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT,
        LastName TEXT,
        Email TEXT,
        PhoneNumber TEXT,
        EmploymentStartDate DATE
    );
    """)

    # Create EmployeeShifts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EmployeeShifts (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER,
        EmployeeName TEXT,
        StartTime TEXT,
        EndTime TEXT,
        Date DATE
    );
    """)

    # Create Availability table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Availability (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER,
        DayOfWeek TEXT,
        StartTime1 TEXT,
        EndTime1 TEXT,
        StartTime2 TEXT,
        EndTime2 TEXT,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(ID)
    );
    """)

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Create tables when the application starts
create_tables()

# Function to get SQLite cursor
def get_db_cursor():
    conn = get_db_connection()
    return conn.cursor()

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.json
    print("Add Employee API Called")
    print(data)
    sql = "INSERT INTO Employees (FirstName, LastName, Email, PhoneNumber, EmploymentStartDate) VALUES (?, ?, ?, ?, ?)"
    values = (data['FirstName'], data['LastName'], data['Email'], data['PhoneNumber'], data['EmploymentStartDate'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Employee added successfully"}), 200

@app.route('/add_employee_shift', methods=['POST'])
def add_employee_shift():
    data = request.json
    sql = "INSERT INTO EmployeeShifts (EmployeeID, EmployeeName, StartTime, EndTime, Date) VALUES (?, ?, ?, ?, ?)"
    values = (data['EmployeeID'], data['EmployeeName'], data['StartTime'], data['EndTime'], data['Date'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Employee shift added successfully"}), 200

@app.route('/add_availability', methods=['POST'])
def add_availability():
    data = request.json
    sql = """
        INSERT OR REPLACE INTO Availability 
        (EmployeeID, DayOfWeek, StartTime1, EndTime1, StartTime2, EndTime2) 
        VALUES (?, ?, ?, ?, ?, ?)
    """
    values = (
        data['EmployeeID'],
        data['DayOfWeek'],
        data['StartTime1'],
        data['EndTime1'],
        data['StartTime2'],
        data['EndTime2']
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Availability added or updated successfully"}), 200


@app.route('/find_available_employees', methods=['POST'])
def find_available_employees():
    data = request.json
    start_time = data.get('StartTime')
    end_time = data.get('EndTime')
    day_of_week = data.get('DayOfWeek')

    sql = """
        SELECT e.ID, e.FirstName, e.LastName
        FROM Employees e
        LEFT JOIN Availability a ON e.ID = a.EmployeeID
        WHERE (a.DayOfWeek = ?) AND ((a.StartTime1 <= ? AND a.EndTime1 >= ?) OR (a.StartTime2 <= ? AND a.EndTime2 >= ?))
    """
    values = (day_of_week, start_time, end_time, start_time, end_time)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    available_employees = cursor.fetchall()
    conn.close()

    if available_employees:
        result = [{"EmployeeID": emp['ID'], "FirstName": emp['FirstName'], "LastName": emp['LastName']} for emp in available_employees]
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
    sql = "UPDATE EmployeeShifts SET EmployeeID = ?, EmployeeName = ? WHERE ID = ?"
    values = (new_employee_id, new_employee_name, shift_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        return jsonify({"message": "Employee for the shift updated successfully"}), 200
    except sqlite3.Error as err:
        conn.rollback()
        conn.close()
        return jsonify({"message": f"Failed to update employee for the shift: {err}"}), 500
    
@app.route('/get_user_by_id', methods=['GET'])
def get_user_by_id():
    user_id = request.args.get('UserID')

    # Query to retrieve user data by ID
    sql = "SELECT * FROM Employees WHERE ID = ?"
    values = (user_id,)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
@app.route('/get_all_shifts', methods=['GET'])
def get_all_shifts():
    # Query to fetch all shifts
    sql = "SELECT * FROM EmployeeShifts"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    shifts = cursor.fetchall()
    conn.close()
    
    shifts_data = []

    if shifts:
        for shift in shifts:
            # Create a dictionary representing the shift object
            shift_data = {
                "ShiftID": shift['ID'],
                "EmployeeID": shift['EmployeeID'],
                "EmployeeName": shift['EmployeeName'],
                "StartTime": str(shift['StartTime']),
                "EndTime": str(shift['EndTime']),
                "Date": str(shift['Date'])
            }
            # Append the dictionary to the list
            shifts_data.append(shift_data)
        return jsonify({"message": "All shifts retrieved successfully", "shifts": shifts_data}), 200
    else:
        return jsonify({"message": "No shifts found"}), 404
    
@app.route('/get_shifts_for_individual', methods=['GET'])
def get_shifts_for_individual():
    user_id = request.args.get('UserID')

    sql = "SELECT * FROM EmployeeShifts WHERE ID = ?"
    values = (user_id,)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    shifts = cursor.fetchall()
    conn.close()

    if shifts:
        shifts_data = [{"ShiftID": shift['ID'], "EmployeeID": shift['EmployeeID'], "EmployeeName": shift['EmployeeName'], "StartTime": shift['StartTime'], "EndTime": shift['EndTime'], "Date": shift['Date']} for shift in shifts]
        return jsonify({"message": "All shifts retrieved successfully", "shifts": shifts_data}), 200
    else:
        return jsonify({"message": "No shifts found"}), 404
    
@app.route('/get_availabilities_for_individual', methods=['GET'])
def get_availabilities_for_individual():
    user_id = request.args.get('UserID')

    sql = "SELECT * FROM Availability WHERE EmployeeID = ?"
    values = (user_id,)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    availabilities = cursor.fetchall()
    conn.close()

    availability_data_array = []

    if availabilities:
        for availability in availabilities:
            availability_data = {
                "Date": str(availability['Date']),
                "EmployeeID": str(availability['EmployeeID']),
                "EmployeeName": availability['EmployeeName'],
                "StartTime": str(availability['StartTime']),
                "EndTime": str(availability['EndTime']),
                "DayOfWeek": availability['DayOfWeek']
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
    sql = "SELECT Email FROM Employees WHERE ID = ?"
    values = (user_id,)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    email = cursor.fetchone()
    conn.close()

    if email:
        return jsonify({"message": "Email retrieved successfully", "email": email['Email']}), 200
    else:
        return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
