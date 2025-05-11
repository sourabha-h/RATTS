import sqlite3 as sql
# from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from passlib.context import CryptContext
import pandas as pd
from fastapi import FastAPI, HTTPException
import ast
import json


# SECRET_KEY = "test"
# serializer = URLSafeTimedSerializer(SECRET_KEY)
# verify_link = "http://127.0.0.1:8000"

conn = None

def initialize_connection():
    global conn

    try:
        conn = sql.connect("C:/xampp/htdocs/RATTS/testing")
        return conn
    except sql.Error as err:
        print("Error:", err)
        return None

# def get_cursor(dictionary = False):
#     global conn
#     if conn is None:
#         conn = initialize_connection()
#         print('New connection created' if conn else 'Failed to create new connection')
#     else:
#         print('Existing connection used')
#     if dictionary:
#         cursor = conn.cursor(dictionary=True)
#     else:
#         cursor = conn.cursor()
#     return cursor
def get_cursor(dictionary=False):
    global conn
    if conn is None:
        conn = initialize_connection()
        print('New connection created' if conn else 'Failed to create new connection')
    else:
        print('Existing connection used')

    if dictionary:
        conn.row_factory = sql.Row  # This allows dictionary-like access to rows
    else:
        conn.row_factory = None  # Reset to default row factory if dictionary=False

    cursor = conn.cursor()
    return cursor




def hash_password(password):
    crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = crypt_context.hash(password)
    return hashed_password
    
def is_bcrypt_hash(hashed_str):
    # The length of bcrypt hashed string is 60 characters
    if len(hashed_str) != 60:
        return False
    else:
        return True

