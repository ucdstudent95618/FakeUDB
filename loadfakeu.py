import psycopg2
import csv
import os
import time 


def loadfakeu(*arg):
	if len(arg) == 0:
		directory = os.getcwd()
	else:
		directory = arg[0]

	connection = psycopg2.connect("dbname=fakeudata")
	cursor = connection.cursor()

	cursor.execute("""
		CREATE TABLE Course(
			CID INT,
			Term INT,
			Subj CHAR(5),
			Crse INT,
			Sec INT,
			Units VARCHAR(15),
			PRIMARY KEY(CID, Term)
		)
	""")

	cursor.execute("""
		CREATE TABLE Meeting(
			CID INT,
			Term INT,
			Instructor VARCHAR(50),
			Type VARCHAR(30),
			Days VARCHAR(7),
			Time VARCHAR(30),
			Building VARCHAR(10),
			Room VARCHAR(5),
			PRIMARY KEY(CID, Term, Instructor, Type, Days, Time)
		)
	""")

	cursor.execute("""
		CREATE TABLE Student(
			SID INT,
			Surname VARCHAR(20),
			Prefname VARCHAR(20),
			Email VARCHAR(50),
			PRIMARY KEY(SID)
		)
	""")

	cursor.execute("""
		CREATE TABLE Enrolled(
			CID INT,
			Term INT,
			SID INT,
			Seat INT,
			Level VARCHAR(5),
			Units VARCHAR(5),
			Class VARCHAR(2),
			Major VARCHAR(5),
			Grade VARCHAR(5),
			Status VARCHAR(2),
			PRIMARY KEY(CID, Term, SID)
		)
	""")

	connection.commit()
	
	for csv_file in os.listdir(directory):
		print(csv_file)
		with open(os.path.join(directory, csv_file), 'r') as file:
			reader = csv.reader(file)

			for line in reader:
				if line[0] == 'CID':
					line = next(reader)
					while len(line) != 1:
						line = ['NULL' if x=='' else x for x in line]
						cid, term, subj, crse, sec, units = line
						cursor.execute(
							"INSERT INTO Course VALUES (%s, %s, %s, %s, %s, %s)",
							line
						)
						line = next(reader)
				elif line[0] == 'INSTRUCTOR(S)':
					line = next(reader)
					counter = 0
					while len(line) != 1:
						if counter != 0:
							line[0] = instructor
						line = ['NULL' if x == '' else x for x in line]
						instructor, type, days, time, build, room = line
						line = [cid, term] + line
						cursor.execute(
							"""INSERT INTO Meeting VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
							ON CONFLICT (CID, Term, Instructor, Type, Days, Time) DO NOTHING
							""",
							line
						)
						line = next(reader)
						counter += 1
				elif line[0] == 'SEAT':
					try:
						line = next(reader)
					except StopIteration:
						cursor.execute("DELETE FROM Course WHERE CID=%s AND Term=%s", (cid, term))
						cursor.execute("DELETE FROM Meeting WHERE CID=%s AND Term=%s AND Type=%s", (cid, term, type))
						break
					if len(line) == 1:
						cursor.execute("DELETE FROM Course WHERE CID=%s AND Term=%s", (cid, term))
						cursor.execute("DELETE FROM Meeting WHERE CID=%s AND Term=%s AND Type=%s", (cid, term, type))
					else:
						while len(line) != 0 and len(line) != 1:
							line = ['NULL' if x == '' else x for x in line]
							seat, sid, surname, prefname, level, units, clas, major, grade, status, email = line
							line = [cid, term, sid, seat, level, units, clas, major, grade, status]
							cursor.execute(
								"INSERT INTO Enrolled VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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


def main():
	start_time = time.time()
	loadfakeu("/Users/miguel/Dropbox/cs/ecs165a/Homework4/Grades")
	print("Time %lf secs.\n" % (time.time() - start_time))


if __name__ == "__main__":
	main()
