import psycopg2
import csv
import os
import time

connection = psycopg2.connect("dbname=fakeudata")
cursor = connection.cursor()


def partB():
    print("PartB ")

    cursor.execute("""
        SELECT Meeting.CID AS CID, Instructor, Grade
        INTO temp
        FROM Meeting
        INNER JOIN Enrolled ON Meeting.CID = Enrolled.CID
        WHERE Grade = 'A+' OR Grade = 'A' OR Grade = 'A-';

        SELECT CID, COUNT(*) AS Count, Instructor
        FROM temp
        GROUP BY CID, Instructor
        ORDER BY Count DESC;
    """) 

    count_grade = cursor.fetchall()

    cursor.execute("""
        SELECT Grade
        INTO temp2
        FROM Enrolled
        WHERE CID = %s """,  [count_grade[0][0]]
    )

    cursor.execute(""" 
        SELECT Grade, COUNT(Grade) AS Count
        FROM temp2
        GROUP BY Grade
        ORDER BY Count DESC;
        """)

    avg = cursor.fetchall()

    #for row in avg :
       # print row 
    print "EASIEST PROFESSOR:", count_grade[0][2], "AVG GRADE =", avg[0][0]

    cursor.execute("DROP TABLE temp, temp2")

    cursor.execute("""
        SELECT Meeting.CID AS CID, Instructor, Grade
        INTO temp
        FROM Meeting
        INNER JOIN Enrolled ON Meeting.CID = Enrolled.CID
        WHERE Grade = 'F' OR Grade = 'D';

        SELECT CID, COUNT(*) AS Count, Instructor
        FROM temp
        GROUP BY CID, Instructor
        ORDER BY Count DESC;
    """) 

    count_grade = cursor.fetchall()

    cursor.execute("""
        SELECT Grade
        INTO temp2
        FROM Enrolled
        WHERE CID = %s """,  [count_grade[0][0]]
    )

    cursor.execute(""" 
        SELECT Grade, COUNT(Grade) AS Count
        FROM temp2
        GROUP BY Grade
        ORDER BY Count DESC;
        """)

    avg = cursor.fetchall()

    print "HARDEST PROFESSOR:", count_grade[0][2], "AVG GRADE =", avg[0][0], "\n"

    cursor.execute("DROP TABLE temp, temp2")

def partE() :
    print("PartE: ")

    # remove the summer quarter
    cursor.execute(""" 
        SELECT Course.CID AS CID, Instructor, Meeting.Term AS Term, Time, Subj,Crse
        INTO temp
        FROM Meeting
        INNER JOIN Course ON Course.CID = Meeting.CID AND Time != 'None'
        WHERE NOT CAST(Meeting.Term AS TEXT) LIKE '%06a';
    """)

    #CID's not equal, Subj not equal, TERM equal, Instructor Equal
    cursor.execute("""
        SELECT T1.CID AS CID1, T1.SUBJ AS SUBJ1, T1.Crse AS CRSE1, T2.CID AS CID2, T2.SUBJ AS SUBJ2, T2.Crse AS CRSE2
        INTO temp2
        FROM temp T1, temp T2
        WHERE T1.CID != T2.CID AND T1.CID < T2.CID AND T1.SUBJ != T2.SUBJ AND T1.Crse != T2.Crse AND T1.Term = T2.Term AND T1.Instructor = T2.Instructor 
        AND T1.Time = T2.Time;

        SELECT DISTINCT * 
        FROM temp2 
        GROUP BY CID1, SUBJ1, CRSE1, CID2, SUBJ2, CRSE2
        ORDER BY SUBJ1;
    """)

    join_data = cursor.fetchall()
    
    for i, row in enumerate(join_data) :
       print join_data[i][0], join_data[i][1], join_data[i][2],join_data[i][3], join_data[i][4], join_data[i][5]
    
    cursor.execute("DROP TABLE temp, temp2")

