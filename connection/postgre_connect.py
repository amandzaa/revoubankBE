import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection_to_postgres():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('DB_NAME')
    )

def create_new_table():
    get_connection = None
    current_cursor = None
    
    try:
        get_connection = get_connection_to_postgres()
        current_cursor = get_connection.cursor()
        
        current_cursor.execute("""
            CREATE TABLE daftar_t1 (
                tl_id SERIAL PRIMARY KEY,
                nama_tl VARCHAR(50) NOT NULL,
                lead_team INTEGER  -- Fixed the incorrect "IN"
            )
        """)
        
        get_connection.commit()
        print("Table created successfully!")
    
    except Exception as error:
        print(f"Ada error gaes: {error}")
    
    finally:
        if current_cursor:
            current_cursor.close()
        if get_connection:
            get_connection.close()
        print("Done")

# Call function to create table
create_new_table()
