# Load and check environment variables before anything else
from utils.env_check import load_and_check_env_variables  # Import the environment check function
load_and_check_env_variables()


from flask import Flask, render_template, request, jsonify
from extensions import socketio  # Import SocketIO
from limiter import limiter  # Import the Limiter instance
from cors import cors        # Import the CORS instance

from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.orders import orders_bp
from blueprints.search import search_bp
from blueprints.apikey import api_key_bp
from blueprints.log import log_bp
from blueprints.tv_json import tv_json_bp
from blueprints.brlogin import brlogin_bp
from blueprints.core import core_bp  

from restx_api import api_v1_bp

from database.auth_db import init_db as ensure_auth_tables_exists
from database.user_db import init_db as ensure_user_tables_exists
from database.symbol import init_db as ensure_master_contract_tables_exists
from database.apilog_db import init_db as ensure_api_log_tables_exists

from utils.plugin_loader import load_broker_auth_functions

from dotenv import load_dotenv
import os
# -------------------------------------
from myopenalgo.orders import api
from pprint import pprint   
import psycopg2
import random
import requests


def create_app():
    # Initialize Flask application
    app = Flask(__name__)

    # Initialize SocketIO
    socketio.init_app(app)  # Link SocketIO to the Flask app

    # Initialize Flask-Limiter with the app object
    limiter.init_app(app)

    # Initialize Flask-CORS with the app object
    cors.init_app(app)

    load_dotenv()

    # creds 
    host = 'localhost'        # or your host
    database = 'splithook'  # your database name
    user = 'postgres'    # your username
    password = 'qwerty' # your password

    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # Environment variables
    app.secret_key = os.getenv('APP_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Adjust the environment variable name as necessary

    # Initialize SQLAlchemy
 #   db.init_app(app)

    # Register the blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(api_key_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(tv_json_bp)
    app.register_blueprint(brlogin_bp)
    app.register_blueprint(core_bp)  

    # Register RESTx API blueprint
    app.register_blueprint(api_v1_bp)

    #########################
    # Function to increment the username in the pattern AAA000
    def increment_username(username):
        # Separate letters and digits
        letter_part = username[:3]
        number_part = int(username[3:])
        
        # Increment the numeric part
        number_part += 1
        if number_part > 999:  # If number exceeds 999, reset to 000 and increment letters
            number_part = 0
            # Convert letters to list for easier manipulation
            letters = list(letter_part)
            for i in range(2, -1, -1):  # Start from the last letter
                if letters[i] == 'Z':
                    letters[i] = 'A'
                else:
                    letters[i] = chr(ord(letters[i]) + 1)
                    break
            letter_part = ''.join(letters)
        
        # Format new username as AAA000
        return f"{letter_part}{number_part:03}"

    def place_order(data, customer_data):
        client = api(api_key='secret', host='http://127.0.0.1:5000')
        response = client.placeorder(
        strategy="Python",
        symbol=data['symbol'],
        action=data['action'],
        exchange=data['exchange'],
        price_type=data['type'],
        product="MIS",
        quantity=int(data['qty']),
        broker=customer_data['broker'],
        BROKER_API_SECRET=customer_data['BROKER_API_SECRET'],
        BROKER_API_KEY=customer_data['BROKER_API_KEY']
    )
        insert_query_customer_order = "insert into customer_order (username , orderid , tradingviewuniqueid , status , price, symbol) values (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query_customer_order, (data['username'], response['orderid'], data['key'], response['status'], response['price'], data['symbol']))

        return response
    
    def cancel_order(order_id, customer_data):
        client = api(api_key='secret', host='http://127.0.0.1:5000')
        response = client.cancelorder(
        order_id,
        broker=customer_data['broker'],
        BROKER_API_SECRET=customer_data['BROKER_API_SECRET'],
        BROKER_API_KEY=customer_data['BROKER_API_KEY']
    )
        return response

    @app.route('/read_webhook', methods=['POST'])
    def read_webhook():
        # step 1: read webhook
        # To get JSON data
        data = request.json
        customer_data = {
            "broker":"dhan",
            "BROKER_API_SECRET":'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMwNTU0OTc5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cDovLzEyNy4wLjAuMTo1MDAwL2Jyb2tlci9jYWxsYmFjayIsImRoYW5DbGllbnRJZCI6IjExMDQ0NjkyOTYifQ.9RalbE-7z3H0VVSonEfl7S7PEywm1uXvMWw9XNDaSmsrvwH465SnFqMnbGhwL6mWRZQghlc9X_3wxt4sqhwf2g',
            "BROKER_API_KEY":'1208340021952771'
        }
        print(data)

        # step 2: insert into admin_order table
        admin = 'adminuser'
        insert_query_admin_order = "insert into admin_order(tradingviewuniqueid , symbol , type , action , exchange , stoploss , profit) values (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query_admin_order, (data['key'], data['symbol'], data['type'], data['action'], data['exchange'], data['stoploss'], data['profit']))
        
        # step 3: get symbol
        symbol = data['symbol']

        # step 4: find all customers with this symbol
        select_query_for_customers_with_symbol = "select username from customer_stock where symbol = %s;"
        cursor.execute(select_query_for_customers_with_symbol, (symbol,))
        rows = cursor.fetchall()

        for row in rows:
            print(row)
            data['username'] = row[0]
            # step 5: fetch details for each customer
            select_query_for_customers_data = "select broker, apisecret, apikey from customer where username = %s;"
            cursor.execute(select_query_for_customers_data, (row[0],))
            api_data = cursor.fetchone()

            customer_data = {
                "broker": api_data[0],
                "BROKER_API_SECRET": api_data[1],
                "BROKER_API_KEY": api_data[0]
            }

            # step 6: place order for each customer
            order_data = place_order(data, customer_data)

            stoploss_orderid = ''
            #place stop loss
            if(data['stop_loss_percent'] and data['stop_loss_percent'] != ''):
                if(data['action'] == 'Buy'):
                    data['action'] = 'Sell'
                    data['price'] = (100 - data['stop_loss_percent'])*order_data['price']
                    stop_loss_order_data = place_order(data, customer_data)
                    stoploss_orderid = stoploss_orderid['orderid']

                if(data['action'] == 'Sell'):
                    data['action'] = 'Buy'
                    data['price'] = (100 + data['stop_loss_percent'])*order_data['price']
                    stop_loss_order_data = place_order(data, customer_data)
                    stoploss_orderid = stoploss_orderid['orderid']

            # if stop loss percent is empty cancel the stoploss order
            if(data['stop_loss_percent'] and data['stop_loss_percent'] == ''):
                if(data['action'] == 'Buy'):
                    query = "SELECT stoplossOrderId FROM customer_order WHERE action = %s AND symbol = %s ORDER BY timestamp DESC LIMIT 1; "
                    cursor.execute(query,('Sell',data['symbol']))
                    row = cursor.fetchone()
                    stoploss_orderid = row[0]
                    cancel_order(row[0], customer_data)

                if(data['action'] == 'Sell'):
                    query = "SELECT stoplossorderid FROM customer_order WHERE action = %s AND symbol = %s ORDER BY timestamp DESC LIMIT 1; "
                    cursor.execute(query,('Buy',data['symbol']))
                    row = cursor.fetchone()
                    stoploss_orderid = row[0]
                    cancel_order(row[0], customer_data)
            
            update_query_customer_order = "update customer_order set stoplossorderid = %s where username = %s and symbol = %s;"
            cursor.execute(update_query_customer_order, (stoploss_orderid, row[0], symbol, ))

        return jsonify({"message": "working"})
    
    @app.route('/login', methods=['GET'])
    def login():
        return render_template('sh_login.html')
    
    @app.route('/register', methods=['GET'])
    def register():
        return render_template('sh_register.html')
    
    # for customer
    @app.route('/customer/stocks', methods=['GET'])
    def stocks():
        return render_template('sh_cust_stock.html')
    
    @app.route('/customer/logs', methods=['GET'])
    def logs():
        return render_template('sh_cust_logs.html')
    
    # for admin
    @app.route('/admin/stocks', methods=['GET'])
    def admin_stocks():
        return render_template('sh_admin_stock.html')
    
    @app.route('/admin/logs', methods=['GET'])
    def admin_logs():
        return render_template('sh_admin_logs.html')
    
    @app.route('/admin/settings', methods=['GET'])
    def admin_settings():
        return render_template('sh_admin_settings.html')
    
    @app.route('/customer/status/<username>', methods=['GET'])
    def customer_status(username):
        customer_status_query = "select broker, apisecret, apikey from customer where username = %s;"
        cursor.execute(customer_status_query, (username,))
        res = cursor.fetchone()
        if(res[0] == None and res[1] == None and res[2] == None):
            return jsonify({"status": False})    
        return jsonify({"status": True})

    # for login verification
    @app.route('/verify', methods=['POST'])
    def verify_login():
        data = request.get_json()

        # Get 'username' and 'password' from the request data
        username = data.get('username')
        password = data.get('password')

        print(username, password)

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Prepare the SQL query to retrieve the password for the specified username
        select_query = '''
        SELECT password, type FROM users WHERE username = %s;
        '''
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()
        print(result)

        if result is None:
            return jsonify({"error": "User not found"}), 404

        # Fetch the stored password from the database
        stored_password, user_type = result[0], result[1]

        # Compare the provided password with the stored password
        if password == stored_password and user_type == 'admin':
            return jsonify({"status": "success", "redirect_url": "/admin/settings"}), 200
        if password == stored_password and user_type == 'customer':
            query = '''SELECT broker, apikey, apisecret FROM customer WHERE username = %s;'''
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            print(result)
            if(result[0] == None and result[1] == None and result[2] == None):
                return jsonify({"status": "success", "redirect_url": "/register"}), 200
            
            return jsonify({"status": "success", "redirect_url": "/customer/stocks"}), 200
        else:
            return jsonify({"status": "failed", "redirect_url": "/login"}), 401
    
    #for adding new user
    @app.route('/customer/add', methods=['POST'])
    def add_customer():
        data = request.get_json()
        name = data['name']
        email = data['email']
        mobilenumber = data['mobilenumber']
        user_type = 'customer'
        status = 'Enabled'
        password = str(random.randint(100000, 999999))

        cursor.execute("SELECT username FROM users where type='customer' ORDER BY username DESC LIMIT 1;")
        result = cursor.fetchone()
        last_username = result[0] if result else "AAA000"  # Start from 'AAA000' if no usernames exist

        # Calculate the next username
        print(last_username)
        next_username = increment_username(last_username)

        # Insert the new username into the database
        cursor.execute("INSERT INTO users (email, mobileNumber, username, name, password, type) VALUES (%s,%s,%s,%s,%s,%s);", (email, mobilenumber, next_username,name, password, user_type))
        cursor.execute("INSERT INTO customer (username, status) VALUES (%s, %s);", (next_username,status))
        
        conn.commit()

        ##TODO: send user email from support@arivax.com their username and password 

        return jsonify({"status": "success", "redirect_url": "/admin/settings"}), 200
   
    # for adding more about customer like broker, api_key and secret
    @app.route('/customer/register', methods=['POST'])
    def register_customer():
        data = request.get_json()
        broker = data['broker']
        apikey = data['api_key']
        apisecret = data['api_secret']
        username = data['username']
        
        cursor.execute("update customer set broker = %s, apikey = %s, apisecret = %s where username = %s;", (broker, apikey, apisecret, username))
        
        conn.commit()

        return jsonify({"status": "success", "redirect_url": "/customer/stocks"}), 200
    
    # for getting customer trade logs
    @app.route('/customer/logs/get/<username>', methods=['GET'])
    def get_customer_trades(username):
        cursor.execute("SELECT * FROM customer_order where username = %s;", (username,))
        result = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Convert the result into a list of dictionaries
        customers = [dict(zip(columns, row)) for row in result]

        return jsonify(customers)
    
    # for getting admin webhook logs
    @app.route('/admin/logs/get', methods=['GET'])
    def get_admin_trades():
        cursor.execute("SELECT * FROM admin_order")
        result = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Convert the result into a list of dictionaries
        customers = [dict(zip(columns, row)) for row in result]

        return jsonify(customers)
    
    # for getting admin webhook logs
    @app.route('/admin/orders/get', methods=['GET'])
    def get_admin_orders():
        cursor.execute("SELECT symbol FROM admin_order;")
        result = cursor.fetchall()
        
        # Convert the result into a list of dictionaries
        customers = [dict(zip(row)) for row in result]

        return jsonify(result)
    
    # for getting admin stocks
    @app.route('/admin/stocks/get', methods=['GET'])
    def get_admin_stocks():
        cursor.execute("SELECT symbol FROM admin_stock;")
        result = cursor.fetchall()
        res = []
        for i in result:
            res.append(i[0])
        # Convert the result into a list of dictionaries
        # customers = [dict(zip(row)) for row in result]

        return jsonify(res)
    
    # for getting customer stocks
    @app.route('/customer/stocks/get/<username>', methods=['GET'])
    def get_customer_stocks(username):
        cursor.execute("SELECT * FROM customer_stock where username = %s;",(username,))
        result = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert the result into a list of dictionaries
        customers = [dict(zip(columns, row)) for row in result]

        return jsonify(customers)
    
    # for deleting admin stocks
    @app.route('/admin/stocks/delete/<stock>', methods=['DELETE'])
    def delete_admin_stock(stock):
        cursor.execute("delete from admin_stock where symbol = %s;",(stock,))
        
        return jsonify({"status": "deleted successfully"})
    
    # for deleting customer stocks
    @app.route('/customer/stocks/delete', methods=['DELETE'])
    def customer_admin_stock():
        data = request.get_json()
        username = data['username']
        symbol = data['symbol']
        cursor.execute("delete from customer_stock where symbol = %s and username = %s;",(symbol, username))
        conn.commit()
        return jsonify({"status": "deleted successfully"})
    
    #for getting all customers
    @app.route('/customer/get', methods=['GET'])
    def get_all_customers():
        cursor.execute("SELECT c.*, u.* FROM customer c JOIN users u ON c.username = u.username ORDER BY c.status DESC;")
        result = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Convert the result into a list of dictionaries
        customers = [dict(zip(columns, row)) for row in result]

        return jsonify(customers)

    @app.route('/customer/enable/<username>', methods=['GET', 'POST'])
    def enable_customer(username):
        username = str(username)
        cursor.execute("UPDATE customer SET status='Enabled' WHERE username = %s;", (username,))
        conn.commit()
        return jsonify({"status":"success"})
    
    @app.route('/customer/disable/<username>', methods=['GET', 'POST'])
    def disable_customers(username):
        print(type(username))
        username = str(username)
        cursor.execute("UPDATE customer SET status='Disabled' WHERE username = %s;", (username,))

        conn.commit()
        return jsonify({"status":"success"})
    
    # for fetching stock symbols
    @app.route('/stocks/<query>', methods=['GET'])
    def fetch_stock_list(query):
        # NSE search endpoint (Unofficial API)
        url = "https://www.nseindia.com/api/search/autocomplete"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        params = {"q": query}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return [
                {"symbol": item["symbol"], "name": item["symbol_info"]}
                for item in data.get("symbols", [])
            ]
        else:
            print("Failed to fetch data from NSE:", response.status_code)
            return []

    # for adding stock to admin_stock
    @app.route('/stocks/add/<stock>', methods=['GET'])
    def add_admin_stock(stock):
        stock = str(stock)
        cursor.execute("SELECT COUNT(*) FROM admin_stock WHERE symbol = (%s);", (stock,))
        stock_exists = cursor.fetchone()[0]
        print(stock_exists)
        if(stock_exists == 0):
            cursor.execute("insert into admin_stock(symbol) values (%s);", (stock,))
        conn.commit()
        return jsonify({"status":"success"})

    # for adding stock to customer_stock
    @app.route('/customer/stocks/add/', methods=['POST'])
    def add_customer_stock():
        data = request.get_json()

        username = data['username']
        symbol = data['symbol']
        quantity = data['quantity']
        
        # Check if the username exists in the table
        cursor.execute("SELECT COUNT(*) FROM customer_stock WHERE username = %s and symbol = %s;", (username, symbol))
        user_exists = cursor.fetchone()[0]

        if user_exists == 0:
            # Insert new record if username does not exist
            cursor.execute(
                "INSERT INTO customer_stock(username, symbol, quantity) VALUES (%s, %s, %s);",
                (username, symbol, quantity)
            )
            print("User added to the table.")
        else:
            # If user exists, pass or perform any other desired action
            print("User already exists, skipping insertion.")        
        conn.commit()
        return jsonify({"status":"success"})
    
    # for updating stock to customer_stock
    @app.route('/customer/stocks/update/', methods=['POST'])
    def update_customer_stock():
        data = request.get_json()

        username = data['username']
        symbol = data['symbol']
        quantity = data['quantity']

        cursor.execute("update customer_stock set quantity = %s where username = %s and symbol = %s;", (quantity,username,symbol))
        conn.commit()
        return jsonify({"status":"success"})


    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.context_processor
    def inject_version():
        return dict(version=os.getenv('FLASK_APP_VERSION'))

    return app


def setup_environment(app):
    with app.app_context():

        #load broker plugins
        app.broker_auth_functions = load_broker_auth_functions()
        # Ensure all the tables exist
        ensure_auth_tables_exists()
        ensure_user_tables_exists()
        ensure_master_contract_tables_exists()
        ensure_api_log_tables_exists()

    # Conditionally setup ngrok in development environment
    if os.getenv('NGROK_ALLOW') == 'TRUE':
        from pyngrok import ngrok
        public_url = ngrok.connect(name='flask').public_url  # Assuming Flask runs on the default port 5000
        print(" * ngrok URL: " + public_url + " *")


app = create_app()

# Explicitly call the setup environment function
setup_environment(app)

# Start Flask development server with SocketIO support if directly executed
if __name__ == '__main__':
    # Get environment variables
    host_ip = os.getenv('FLASK_HOST_IP', '127.0.0.1')  # Default to '127.0.0.1' if not set
    port = int(os.getenv('FLASK_PORT', 5000))  # Default to 5000 if not set
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')  # Default to False if not set

    socketio.run(app, host=host_ip, port=port, debug=debug)