def partF() :
    print("PartF: \n")

    print("ABC: \n")

    cursor.execute("""
        CREATE TABLE Chart(
			Grade VARCHAR(5),
			UNITS DECIMAL(3,1),
			PRIMARY KEY(UNITS, GRADE)
		)
    """)

    cursor.execute("""
        INSERT INTO Chart VALUES 
        ('A+', 4.000),
        ('A', 4.000),
        ('A-', 3.700),
        ('B+', 3.300),
        ('B', 3.000),
        ('B-', 2.700),
        ('C+', 2.300),
        ('C', 2.000),
        ('C-', 1.700),
        ('D+', 1.300),
        ('D', 1.000),
        ('D-', 0.700),
        ('F', 0.000)
    """)

    cursor.execute("""
        SELECT SUBJ, MAJOR, GRADE 
        INTO temp
        FROM Course
        INNER JOIN Enrolled ON Enrolled.CID = Course.CID AND SUBJ = 'ABC'
        WHERE Grade = 'A+' OR Grade = 'A' OR Grade = 'A-' OR Grade = 'B+' OR Grade = 'B' OR Grade = 'B-' OR Grade = 'C+'
        OR Grade = 'C' OR Grade = 'C-' OR Grade = 'D+' OR Grade = 'D' OR Grade = 'D-' OR Grade = 'F';
    """)

    cursor.execute("""
        SELECT SUBJ, MAJOR, Grade, COUNT(GRADE) AS COUNT
        INTO temp2
        FROM temp
        GROUP BY MAJOR, SUBJ, Grade;
    """)

    cursor.execute("""
        SELECT MAJOR, Chart.Grade AS Grade, UNITS, COUNT, UNITS*COUNT AS UNITCOUNT
        INTO temp3
        FROM temp2
        INNER JOIN Chart ON Chart.Grade = temp2.Grade
        ORDER BY MAJOR, Grade;
    """)

    # REFRENCED FROM https://stackoverflow.com/questions/12864467/how-to-take-sum-of-column-with-same-id-in-sql
    cursor.execute("""
        SELECT DISTINCT T.MAJOR AS MAJOR, GPA * 4 AS GPA
        INTO temp4
        FROM temp3 AS T
        JOIN (SELECT MAJOR, ((SUM(UNITCOUNT) * 4) / (SUM(COUNT) * 16)) AS GPA
                FROM temp3
                GROUP BY MAJOR
        ) AS T2 ON T.MAJOR = T2.MAJOR
        ORDER BY GPA DESC;
    """)

    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '4.0';
    """)



    best_data = cursor.fetchall()
    print "BEST:"
    for i, row in enumerate(best_data) :
       print best_data[i][0]
    print " "
    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '0.0';
    """)

    worst_data = cursor.fetchall()
    print "WORST:"
    for i, row in enumerate(worst_data) :
       print worst_data[i][0]
    

    cursor.execute("DROP TABLE temp, temp2, temp3, temp4")

    print " "

    print "DEF: \n"

    cursor.execute("""
        SELECT SUBJ, MAJOR, GRADE 
        INTO temp
        FROM Course
        INNER JOIN Enrolled ON Enrolled.CID = Course.CID AND SUBJ = 'DEF'
        WHERE Grade = 'A+' OR Grade = 'A' OR Grade = 'A-' OR Grade = 'B+' OR Grade = 'B' OR Grade = 'B-' OR Grade = 'C+'
        OR Grade = 'C' OR Grade = 'C-' OR Grade = 'D+' OR Grade = 'D' OR Grade = 'D-' OR Grade = 'F';
    """)

    cursor.execute("""
        SELECT SUBJ, MAJOR, Grade, COUNT(GRADE) AS COUNT
        INTO temp2
        FROM temp
        GROUP BY MAJOR, SUBJ, Grade;
    """)

    cursor.execute("""
        SELECT MAJOR, Chart.Grade AS Grade, UNITS, COUNT, UNITS*COUNT AS UNITCOUNT
        INTO temp3
        FROM temp2
        INNER JOIN Chart ON Chart.Grade = temp2.Grade
        ORDER BY MAJOR, Grade;
    """)

    # REFRENCED FROM https://stackoverflow.com/questions/12864467/how-to-take-sum-of-column-with-same-id-in-sql
    cursor.execute("""
        SELECT DISTINCT T.MAJOR AS MAJOR, GPA * 4 AS GPA
        INTO temp4
        FROM temp3 AS T
        JOIN (SELECT MAJOR, ((SUM(UNITCOUNT) * 4) / (SUM(COUNT) * 16)) AS GPA
                FROM temp3
                GROUP BY MAJOR
        ) AS T2 ON T.MAJOR = T2.MAJOR
        ORDER BY GPA DESC;
    """)

    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '4.0';
    """)

    best_data = cursor.fetchall()
    print "BEST:"
    for i, row in enumerate(best_data) :
       print best_data[i][0]
    print " "
    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '0.0';
    """)

    worst_data = cursor.fetchall()
    print "WORST:"
    for i, row in enumerate(worst_data) :
       print worst_data[i][0]

    cursor.execute("DROP TABLE temp, temp2, temp3, temp4, Chart")



def partH() :
    print("PartH: \n")

    cursor.execute("""
        SELECT DISTINCT A.SID AS SID, A.MAJOR AS AMAJOR, B.MAJOR AS BMAJOR
        INTO temp
        FROM ENROLLED A
        INNER JOIN ENROLLED B ON A.SID = B.SID
        WHERE A.MAJOR LIKE 'ABC%' AND NOT B.MAJOR LIKE 'ABC%' AND A.MAJOR < B.MAJOR AND A.TERM < B.TERM;
    """)

    cursor.execute("""
        SELECT BMAJOR, COUNT(BMAJOR) AS COUNT
        INTO temp2
        FROM temp
        GROUP BY BMAJOR 
        ORDER BY COUNT DESC;
    """)

    cursor.execute("""
        SELECT SUM(COUNT) AS TOTAL
        FROM temp2;
    """)
    total_transfer = cursor.fetchall()

    cursor.execute("""
        SELECT BMAJOR, COUNT
        FROM temp2
        GROUP BY BMAJOR, COUNT 
        ORDER BY COUNT DESC;
    """)
    join_data = cursor.fetchall()


    for i, val in enumerate(join_data) :
        if (i < 5) :
            print join_data[i][0], '{0:.3g}'.format(join_data[i][1] / total_transfer[0][0])

    cursor.execute("DROP TABLE temp, temp2")



partB()
partE()
partF()
partH()

#befh 