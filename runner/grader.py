# pip install MySQL-python for mysqld
import MySQLdb as sql

# connect with mysql db ebcode
# get the result from runner and write to database
result = {'submission_result_id': 'submission_result_id',
          'submission_id': 2,
          'problem_id': 6,
          'output': {
                    'input1': {
                    'input_id':'input_id1',
                    'output': 'output1',
                    'status':'pass'
                    },
                    'input2': {
                    'input_id':'input_id2',
                    'output': 'output2',
                    'status':'failed'
                    }
          },
          'failed_input': 2
          }
# DB connection class
class Database():
    def __init__(self):
        self.connect_db()

	#connect the program to SQL database
	#pass in the db information to connect
    def connect_db(self):
        self.db = sql.connect(host = "localhost",
							  user = "root",
							  passwd = "Hanoi123",
							  db = "ebcode")
        return self.db

    # write function: write to sub_result table, output column, failed_test_id column
    def write(self, result):
        sub_result_id = result['submission_result_id']
        failed_id = result['failed_input']
        sub_id = result['submission_id']
        query = """INSERT INTO ebcode.submission_results (submission_id, failed_test_id)
                   VALUES ({}, {});""".format(sub_id, failed_id)

        self.db.query(query)
        self.db.commit()

database = Database()
result = database.write(result)
