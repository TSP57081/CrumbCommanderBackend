import mysql.connector
from dotenv import load_dotenv
import os
 
load_dotenv()
 
username = os.getenv("DBUSERNAME")
password = os.getenv("PASSWORD")
DB_host = os.getenv("HOST")
DATABASE_NAME = os.getenv("DATABASE")
 
conn = mysql.connector.connect(
            host= DB_host,
            user = username,
            password = password,
        )
 
cursor = conn.cursor()
 
cursor.execute("CREATE DATABASE IF NOT EXISTS " + DATABASE_NAME)
 
cursor.execute("USE " + DATABASE_NAME)

create_table_query = """
    CREATE TABLE Employees (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100),
    PhoneNumber VARCHAR(20),
    EmploymentStartDate DATE
);
"""
cursor.execute(create_table_query)

cursor.execute("""
    CREATE TABLE EmployeeShifts (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT,
    EmployeeName VARCHAR(20),
    StartTime TIME,
    EndTime TIME,
    Date DATE
);
""")

cursor.execute("""
    CREATE TABLE Availability (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT,
    DayOfWeek VARCHAR(20),
    StartTime1 TIME,
    EndTime1 TIME,
    StartTime2 TIME,
    EndTime2 TIME,
    -- Add more columns as needed for additional time ranges
    FOREIGN KEY (EmployeeID) REFERENCES Employees(ID)
);
""")

conn.commit()
conn.close()