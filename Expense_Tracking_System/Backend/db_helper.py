import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger

logger = setup_logger("db_logger")
@contextmanager
def get_db_conn(commit=False):
    connection = mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='root',
        database='expense_manager'
    )

    ''' if connection.is_connected():
        print("Connection is established")
    else:
        print("Connection Failed")'''

    cursor = connection.cursor(dictionary=True)
    yield cursor

    if commit:
        connection.commit()
    cursor.close()
    connection.close()       

def fecth_data():
    logger.info("fetch_day_data called ")
    with get_db_conn() as cursor:
        cursor.execute('select * from expenses where expense_date')
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)

def fetch_day_data(expense_date):
    logger.info(f"fetch_day_data called with {expense_date}")
    with get_db_conn() as cursor:
        cursor.execute('select * from expenses where expense_date=%s',(expense_date,))
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)
    
    return expenses

def insert_expense(expense_date,amount,category,notes):
    logger.info(f"insert_expense called with {expense_date},{amount},{category},{notes}")
    with get_db_conn(commit=True) as cursor:
        cursor.execute(
            'Insert into expenses(expense_date,amount,category,notes) values (%s,%s,%s,%s)',(expense_date,amount,category,notes)
        )

def delete_expense(expense_date):
    logger.info(f"delete_expense called with {expense_date}")
    with get_db_conn(commit=True) as cursor:
        cursor.execute(
            'Delete from expenses where expense_date=%s',(expense_date,)
        )

def fetch_expense(expense_date_from,expense_date_to):
    logger.info(f"fetch_expense_summary called with start: {expense_date_from} end: {expense_date_to}")
    with get_db_conn() as cursor:
            cursor.execute(
            '''SELECT category, SUM(amount) as total 
               FROM expenses WHERE expense_date
               BETWEEN %s and %s  
               GROUP BY category;''',
            (expense_date_from, expense_date_to)
                    )
            data = cursor.fetchall()
        
    return data

def fetch_monthly_expense_summary():
    logger.info(f"fetch_expense_summary_by_months")
    with get_db_conn() as cursor:
        cursor.execute(
            '''SELECT month(expense_date) as expense_month, 
               monthname(expense_date) as month_name,
               sum(amount) as total FROM expenses
               GROUP BY expense_month, month_name;
            '''
        )
        data = cursor.fetchall()
        return data

if __name__=="__main__":
    #expense = fecth_day_data("2024_08_01")
    #print(expense)
    #insert_expense('2025-09-07',40,'Food','Bajji')
    #expense = fecth_day_data("2025-09-07")
    #print(expense)
    #delete_expense("2025-09-06")
    expense = fetch_expense('2024-08-01','2024-08-05')
    for record in expense:
        print(record)