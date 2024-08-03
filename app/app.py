from flask import Flask, render_template
from sqlalchemy import text
import time 

app = Flask(__name__)

# Assuming `engine` is properly defined in your `db` module
from db import engine

@app.route('/')
def index():
    with engine.connect() as conn:
        # fetch data from sql_task_a_result
        sql_task_a_result = conn.execute(text('SELECT * FROM sql_task_a_result;')).fetchall()
        sql_task_b_result = conn.execute(text('SELECT * FROM sql_task_b_result;')).fetchall()
        http_log_analyze_task_result = conn.execute(text('SELECT * FROM http_log_analyze_task_result;')).fetchall()
    
    return render_template('index.html',
                           sql_task_a_result=sql_task_a_result,
                           sql_task_b_result=sql_task_b_result,
                           http_log_analyze_task_result=http_log_analyze_task_result)

if __name__ == '__main__':
    time.sleep(100)
    app.run(host='0.0.0.0', port=5000)
