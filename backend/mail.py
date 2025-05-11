from signup import get_cursor, conn, initialize_connection  # Import necessary functions and variables
from datetime import datetime
import sqlite3 as sql

def add_mail(email, created_by=None):
    global conn
    try:
        # Ensure the connection is initialized
        if conn is None:
            conn = initialize_connection()
        
        # Get a cursor
        cursor = get_cursor()
        
        # Check if the email already exists
        check_query = "SELECT * FROM mail_lists WHERE email = ?"
        cursor.execute(check_query, (email,))
        result = cursor.fetchone()
        
        if result:
            # If email exists, update the deleted_at field to NULL
            update_query = """
            UPDATE mail_lists
            SET deleted_at = NULL, updated_at = ?, created_by = ?
            WHERE email = ?
            """
            cursor.execute(update_query, (datetime.now(), created_by, email))
            print("Mail updated (undeleted)")
        else:
            # If email does not exist, insert a new record
            insert_query = """
            INSERT INTO mail_lists (email, created_at, updated_at, created_by)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (email, datetime.now(), datetime.now(), created_by))
            print("Mail added")
        
        # Commit changes
        conn.commit()
        return True

    except sql.Error as err:
        print(f"Error: {err}")
        return None





def delete_mail(email, deleted_by=None):
    global conn
    try:
        # Ensure the connection is initialized
        if conn is None:
            conn = initialize_connection()
        
        # Get a cursor
        cursor = get_cursor()
        
        # Prepare the SQL query
        query = """
        UPDATE mail_lists
        SET deleted_at = ?, deleted_by = ?
        WHERE email = ?
        """
        
        # Execute the query with parameters
        cursor.execute(query, (datetime.now(), deleted_by, email))
        
        # Commit changes
        conn.commit()
        print("Soft delete executed and committed successfully")
        return True

    except sql.Error as err:
        print(f"Error: {err}")
        return None



def get_all_mail_ids():
    global conn
    try:
        # Ensure the connection is initialized
        if conn is None:
            conn = initialize_connection()
        
        # Get a cursor
        cursor = get_cursor()
        
        # Prepare the SQL query
        query = """
        SELECT email, DATE(created_at) AS created_date
        FROM mail_lists
        WHERE deleted_at IS NULL
        """
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results
        rows = cursor.fetchall()
        
        # Print or return results
        for row in rows:
            print(f"Email: {row[0]}, Created Date: {row[1]}")
        
        return rows

    except sql.Error as err:
        print(f"Error: {err}")
        return None



