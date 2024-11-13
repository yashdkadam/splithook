# import os

# # os.environ['BROKER_API_KEY'] = "1"


# # BROKER_API_SECRET = 
# 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMwNTU0OTc5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cDovLzEyNy4wLjAuMTo1MDAwL2Jyb2tlci9jYWxsYmFjayIsImRoYW5DbGllbnRJZCI6IjExMDQ0NjkyOTYifQ.9RalbE-7z3H0VVSonEfl7S7PEywm1uXvMWw9XNDaSmsrvwH465SnFqMnbGhwL6mWRZQghlc9X_3wxt4sqhwf2g'
# # BROKER_API_KEY = '1208340021952771'

# broker = ['fivepaisa', 'aliceblue', 'angel', 'dhan', 'fyers',
#           'icici', 'kotak', 'upstox', 'zebu', 'zerodha']

# def update_env_file(file_path, key, new_value):
#     # Read the .env file
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#         print(lines)

#     # Update the key-value pair
#     with open(file_path, 'w') as file:
#         for line in lines:
#             # If the line starts with the key, replace it with the new value
#             if line.startswith(f"{key} = "):
#                 file.write(f"{key} = {new_value}\n")
#             else:
#                 file.write(line)

# # Usage
# update_env_file('.env', 'BROKER_API_KEY', "'1208340021952771'")

# print(os.getenv('BROKER_API_KEY'))

# import os
# import subprocess
# import time

# def convert_to_mp4_gpu(file_path, output_path):
#     # Use h264_nvenc for GPU acceleration
#     # command = f"ffmpeg -i \"{file_path}\" -c:v h264_nvenc -c:a aac \"{output_path}\""
#     command = f"ffmpeg -i \"{file_path}\" -c:v copy -c:a copy \"{output_path}\""
#     subprocess.run(command, shell=True, check=True)

# def convert_videos_in_directory(directory):
#     total_start_time = time.time()  # Start time for total conversion process
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             file_path = os.path.join(root, file)
#             if not file.lower().endswith(".mp4"):
#                 output_file_path = os.path.splitext(file_path)[0] + ".mp4"
#                 try:
#                     print(f"Converting {file_path} to MP4 format using GPU...")
#                     start_time = time.time()  # Start time for individual file
#                     convert_to_mp4_gpu(file_path, output_file_path)
#                     end_time = time.time()  # End time for individual file
#                     time_taken = end_time - start_time
#                     print(f"Converted {file_path} to {output_file_path} in {time_taken:.2f} seconds")
#                     print("directory_path", directory_path)
#                     print("file_path", file_path)
#                     print(f"rm -rf {file_path}")
#                     os.system(f"rm -rf '{file_path}'")
#                 except Exception as e:
#                     print(f"Failed to convert {file_path}: {e}")
#     total_end_time = time.time()  # End time for total conversion process
#     total_time_taken = total_end_time - total_start_time
#     print(f"Total time taken to convert all files: {total_time_taken:.2f} seconds")

# # Set the directory path
# directory_path = "D:\courses\The Great Indian Kapil Show (2024) S01 (1080p NF WEBRip DDP 5.1 x265) [AnoZu]"
# convert_videos_in_directory(directory_path)

#########################################################

import psycopg2

# Database connection parameters
host = 'localhost'        # or your host
database = 'splithook'  # your database name
user = 'postgres'    # your username
password = 'qwerty' # your password

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    '''
    public | admin_orders    | table | postgres
    public | admin_stocks    | table | postgres
    public | admins          | table | postgres
    public | customer_orders | table | postgres
    public | customers       | table | postgres
    public | stocks          | table | postgres
    public | users           | table | postgres

            
    '''
    stringi = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMyMDI1ODk1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNDQ2OTI5NiJ9.Ai8sEVQXWIAi6T97MutDQCygoMekOreE59OgWDZzp6pkl79JJ-Hf6cv8mwO4wUl9NxThXyvE0aQX10sB1kagGQ'
    print(len(stringi))
    # SQL query to create a table 
    create_table_query = '''
        ALTER TABLE customer
ALTER COLUMN apisecret TYPE character varying(500);

    '''
    cursor.execute(create_table_query)

    # Commit the changes to the database
    conn.commit()
    print("Table created successfully")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the database connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
