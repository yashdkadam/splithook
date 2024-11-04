import psycopg2

# Database connection parameters
host = 'localhost'        # or your host
database = 'splithook'    # your database name
user = 'postgres'         # your username
password = 'qwerty'       # your password

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("Connection to the database was successful.")

    # SQL query to insert data into the admin_stocks table
    # insert_query = '''
    #     INSERT INTO admin_stocks (username, symbol) 
    #     VALUES ('john_doe', 'AAPL');
    # '''
    
    # cursor.execute(insert_query)
    # Commit the changes to the database
    # conn.commit()
    # print("Data inserted successfully.")

    # SQL query to select all records from the admin_stocks table
    select_query = '''
    SELECT * FROM customer_stock;
    '''
    
    cursor.execute(select_query)
    rows = cursor.fetchall()  # Fetch all results
    print("Data retrieved successfully.")

    # Print each row in the result
    for row in rows:
        print(row)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the database connection
    if cursor:
        cursor.close()
        print("Cursor closed.")
    if conn:
        conn.close()
        print("Connection closed.")
