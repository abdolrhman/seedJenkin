import sqlite3
import os
from datetime import datetime
from jenkinsapi.jenkins import Jenkins
### define Jenkins parameters  #####
jenkins_url = 'http://localhost:8080'
username='abdo'
password='9518662951'

### Database details  #####
db_name = 'jenkins.db' ## sqlite database path
createTable = "CREATE TABLE jenkins(id int,job_name varchar(32), status char(12), date_checked date)"

# check db name already exist, delete file to not raze error each time the script is Run
if os.path.isfile(db_name):
    try:
        os.remove(db_name)
    except OSError:
        pass
	# raise SystemExit(0)


def create_connection(db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        db_connector = sqlite3.connect(db_name)
        return db_connector
    except Error as e:
        print(e)

    return None
def create_table(db_connector, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = db_connector.cursor()
        c.execute(createTable)
    except Error as e:
        print(e)

# create a database connection
db_connector =  create_connection(db_name)
### get server instance  #####
c = db_connector.cursor()
if db_connector is not None:
    # create jenkins table
    create_table(db_connector, createTable)
else:
    print("Error! cannot create the database connection.")

server = Jenkins(jenkins_url, username, password)
### create dictionary that holds the jobs name as keys and status as values ###
dict={}
def saveJobs():
	# @get_job :: to get all jobs
	for job_name, job_instance in server.get_jobs():
		# print (job_name);
		if job_instance.is_running():
			status = 'RUNNING'
		elif job_instance.get_last_build_or_none() == None :
			status = 'NONE'
		else:
			simple_job = server.get_job(job_instance.name)
			simple_build = simple_job.get_last_build()
			status = simple_build.get_status()

		i = datetime.now()
		checked_time = i.strftime('%Y/%m/%d %H:%M:%S')
		tupleData = (job_instance.name, status, checked_time)
		c.execute("SELECT id FROM jenkins WHERE job_name = ?", (job_instance.name,))
		data=c.fetchone()
		if data is None:
			c.execute('INSERT INTO jenkins (job_name, status, date_checked) VALUES (?,?,?)', tupleData)
		else:
			tuple2 = (status, checked_time, job_instance.name)
			c.execute('UPDATE jenkins SET status=?, date_checked=? WHERE job_name=?', tuple2)

		### Add to dictionary ###
		dict[job_instance.name] = status

	# Save (commit) the changes
	db_connector.commit()

	# We can close the connection
	db_connector.close()

if __name__ == '__main__':
	saveJobs();
