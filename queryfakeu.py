import psycopg2
import csv
import os
import time

connection = psycopg2.connect("dbname=fakeudata")
cursor = connection.cursor()

def partA():
    print("PartA: ")
    print("(1 Unit)")
    cursor.execute("""
        SELECT  LEN()
        FROM    Enrolled, Course 
        WHERE   SUBJ = 'ABC' OR SUBJ = 'DEF' AND Units = '1';
    """) 
    rows = cursor.fetchall()
    print(len(rows))

def partB():
    print("PartB ")
    print("Hardest Instructor: ")

    cursor.execute("""
        SELECT  *
            INTO Emp_subset
        FROM    Enrolled
        WHERE   Grade != 'NP' OR Grade != 'P' OR Grade != 'S' OR Grade != 'NS';
    """) 

    cursor.execute(""" 
        SELECT *
            INTO Emp1_subset
        FROM Emp_subset 
        WHERE 
    
    """)

    cursor.execute(""" 
        DROP TABLE Emp_subset;
    """)

partA()
#partB()

befh 