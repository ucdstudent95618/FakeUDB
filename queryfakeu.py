#!/usr/bin/python3


import psycopg2


def prob_3a(cursor):
	print("----- Problem 3a -----")
	print("units, percent")
	for i in range(1, 21):
		cursor.execute("""
			SELECT COUNT(*) 
			FROM course FULL OUTER JOIN enrolled ON course.cid=enrolled.cid AND course.term=enrolled.term 
			WHERE subj IN ('ABC', 'DEF') AND enrolled.units=(%s)
			""", (i,))
		num_students = cursor.fetchone()[0]
		cursor.execute("""
			SELECT COUNT(*) FROM enrolled
			""")
		total = cursor.fetchone()[0]
		#REFERENCED FROM https://stackoverflow.com/questions/11719044/how-to-get-a-float-result-by-dividing-two-integer-values
		print(i, float(num_students) / float(total) * 100)


def prob_3b(cursor):
    print("\n----- Problem 3b -----")

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

    print("EASIEST PROFESSOR:", count_grade[0][2], "AVG GRADE =", avg[0][0])

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

    print("HARDEST PROFESSOR:", count_grade[0][2], "AVG GRADE =", avg[0][0])

    cursor.execute("DROP TABLE temp, temp2")


def prob_3c(cursor):
	print("\n----- Problem 3c -----")
	print("units, avg_gpa")
	cursor.execute("CREATE TABLE grade_point(Grade CHAR(2), Point DECIMAL(2,1));")
	cursor.execute("""
		INSERT INTO grade_point VALUES ('A+', 4.0), ('A', 4.0), ('A-', 3.7), ('B+', 3.3), ('B', 3.0), 
			('B-', 2.7), ('C+', 2.3), ('C', 2.0), ('C-', 1.7), ('D+', 1.3), ('D', 1.0), ('D-', .7), ('F', 0);
	""")	
	for i in range(1, 21):
		#REFERENCED FROM https://www.w3schools.com/sql/sql_view.asp
		cursor.execute("""
			CREATE VIEW threeC AS SELECT enrolled.sid, course.cid, grade 
			FROM course FULL OUTER JOIN enrolled ON course.cid=enrolled.cid AND course.term=enrolled.term 
			WHERE subj IN ('ABC', 'DEF') AND enrolled.units=(%s)
			""", (i,))
		cursor.execute("SELECT SUM(gp) FROM (SELECT *, point * 1 AS gp FROM threeC NATURAL JOIN grade_point) AS a;")
		sum = cursor.fetchone()[0]
		cursor.execute("SELECT COUNT(*) FROM threeC Natural JOIN grade_point;")
		total = cursor.fetchone()[0]
		if sum == None:
			gpa = 0
		else:
			gpa = float(sum) / float(total)
		print(i, gpa)
		cursor.execute("DROP VIEW threeC;")
		
	cursor.execute("DROP TABLE grade_point;")
	

def prob_3d(cursor):
	print("\n----- Problem 3d -----")
	cursor.execute("""
			CREATE VIEW threeD AS 
			SELECT subj, crse, CAST(n.num AS float)/ CAST(d.den AS float) AS pass_rate 
			FROM (SELECT subj, crse, COUNT(*) AS num 
				FROM course FULL OUTER JOIN enrolled on course.cid=enrolled.cid AND course.term=enrolled.term 
				WHERE grade NOT IN ('F', 'NP', 'NS', 'U', 'IP', 'I', 'Y') GROUP BY subj, crse) AS n NATURAL JOIN 
				(SELECT subj, crse, COUNT(*) AS den FROM course FULL OUTER JOIN enrolled on course.cid=enrolled.cid AND course.term=enrolled.term 
				WHERE grade NOT IN ('IP', 'I', 'Y') GROUP BY subj, crse) AS d;
			"""
	)
	cursor.execute("""
			SELECT * FROM threeD WHERE pass_rate IN (SELECT MAX(pass_rate) FROM threeD);
			"""
	)
	max_pass = cursor.fetchall()
	print("Courses with the highest pass rate:")
	print("subj, course, pass_rate")
	for i in range(len(max_pass)):
		subj, crse, pr = max_pass[i]
		print(subj, crse, pr)

	cursor.execute("""
			SELECT * FROM threeD WHERE pass_rate IN (SELECT MIN(pass_rate) FROM threeD);
			"""
	)
	min_pass = cursor.fetchall()
	print("\nCourses with the lowest pass rate:")
	print("subj, course, pass_rate")
	for i in range(len(min_pass)):
		subj, crse, pr = min_pass[i]
		print(subj, crse, pr)

	cursor.execute("""DROP VIEW threeD;""")


