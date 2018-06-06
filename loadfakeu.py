#!/usr/bin/python3

import os
import sys
import psycopg2
import csv


def loadfakeu(directory):
	#REFERENCED FROM https://www.dataquest.io/blog/loading-data-into-postgres/
	connection = psycopg2.connect("dbname=fakeudata")
	cursor = connection.cursor()

	cursor.execute("""
		CREATE TABLE Course(
			CID INT,
			Term VARCHAR(10),
			Subj VARCHAR(5),
			Crse INT,
			Sec INT,
			Units VARCHAR(15),
			PRIMARY KEY(CID, Term))
	""")

	cursor.execute("""
		CREATE TABLE Meeting(
			CID INT,
			Term VARCHAR(10),
			Instructor VARCHAR(50),
			Type VARCHAR(30),
			Days VARCHAR(7),
			Time VARCHAR(30),
			Building VARCHAR(10),
			Room VARCHAR(5),
			PRIMARY KEY(CID, Term, Type))
	""")

	cursor.execute("""
		CREATE TABLE Student(
			SID INT,
			Surname VARCHAR(20),
			Prefname VARCHAR(20),
			Email VARCHAR(50),
			PRIMARY KEY(SID))
	""")

	cursor.execute("""
		CREATE TABLE Enrolled(
			CID INT,
			Term VARCHAR(10),
			SID INT,
			Seat INT,
			Level VARCHAR(5),
			Units DECIMAL(3,1),
			Class VARCHAR(2),
			Major VARCHAR(5),
			Grade VARCHAR(5),
			Status VARCHAR(2),
			PRIMARY KEY(CID, Term, SID))
	""")

	connection.commit()
	
	for csv_file in os.listdir(directory):
		if not csv_file.endswith(".csv"):
			continue

		with open(os.path.join(directory, csv_file), 'r') as file:
			reader = csv.reader(file)

			for line in reader:

				if line[0] == 'CID':
					line = next(reader)
					while len(line) != 1:
						#REFERENCED FROM https://stackoverflow.com/questions/4231491/how-to-insert-null-values-into-postgresql-database-using-python
						line = [None if x=='' else x for x in line]
						cid, term, subj, crse, sec, units = line
						cursor.execute("SELECT cid, term FROM Course;")
						temp = cursor.fetchall()
						t = ()
						t = t + (int(cid),) + (str(term),)
						if t in temp:
							term = str(term) + 'a'
							line[1] = term
						cursor.execute("""
							INSERT INTO Course VALUES (%s, %s, %s, %s, %s, %s)""",
							line
						)
						line = next(reader)

				elif line[0] == 'INSTRUCTOR(S)':
					line = next(reader)
					counter = 0
					while len(line) != 1:
						if counter != 0 and line[0] == "":
							line[0] = instructor
						line = [None if x == '' else x for x in line]
						if line[1] == None:
							line[1] = 'NULL'
						instructor, type, days, time, build, room = line
						line = [cid, term] + line
						
						#REFERENCED FROM http://www.postgresqltutorial.com/postgresql-upsert/
						cursor.execute("""
							INSERT INTO Meeting VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
							ON CONFLICT (CID, Term, Type) DO NOTHING
							""", line
						)
						line = next(reader)
						counter += 1

				elif line[0] == 'SEAT':
					try:
						line = next(reader)
					except StopIteration:
						cursor.execute("DELETE FROM Course WHERE CID=%s AND Term=%s", (cid, term))
						cursor.execute("DELETE FROM Meeting WHERE CID=%s AND Term=%s", (cid, term))
						break
					if len(line) == 1:
						cursor.execute("DELETE FROM Course WHERE CID=%s AND Term=%s", (cid, term))
						cursor.execute("DELETE FROM Meeting WHERE CID=%s AND Term=%s", (cid, term))
					else:
						while len(line) != 1:
							line = [None if x == '' else x for x in line]
							seat, sid, surname, prefname, level, units, clas, major, grade, status, email = line
							line = [cid, term, sid, seat, level, units, clas, major, grade, status]
							cursor.execute("""
								INSERT INTO Enrolled VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
								ON CONFLICT (cid, term, sid) DO NOTHING""",
								line
							)
							line = [sid, surname, prefname, email]
							cursor.execute(
								"INSERT INTO Student VALUES (%s, %s, %s, %s) ON CONFLICT (SID) DO NOTHING",
								line
							)
							try:
								line = next(reader)
							except StopIteration:
								break
		connection.commit()
	
	cursor.close()
	connection.close()
	print("Sucessfully loaded data.")


def main():
	if len(sys.argv) == 1:
		directory = os.getcwd()
	elif len(sys.argv) == 2:
		if os.path.isabs(sys.argv[1]):
			directory = sys.argv[1]
		else:
			directory = os.path.join(os.getcwd(), sys.argv[1])
	else:
		print("Too many arguments.")
		sys.exit()
	
	loadfakeu(directory)

if __name__ == "__main__":
	main()
