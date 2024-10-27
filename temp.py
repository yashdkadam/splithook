import os

# os.environ['BROKER_API_KEY'] = "1"


# BROKER_API_SECRET = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMwNTU0OTc5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cDovLzEyNy4wLjAuMTo1MDAwL2Jyb2tlci9jYWxsYmFjayIsImRoYW5DbGllbnRJZCI6IjExMDQ0NjkyOTYifQ.9RalbE-7z3H0VVSonEfl7S7PEywm1uXvMWw9XNDaSmsrvwH465SnFqMnbGhwL6mWRZQghlc9X_3wxt4sqhwf2g'
# BROKER_API_KEY = '1208340021952771'

broker = ['fivepaisa', 'aliceblue', 'angel', 'dhan', 'fyers',
          'icici', 'kotak', 'upstox', 'zebu', 'zerodha']

def update_env_file(file_path, key, new_value):
    # Read the .env file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        print(lines)

    # Update the key-value pair
    with open(file_path, 'w') as file:
        for line in lines:
            # If the line starts with the key, replace it with the new value
            if line.startswith(f"{key} = "):
                file.write(f"{key} = {new_value}\n")
            else:
                file.write(line)

# Usage
update_env_file('.env', 'BROKER_API_KEY', "'1208340021952771'")

print(os.getenv('BROKER_API_KEY'))