def admin_func(admin):
    global conn
    if conn is None:
        conn = initialize_connection()
    cur = conn.cursor()

    if admin.function == "UserAvailability":
        sql_get = """SELECT count(*) FROM users WHERE name = ?"""
        data = (admin.user_name,)
        try:
            cur.execute(sql_get, data)
            count = cur.fetchone()[0]
            return count
        except Exception as e:
            return ("Error Fetching record:", e)

    if admin.function == "Users":
        sql_get = """SELECT id, name, email, password, address, country,
           phone_number, device_type, device_address, user_group, user_role,
           verified_at, display_name, active_status
        FROM users;"""
        try:
            cur.execute(sql_get)
            res = cur.fetchall()
            user_data = pd.DataFrame(res, columns=["id", "user_name", "user_email", "user_password",
                                                   "user_address", "user_country", "user_phone", "device_type",
                                                   "device_address", "user_group", "user_role", "user_verified",
                                                   "user_display_name", "active_status"])
            user_json = user_data.to_json(orient='records')
            return user_json
        except Exception as e:
            return ("Error Fetching record:", e)

    if admin.function == "Get":
        sql_get = """SELECT id, name, email, password, address, country,
           phone_number, device_type, device_address, user_group, user_role,
           verified_at, display_name 
        FROM users WHERE active_status = 1 and name = ?"""
        data = (admin.user_name,)
        try:
            cur.execute(sql_get, data)
            res = cur.fetchall()
            user_data = pd.DataFrame([list(res[0])], columns=["id", "user_name", "user_email", "user_password",
                                                              "user_address", "user_country", "user_phone", "device_type",
                                                              "device_address", "user_group", "user_role", "user_verified",
                                                              "user_display_name"])
            user_json = user_data.to_json(orient='records')
            return user_json
        except Exception as e:
            return ("Error Fetching record:", e)

    if admin.function == "Add":
        hashedPassword = hash_password(admin.user_password)

        sql_add = """INSERT INTO users (name, email, password, address, country, phone_number, device_type, device_address, user_group, user_role, verified_at, display_name) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        data = (admin.user_name, admin.user_email, hashedPassword, admin.user_address, admin.user_country,
                admin.user_phone, admin.device_type, admin.device_address, admin.user_group, admin.user_role,
                admin.user_verified, admin.user_display_name)
        try:
            cur.execute(sql_add, data)
            conn.commit()
            # send_verification_mail(admin.user_name, admin.user_email)
            return ("User '" + admin.user_name + "' created successfully.")
        except Exception as e:
            conn.rollback()  # Rollback changes if an error occurs
            return ("Error adding record:", e)

    if admin.function == "Edit":
        if not is_bcrypt_hash(admin.user_password):
            admin.user_password = hash_password(admin.user_password)

        sql_edit = """UPDATE users SET email=?, password=?, address=?, country=?, phone_number=?, device_type=?, device_address=?, user_group=?, user_role=?, display_name=?  
        WHERE name=?"""
        data = (admin.user_email, admin.user_password, admin.user_address, admin.user_country, admin.user_phone,
                admin.device_type, admin.device_address, admin.user_group, admin.user_role, admin.user_display_name,
                admin.user_name)
        try:
            cur.execute(sql_edit, data)
            conn.commit()
            return ("User '" + admin.user_name + "' edited successfully.")
        except Exception as e:
            conn.rollback()  # Rollback changes if an error occurs
            return ("Error editing record:", e)

    if admin.function == "Drop":
        sql_drop = """UPDATE users SET active_status = 0 WHERE name = ?"""
        data = (admin.user_name,)
        try:
            cur.execute(sql_drop, data)
            conn.commit()
            return ("User '" + admin.user_name + "' deleted successfully.")
        except Exception as e:
            conn.rollback()  # Rollback changes if an error occurs
            return ("Error deleting record:", e)


def get_user_id_role_by_username(user_name):
    try:
        # Connect to the SQLite database
        cursor = get_cursor()

        # Use placeholders in the SQL query to avoid SQL injection
        sql_query = "SELECT id, user_role, user_group, display_name FROM users WHERE name = ? OR email = ?;"
        cursor.execute(sql_query, (user_name, user_name))
        userdetails = cursor.fetchone()

        return userdetails

    except sql.Error as err:
        print(f"Error: {err}")
        return None


def login_user_details(login_username):
    try:
        cursor = get_cursor()
        
        # Use placeholders in the SQL query to avoid SQL injection
        sql_query = "SELECT * FROM users WHERE name = ? OR email = ?;"
        cursor.execute(sql_query, (login_username, login_username))
        userdetails = cursor.fetchone()
        
        return userdetails
    except sql.Error as err:
        print(f"Error: {err}")
        return None
    

# def display_permissions():
#     try:
#         cursor = get_cursor()

#         query = "SELECT id, permission_name FROM permissions"
        
#         cursor.execute(query)
#         result = cursor.fetchall()

#         # Convert sqlite3.Row to a list of dictionaries
#         result = [dict(row) for row in result]

#         return result
#     except sql.Error as err:
#         print(f"Error: {err}")
#         raise HTTPException(status_code=500, detail="Failed to fetch permissions")

def display_permissions():
    try:
        cursor = get_cursor(dictionary=True)

        query = "SELECT id, permission_name FROM permissions"
        
        cursor.execute(query)
        result = cursor.fetchall()

        # Result is already a list of Row objects, which can be treated like dictionaries
        return result  # Directly return the result

    except sql.Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to fetch permissions")

    
def insert_role_permissions(role_id, permission_ids):
    try:
        cursor = get_cursor()

        # Prepare the insert query (SQLite uses '?' placeholders instead of '%s')
        insert_query = '''
            INSERT INTO roles (id, permissions, created_at)
            VALUES (?, ?, ?)
        '''
        
        # Use current timestamp for 'created_at'
        created_at = datetime.now()

        # Execute the query, passing the role_id, permission_ids, and created_at
        cursor.execute(insert_query, (role_id, permission_ids, created_at))

        # Commit the transaction
        conn.commit()

        return True

    except sql.Error as err:
        print(f"Error: {err}")
        return None

def insert_permissions(permission_list: list):
    try:
        cursor = get_cursor()

        check_query = 'SELECT COUNT(*) FROM permissions WHERE permission_name = ?'
        insert_query = 'INSERT INTO permissions (permission_name) VALUES (?)'

        for permission in permission_list:
            # Check if the permission already exists
            cursor.execute(check_query, (permission,))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the permission if it doesn't exist
                cursor.execute(insert_query, (permission,))
        
        # Commit the transaction
        conn.commit()

    except sql.Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to insert permissions")
    
def insert_or_update_role_permissions(role_id: int, permission_ids: list):
    try:
        cursor = get_cursor()

        # Convert permission_ids list to a JSON string
        permissions_json = json.dumps(permission_ids)

        # Check if the role exists
        check_query = '''
        SELECT COUNT(*) FROM role_permission_assignments WHERE role_id = ?
        '''
        cursor.execute(check_query, (role_id,))
        role_exists = cursor.fetchone()[0] > 0

        if role_exists:
            # If the role exists, update the permissions
            update_query = '''
            UPDATE role_permission_assignments 
            SET permissions = ?, updated_at = ?
            WHERE role_id = ?
            '''
            cursor.execute(update_query, (permissions_json, datetime.now(), role_id))
        else:
            # If the role does not exist, insert a new record
            insert_query = '''
            INSERT INTO role_permission_assignments (role_id, permissions, created_at)
            VALUES (?, ?, ?)
            '''
            cursor.execute(insert_query, (role_id, permissions_json, datetime.now()))

        # Commit the transaction
        conn.commit()

        return "Permissions Updated Successfully"

    except sql.Error as err:
        print(f"Error: {err}")
        return None

# def display_permissions_by_role(role_id):
#     try:
#         cursor = get_cursor(dictionary=True)

#         # Fetch permissions for the role
#         query = "SELECT id, permissions FROM role_permission_assignments WHERE role_id = ?"
#         cursor.execute(query, (role_id,))
#         result = cursor.fetchall()
#         print(result)
#         if not result:
#             return {"details": [], "permission_names": []}

#         # Extract and evaluate the permissions string
#         permissions_str = result[0]['permissions']
#         permissions_list = ast.literal_eval(permissions_str)
#         print("Permissions list:", permissions_list)

#         if not permissions_list:
#             return {"details": [], "permission_names": []}

#         # Convert permission IDs to a tuple and format them for the IN clause
#         per_ids = tuple(permissions_list)
#         print("Formatted permission IDs:", per_ids)

#         # Fetch details for the permissions using parameterized query
#         query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(','.join('?' for _ in per_ids))
#         print("Query:", query)
#         cursor.execute(query, per_ids)
#         permissions_result = cursor.fetchall()

#         # Create a list of permission names
#         permission_names = [perm['permission_name'] for perm in permissions_result]
#         print("Permission Names:", permission_names)

#         return {"details": permissions_result, "permission_names": permission_names}

#     except sql.Error as err:
#         print(f"Error: {err}")
#         return {"details": [], "permission_names": []}

def display_permissions_by_role(role_id):
    try:
        cursor = get_cursor(dictionary=True)

        # Fetch permissions for the role
        query = "SELECT id, permissions FROM role_permission_assignments WHERE role_id = ?"
        cursor.execute(query, (role_id,))
        result = cursor.fetchall()
        print(result)
        if not result:
            return {"details": [], "permission_names": []}

        # Extract and evaluate the permissions string
        permissions_str = result[0]['permissions']
        print(permissions_str)
        if not permissions_str:
            print("yes")
            return {"details": [], "permission_names": []}

        permissions_list = ast.literal_eval(permissions_str)
        print(permissions_list)
        if not permissions_list:
            return {"details": [], "permission_names": []}

        # Convert permission IDs to a tuple and format them for the IN clause
        per_ids = tuple(permissions_list)
        
        # Fetch details for the permissions using parameterized query
        query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(','.join('?' for _ in per_ids))
        cursor.execute(query, per_ids)
        permissions_result = cursor.fetchall()

        if not permissions_result:
            return {"details": [], "permission_names": []}

        # Create a list of permission names
        permission_names = [perm['permission_name'] for perm in permissions_result]

        return {"details": permissions_result, "permission_names": permission_names}

    except sql.Error as err:
        print(f"Error: {err}")
        return {"details": [], "permission_names": []}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"details": [], "permission_names": []}
    

def create_role(role_name):
    try:
        # Get the database cursor
        cursor = get_cursor()

        # Check if the role already exists (case-insensitive check)
        check_query = '''
        SELECT COUNT(*) FROM roles WHERE LOWER(name) = LOWER(?)
        '''
        cursor.execute(check_query, (role_name,))
        role_count = cursor.fetchone()[0]

        if role_count > 0:
            return {"status": "error", "message": f"Role '{role_name}' already exists (case-insensitive)"}

        # Prepare the insert query
        insert_query = '''
        INSERT INTO roles (name, created_at)
        VALUES (?, ?)
        '''
        # Use current timestamp for the created_at field
        created_at = datetime.now()

        # Execute the insert query
        cursor.execute(insert_query, (role_name, created_at))

        # Commit the transaction
        conn.commit()

        return {"status": "success", "message": f"Role '{role_name}' created successfully"}

    except sql.Error as err:
        print(f"Error: {err}")
        return {"status": "error", "message": "Failed to create role"}


    


def fetch_roles():
    try:
        # Get the database cursor
        cursor = get_cursor(dictionary=True)

        # Prepare the query to fetch all roles
        fetch_query = '''
        SELECT id, name FROM roles
        '''

        # Execute the query
        cursor.execute(fetch_query)

        # Fetch all results
        roles = cursor.fetchall()

        if not roles:
            return {"roles": []}

        # Return the list of roles with their IDs
        return {"roles": roles}

    except sql.Error as err:
        print(f"Error: {err}")
        return {"roles": []}
    
def get_authenticate_user(login_username):
    try:
        cursor = get_cursor()

        # Use placeholders in the SQL query to avoid SQL injection
        sql_query = "SELECT * FROM users WHERE name = ?;"

        cursor.execute(sql_query, (login_username,))
        userdetails = cursor.fetchone()  # Fetch one record
        # print(dict(userdetails))  # If using row_factory, you can convert to dict
        conn.commit()

        return userdetails

    except sql.Error as err:
        print(f"Error: {err}")
        return None