def prob_3e(cursor) :
    print("\n----- Problem 3e -----")
    # remove the summer quarter
    cursor.execute(""" 
        SELECT Course.CID AS CID, Instructor, Meeting.Term AS Term, Time, Subj,Crse
        INTO temp
        FROM Meeting
        INNER JOIN Course ON Course.CID = Meeting.CID AND Time != 'None'
        WHERE NOT CAST(Meeting.Term AS TEXT) LIKE '%06';
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
       print (join_data[i][0], join_data[i][1], join_data[i][2],join_data[i][3], join_data[i][4], join_data[i][5])
    
    cursor.execute("DROP TABLE temp, temp2")


def prob_3f(cursor) :
    print("\n----- Problem 3f -----")

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
    print ("BEST:")
    for i, row in enumerate(best_data) :
       print (best_data[i][0])
    print (" ")
    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '0.0';
    """)

    worst_data = cursor.fetchall()
    print ("WORST:")
    for i, row in enumerate(worst_data) :
       print (worst_data[i][0])

    cursor.execute("DROP TABLE temp, temp2, temp3, temp4")

    print (" ")

    print ("DEF: \n")

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
    print ("BEST:")
    for i, row in enumerate(best_data) :
       print (best_data[i][0])
    print (" ")
    cursor.execute("""
        SELECT * 
        FROM temp4
        WHERE GPA = '0.0';
    """)

    worst_data = cursor.fetchall()
    print ("WORST:")
    for i, row in enumerate(worst_data) :
       print (worst_data[i][0])

    cursor.execute("DROP TABLE temp, temp2, temp3, temp4, Chart")


def prob_3g(cursor):
	print("\n----- Problem 3g -----")
	cursor.execute("""
			CREATE VIEW threeG AS 
			SELECT T1.sid, T1.major AS major1, T2.major AS major2
			FROM enrolled AS T1, enrolled AS T2 
			WHERE T1.sid=T2.sid AND T1.term<T2.term AND T2.major LIKE 'ABC%' AND T1.major NOT LIKE 'ABC%';
			"""
	)
	cursor.execute("""
			SELECT COUNT(*) FROM threeG;
			"""
	)
	total = float(cursor.fetchone()[0])

	cursor.execute("""
			SELECT major1, CAST(COUNT(*) AS float)/ (%s) * 100 AS percent FROM threeG GROUP BY major1 ORDER BY percent DESC;
			""", (total,)
	)
	transfer = cursor.fetchall()
	print("major, percent")
	if len(transfer) >= 5:
		max = 5
	else:
		max = len(transfer)
	for i in range(max):
		major, percent = transfer[i]
		print(major, percent)
	cursor.execute("""DROP VIEW threeG;""")

def prob_3h(cursor) :
    print("\n----- Problem 3h -----")

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
            print (join_data[i][0], '{0:.3g}'.format(join_data[i][1] / total_transfer[0][0]))

    cursor.execute("DROP TABLE temp, temp2")


def main():
	connection = psycopg2.connect("dbname=fakeudata")
	cursor = connection.cursor()

	prob_3a(cursor)
	prob_3b(cursor)
	prob_3c(cursor)
	prob_3d(cursor)
	prob_3e(cursor)
	prob_3f(cursor)
	prob_3g(cursor)
	prob_3h(cursor)

	cursor.close()
	connection.close()


if __name__ == "__main__":
	main()
