import sqlite3 as sql
# from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from passlib.context import CryptContext
import pandas as pd
from fastapi import FastAPI, HTTPException
import ast
import json
from typing import List
import logging
import schedule
import glob
import os
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import calendar
from Tests.oepsoap_testsuite import *
#from Tests.test_process import *
from Tests.generate_csv import *
from Tests.soap_testsuite import *
#from Tests.oepsoap_testsuite import *
from Tests.gui_testsuite import *
from Tests.opcode_testsuite import *
# SECRET_KEY = "test"
# serializer = URLSafeTimedSerializer(SECRET_KEY)
# verify_link = "http://127.0.0.1:8000"

conn = None

def initialize_connection():
    global conn

    try:
         # Get the path four levels up from the current file
        path_four_levels_up = os.path.join(os.path.dirname(__file__))
        print(f"path_four_levels_up: {path_four_levels_up}")
        # Convert to an absolute path
        absolute_path = os.path.abspath(path_four_levels_up)
        db_path = os.path.join(absolute_path,'..','testing')
            
        print(f"The absolute_path is: {absolute_path}")
        print(f"The resource_path is: {db_path}")
        
        
        # Replace backslashes with double backslashes
        modified_db_path = db_path.replace('\\', '\\\\')
        
        # Print the modified path
        print(f"The new library path is: {modified_db_path}")
        
        conn = sql.connect(modified_db_path, check_same_thread=False)
        #conn=sql.connect('C:\\Users\\Rajeswari\\Downloads\\testing', check_same_thread=False)
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
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use

    if admin.function == "Users":
        sql_get_users = """SELECT id, name, email, password, address, country,
           phone_number, device_type, device_address, user_group, user_role,
           verified_at, display_name, active_status
        FROM users;"""
        try:
            cur.execute(sql_get_users)
            users = cur.fetchall()

            # Fetch all roles for mapping
            sql_get_roles = """SELECT id, name FROM roles;"""
            cur.execute(sql_get_roles)
            roles = cur.fetchall()
            role_map = {str(role[0]): role[1] for role in roles}

            # Process user data
            processed_users = []
            for user in users:
                user_group_ids = user[10].split(",") if user[10] else []  # user_group is at index 9
                user_group_json = [
                                    {"id": int(role_id), "name": role_map.get(role_id, "Unknown")}
                                    for role_id in user_group_ids
                                ]

                # Replace user_group with ID:Name pairs
                processed_user = list(user)
                processed_user[10] = user_group_json  # Update user_group field
                processed_users.append(processed_user)

            # Convert processed user data to JSON
            user_data = pd.DataFrame(
                processed_users,
                columns=[
                    "id", "user_name", "user_email", "user_password", "user_address", 
                    "user_country", "user_phone", "device_type", "device_address",
                    "user_group", "user_role", "user_verified", "user_display_name", 
                    "active_status"
                ]
            )
            user_json = user_data.to_json(orient='records')
            return user_json
        except Exception as e:
            return ("Error Fetching record:", str(e))
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use

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
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use

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
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use

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
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use

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
        finally:
            if cur:
                cur.close()  # Ensure the cursor is closed after use



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

# def display_permissions():
#     try:
#         cursor = get_cursor(dictionary=True)

#         query = "SELECT id, permission_name FROM permissions"
        
#         cursor.execute(query)
#         result = cursor.fetchall()

#         # Result is already a list of Row objects, which can be treated like dictionaries
#         return result  # Directly return the result

#     except sql.Error as err:
#         print(f"Error: {err}")
#         raise HTTPException(status_code=500, detail="Failed to fetch permissions")

def display_permissions():
    try:
        # Initialize the cursor with dictionary format
        cursor = get_cursor(dictionary=True)
        
        # Fetch permissions from the database
        query = "SELECT id, permission_name FROM permissions"
        cursor.execute(query)
        permissions_result = cursor.fetchall()  # Fetch all rows as dictionaries
        
        if not permissions_result:
            return {"details": [], "permission_names": []}  # Return empty if no permissions found
        
        # Convert permissions_result rows to mutable dictionaries
        permissions_result = [dict(row) for row in permissions_result]
        
        # Load the JSON mapping file
        with open("permission_mapping.json", "r") as json_file:
            permission_map = json.load(json_file)  # JSON with mappings
        
        # Replace permission names based on JSON mapping
        for perm in permissions_result:
            old_name = perm["permission_name"]  # Get the current permission name
            perm["permission_name"] = permission_map.get(old_name, old_name)  # Replace if found in JSON, else keep original
        
        # Filter out permissions that start with "/"
        filtered_permissions = [perm for perm in permissions_result if not perm["permission_name"].startswith("/")]
        
        # Extract updated permission names from filtered results
        updated_permission_names = [perm["permission_name"] for perm in filtered_permissions]
        
        # Return the filtered result
        return {"details": filtered_permissions, "permission_names": updated_permission_names}
    
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
#         print(permissions_str)
#         if not permissions_str:
#             print("yes")
#             return {"details": [], "permission_names": []}

#         permissions_list = ast.literal_eval(permissions_str)
#         print(permissions_list)
#         if not permissions_list:
#             return {"details": [], "permission_names": []}

#         # Convert permission IDs to a tuple and format them for the IN clause
#         per_ids = tuple(permissions_list)
        
#         # Fetch details for the permissions using parameterized query
#         query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(','.join('?' for _ in per_ids))
#         cursor.execute(query, per_ids)
#         permissions_result = cursor.fetchall()

#         if not permissions_result:
#             return {"details": [], "permission_names": []}

#         # Create a list of permission names
#         permission_names = [perm['permission_name'] for perm in permissions_result]

#         return {"details": permissions_result, "permission_names": permission_names}

#     except sql.Error as err:
#         print(f"Error: {err}")
#         return {"details": [], "permission_names": []}
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return {"details": [], "permission_names": []}


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


########################################
###### testing ###################
######################################

    # Function to insert into regression_tests table
def insert_regression_test(
    system_name: str,
    execution_date: datetime,
    total_suite: int,
    total_pass: int,
    total_fail: int,
    description: str,
    result_file: str,
    created_by: int,
    updated_by: int,
    deleted_by: int = None
):

    try:


        cursor = get_cursor()
        sql = '''
        INSERT INTO regression_tests (system_name, execution_date, total_suite, total_pass, total_fail, description, result_file, created_by, updated_by, deleted_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            system_name,
            execution_date,
            total_suite,
            total_pass,
            total_fail,
            description,
            result_file,
            created_by,
            updated_by,
            deleted_by
        )
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid  # Return the ID of the inserted record
    except sql.Error as err:
        print(f"Error: {err}")
        return None



# Function to insert into unit_tests table
def insert_unit_test(
    execution_date: datetime,
    total_pass:int,
    total_fail:int,
    parent_system_name: str,
    system_name: str,
    task_name: str,
    description: str,
    result_file: str,
    modex:str,
    created_by: int,
    updated_by: int,
    deleted_by: int = None
):

    try:

        cursor = get_cursor()
        sql = '''
        INSERT INTO unit_tests (execution_date, total_pass, total_fail, parent_system_name, system_name, task_name, description, result_file, modex, created_by, updated_by, deleted_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
        '''
        values = (
            execution_date,
            total_pass,
            total_fail,
            parent_system_name,
            system_name,
            task_name,
            description,
            result_file,
            modex,
            created_by,
            updated_by,
            deleted_by
        )
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid  # Return the ID of the inserted record 
    except sql.Error as err:
        print(f"Error: {err}")
        return None


################################################
############ dashboard #################
##################################################

def last_5_reg_runs():
    try:
        # Set the row factory to allow dictionary-like access to rows
        # conn.row_factory = sql.Row  # Allows accessing rows by column names
        cursor = get_cursor()
        query = """
        SELECT execution_date, total_suite AS Total, total_pass AS Success,
                total_fail AS Failed, system_name, result_file AS html
        FROM regression_tests
        ORDER BY created_at DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        
        # Convert query results to desired output format
        last_runs = []
        for row in rows:
            # Check if result file exists
            html_link = ""
            if row[5]:  # if result_file is not None or empty
                file_path = os.path.join("Output", "Metrics", "Result", row[5])
                # Check if the file exists
                if os.path.isfile(file_path):
                    # File exists, use the URL
                    html_link = f"http://127.0.0.1:8000/Output/Metrics/Result/{row[5]}"
                    print("File exists!")
                else:
                    print(f"File does not exist: {file_path}")
            
            last_runs.append({
                "ExecutionDate": row[0],
                "Total": row[1],
                "Success": row[2],
                "Failed": row[3],
                "system_name": row[4],
                "html": html_link
            })
            
        return last_runs
    except sql.Error as err:
        print(f"Error: {err}")
        return None
 

def get_top_5_failed_consecutive_cases(system=None, date_from=None, date_to=None):
    try:
        cursor = get_cursor()
        current_date = datetime.now()
        
        # Handle date logic
        if date_from and date_from.strip():
            try:
                start_date = date_from
                start_date_obj = datetime.strptime(date_from, "%Y-%m-%d")
                
                if date_to and date_to.strip():
                    try:
                        end_date_obj = datetime.strptime(date_to, "%Y-%m-%d")
                        end_date = date_to if end_date_obj >= start_date_obj else date_from
                    except ValueError:
                        end_date = date_from
                else:
                    end_date = date_from
                
                date_range_description = f"From {start_date} to {end_date}" if start_date != end_date else f"Single date: {start_date}"
                
            except ValueError:
                raise ValueError("Invalid date_from format. Expected YYYY-MM-DD.")
        else:
            # Default to previous 30 days
            end_date_obj = current_date
            start_date_obj = end_date_obj - timedelta(days=30)
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date = end_date_obj.strftime("%Y-%m-%d")
            date_range_description = f"Previous 30 days: {start_date} to {end_date}"
        
        # Build query parameters
        params = []
        is_single_date = start_date == end_date
        
        # Date condition
        if is_single_date:
            date_condition = "DATE(execution_date) = ?"
            params.append(start_date)
        else:
            date_condition = "execution_date BETWEEN ? AND ?"
            end_date_with_time = end_date + " 23:59:59" if not end_date.endswith("23:59:59") else end_date
            params.extend([start_date, end_date_with_time])
        
        # System filter
        system_condition = " AND system_name = ?" if system and system.strip() else ""
        if system_condition:
            params.append(system)
        
        # Execute query
        query = f"""
        SELECT 
            execution_date, parent_system_name, system_name,
            task_name, result_file, total_fail, total_pass
        FROM 
            unit_tests
        WHERE {date_condition}{system_condition}
        ORDER BY execution_date ASC
        """
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        # Process results
        results = []
        for row in rows:
            execution_date, _, system_name, task_name, result_file, total_fail, total_pass = row
            
            file_data = ""
            if result_file:
                file_path = os.path.join("Output", "Metrics", "Result", result_file)
                if os.path.isfile(file_path):
                    file_data = f"http://127.0.0.1:8000/Output/Metrics/Result/{result_file}"
            
            results.append({
                "system_name": system_name,
                "template_name": task_name,
                "total_passed": total_pass,
                "total_failed": total_fail,
                "timestamp": execution_date,
                "file": file_data
            })
        
        # Create final result
        final_result = {
            "date_range": date_range_description,
            "data": results
        }
        
        if system and system.strip():
            final_result["system_filter"] = system
            
        return final_result
        
    except sql.Error as err:
        print(f"SQL Error: {err}")
        raise err
    except ValueError as err:
        print(f"Value Error: {err}")
        raise err
    except Exception as err:
        print(f"General Error: {err}")
        raise err
 

def get_latest_regression_test():
    try:
        cursor = get_cursor()

        query = """
        SELECT execution_date, total_suite, total_pass, total_fail, result_file, system_name
        FROM regression_tests
        WHERE schedule_id IS NULL  -- Changed from NOT IN to IS NULL
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            execution_date = row[0]
            total_suite = row[1]
            total_pass = row[2]
            total_fail = row[3]
            result_file = row[4]
            system_name = row[5]
            latest_file = result_file.split('/')[-1] if result_file else "N/A"
            
            result = {
                "ExecutionDate": execution_date,
                "Total": total_suite,
                "Success": total_pass,
                "Failed": total_fail,
                "SystemName": system_name,
                "html": f"http://127.0.0.1:8000/Output/Metrics/Result/{latest_file}",
            }
            return result
        else:
            print("No records found in regression_tests.")
            return None

    except sql.Error as err:
        print(f"Error: {err}")
        return None




###################################################
############# mail #########################
####################################################

def add_mail(email, created_by=None):

    try:

        
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
    try:
        
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
    try:
        
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
    

def update_role_for_user(user_id, role_ids):
    """
    Updates the user_role for a given user in the users table.

    Args:
        user_id (int): The ID of the user to update.
        role_ids (str): A comma-separated string of role IDs to assign to the user.

    Returns:
        dict: A dictionary containing the status of the update operation.
    """
    try:
        # Obtain a database cursor
        cursor = get_cursor()  # Ensures the database connection is initialized

        # Update query for the users table
        update_user_role_query = 'UPDATE users SET user_role = ? WHERE id = ?'

        # Perform the update for users table
        cursor.execute(update_user_role_query, (role_ids, user_id))

        # Commit the transaction
        conn.commit()

        # Return success status
        print(f"Successfully updated roles.")
        return {"status": "success", "message": f"Successfully updated roles."}

    except sql.Error as err:
        print(f"Error: {err}")
        return {"status": "error", "message": "Failed to update roles.", "error_details": str(err)}



###################################################################################################
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
    

def display_permissions_by_role(role_id):
    try:
        cursor = get_cursor(dictionary=True)

        # Fetch permissions for the role
        query = "SELECT id, permissions FROM role_permission_assignments WHERE role_id = ?"
        cursor.execute(query, (role_id,))
        result = cursor.fetchall()

        if not result:
            return {"details": [], "permission_urls": []}

        # Extract and evaluate the permissions string
        permissions_str = result[0]['permissions']
        print(permissions_str)
        if not permissions_str:
            print("yes")
            return {"details": [], "permission_urls": []}

        # Convert the permissions string into a list
        permissions_list = ast.literal_eval(permissions_str)
        if not permissions_list:
            return {"details": [], "permission_urls": []}

        # Convert permission IDs to a tuple and prepare the IN clause
        per_ids = tuple(permissions_list)

        # Fetch details for the permissions
        query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(','.join('?' for _ in per_ids))
        cursor.execute(query, per_ids)
        permissions_result = cursor.fetchall()
        #print(permissions_result,'permissions_resul11111111111111111111111111111t')
        if not permissions_result:
            return {"details": [], "permission_names": []}

        # Convert permissions_result rows to mutable dictionaries
        permissions_result = [dict(row) for row in permissions_result]
        #print(permissions_result,'permissions_resultttttttttttttttttttttttttttttttttttttttttttt')
        # Load the JSON mapping file
        with open("permission_mapping.json", "r") as json_file:
            permission_map = json.load(json_file)  # JSON with mappings
            print(permission_map,'permission_mapppppppppppp')
        # Replace permission names based on JSON mapping
        permission_urls = []    
        for perm in permissions_result:
            old_name = perm["permission_name"]  # Get the current permission name
            perm["permission_name"] = permission_map.get(old_name, old_name)  # Replace if found in JSON, else keep original
            #print(perm["permission_name"],'permmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
        # Extract updated permission names
        updated_permission_names = [perm["permission_name"] for perm in permissions_result]
        permission_url = permission_map.get("urls", {}).get(old_name, f"/api/{old_name.replace(' ', '_').lower()}")  # Fallback URL
        permission_urls.append(permission_url)
        #print(permission_urls,'permission_urls')
        #print(permissions_result,'permissions_resultttttttttttttttttttttttttttttttttttttttttttt')
        #print(updated_permission_names,'updated_permission_namesssssssssssssssssssssssssss')
        return {"details": permissions_result, "permission_names": permission_url}

    except sql.Error as err:
        #print(f"Error: {err}")
        return {"details": [], "permission_names": []}
    except Exception as e:
        #print(f"Unexpected error: {e}")
        return {"details": [], "permission_names": []}
    

# def display_permissions_by_user_id(user_id):
#     try:
#         # # Split `user_ids` to handle multiple IDs
#         # user_ids = user_ids.split(',')
#         # print("User IDsssssssssssssssssssssss:", user_ids)

#         cursor = get_cursor(dictionary=True)

#         # Step 1: Fetch `user_role` for each `id` from the `users` table
#         user_roles = []
#         user_role_query = """
#             SELECT DISTINCT u.user_role
#             FROM users u
#             WHERE u.id IN ({})
#         """.format(','.join('?' for _ in user_id))
#         print(user_role_query,'user_role_queryyyyyyyyyyyyyyyyyyyyyyyyyyyy')
#         print(f"Executing queryyyyyyyyyyyyyyyyyyyyyy: {user_role_query} with user_ids: {user_id}")
#         cursor.execute(user_role_query, tuple(user_id))
#         user_role_results = cursor.fetchall()
#         print(user_role_results,'user_role_resultssssssssssssssssssssssssss') 
#         if user_role_results:
#             # Split comma-separated user_role values for each user
#             for row in user_role_results:
#                 roles = row['user_role'].split(',')
#                 user_roles.extend(roles)  # Add each user_role to the list
#             print(f"Fetched User Roles: {user_roles}")
#         else:
#             print("No user roles found.")
#             return {"details": [], "permission_names": []}

#         # Remove duplicate roles
#         user_roles = list(set(user_roles))
#         print(f"Unique User Roles: {user_roles}")

#         # Step 2: Fetch permissions for each unique role_id from `role_permission_assignments`
#         combined_permissions = set()
#         role_permission_results = []
#         print(f"Fetching permissions for rolessssssssssssssss: {user_roles}")
#         for user_role in user_roles:
#             role_query = """
#                 SELECT rpa.role_id, rpa.permissions
#                 FROM role_permission_assignments rpa
#                 WHERE rpa.role_id = ?
#             """
#             print(f"Executing query: {role_query} with user_role: {user_role}")
#             cursor.execute(role_query, (user_role,))
#             role_results = cursor.fetchall()
#             print(f"Role Resultssssssssssssssssssss: {role_results}")
#             if role_results:
#                 role_permission_results.extend(role_results)
#                 for role in role_results:
#                     if role['permissions']:
#                         permissions_list = ast.literal_eval(role['permissions'])
#                         combined_permissions.update(permissions_list)
#             else:
#                 print(f"No role_permissions found for user_role {user_role}.")

#         # If no permissions are found, return an empty list
#         if not combined_permissions:
#             print("No combined permissions found.")
#             return {"details": [], "permission_names": []}

#         # Step 3: Fetch permission details from the `permissions` table
#         permission_query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(
#             ','.join('?' for _ in combined_permissions)
#         )
#         print(f"Executing query: {permission_query} with combined_permissions: {tuple(combined_permissions)}")
#         cursor.execute(permission_query, tuple(combined_permissions))
#         permissions_result = cursor.fetchall()
#         print(f"Permissions Result111111111111111111111: {permissions_result}")
#         if not permissions_result:
#             print("No permission details found.")
#             return {"details": [], "permission_names": []}

#         # Convert results to dictionaries
#         permissions_result = [dict(row) for row in permissions_result]
#         print(permissions_result,'permissions_result22222222222222222222222')
#         # Load the JSON mapping file
#         with open("permission_mapping.json", "r") as json_file:
#             permission_map = json.load(json_file)
#             print(permission_map,'permission_map')
#         # Replace permission names based on JSON mapping
#         for perm in permissions_result:
#             old_name = perm["permission_name"]
#             perm["permission_name"] = permission_map.get(old_name, old_name)

#         # Extract updated permission names
#         updated_permission_names = [perm["permission_name"] for perm in permissions_result]

#         return {
#             "details": permissions_result,
#             "permission_names": updated_permission_names,
#             "role_permissions": role_permission_results,
#         }

#     except sql.Error as err:
#         print(f"Database Error: {err}")
#         return {"details": [], "permission_names": [], "role_permissions": []}
#     except Exception as e:
#         print(f"Unexpected Error: {e}")
#         raise  # Re-raise the exception to see the full traceback


def display_permissions_by_user_id(user_id):
    try:
        # Ensure the user_id is a single integer
        if not isinstance(user_id, int):
            raise ValueError("user_id must be a single integer.")

        cursor = get_cursor(dictionary=True)

        # Step 1: Fetch `user_role` for the given `user_id` from the `users` table
        user_role_query = """
            SELECT u.user_role
            FROM users u
            WHERE u.id = ?
        """
        #print(f"Executing query: {user_role_query} with user_id: {user_id}")
        cursor.execute(user_role_query, (user_id,))
        user_role_result = cursor.fetchone()
        #print(user_role_result, 'user_role_result')

        if not user_role_result:
            #print("No user roles found.")
            return {"details": [], "permission_names": []}

        # Split and deduplicate the user roles
        user_roles = list(set(user_role_result['user_role'].split(',')))
        #print(f"Unique User Roles: {user_roles}")

        # Step 2: Fetch permissions for each unique role_id from `role_permission_assignments`
        combined_permissions = set()
        role_permission_results = []
        #print(f"Fetching permissions for roles: {user_roles}")
        for user_role in user_roles:
            role_query = """
                SELECT rpa.role_id, rpa.permissions
                FROM role_permission_assignments rpa
                WHERE rpa.role_id = ?
            """
            #print(f"Executing query: {role_query} with user_role: {user_role}")
            cursor.execute(role_query, (user_role,))
            role_results = cursor.fetchall()
            #print(f"Role Results: {role_results}")
            if role_results:
                role_permission_results.extend(role_results)
                for role in role_results:
                    if role['permissions']:
                        permissions_list = ast.literal_eval(role['permissions'])
                        combined_permissions.update(permissions_list)
            else:
                print(f"No role_permissions found for user_role {user_role}.")

        if not combined_permissions:
            #print("No combined permissions found.")
            return {"details": [], "permission_names": []}

        # Step 3: Fetch permission details from the `permissions` table
        permission_query = "SELECT id, permission_name FROM permissions WHERE id IN ({})".format(
            ','.join('?' for _ in combined_permissions)
        )
        #print(f"Executing query: {permission_query} with combined_permissions: {tuple(combined_permissions)}")
        cursor.execute(permission_query, tuple(combined_permissions))
        permissions_result = cursor.fetchall()
        #print(f"Permissions Result: {permissions_result}")
        if not permissions_result:
            #print("No permission details found.")
            return {"details": [], "permission_names": []}

        # Convert results to dictionaries
        permissions_result = [dict(row) for row in permissions_result]
        #print(permissions_result, 'permissions_result')

        # Extract raw permission names
        raw_permission_names = [perm["permission_name"] for perm in permissions_result]

        # Load the JSON mapping file
        with open("permission_mapping.json", "r") as json_file:
            permission_map = json.load(json_file)

        # Replace permission names in details using JSON mapping
        for perm in permissions_result:
            old_name = perm["permission_name"]
            perm["permission_name"] = permission_map.get(old_name, old_name)

        return {
            "details": permissions_result,  # Details contain mapped names
            "permission_names": raw_permission_names,  # Raw names from database
        }

    except sql.Error as err:
        #print(f"Database Error: {err}")
        return {"details": [], "permission_names": []}
    except Exception as e:
        #print(f"Unexpected Error: {e}")
        raise  # Re-raise the exception to see the full traceback
    
def get_role_details(role_ids: List[str]):
    try:
        cursor = get_cursor()

        placeholders = ','.join('?' for _ in role_ids)
        query = f"SELECT id, name FROM roles WHERE id IN ({placeholders})"
        cursor.execute(query, role_ids)
        roles = cursor.fetchall()

        # Convert to a list of dictionaries
        return [{"id": role[0], "name": role[1]} for role in roles]
    except sql.Error as err:
        #print(f"Error: {err}")
        return None
        
###############################################################
###########Test Scheduler######################################
    

def parse_days_input(days: str) -> list:
    #parse_days_input(days) handles flexible day specifications:
    #Accepts single days ("1"), ranges ("1-5"), or combinations ("1-5,7,9-11")
    #Returns a sorted list of days
    #Example: "1-5,7" → [1,2,3,4,5,7]
    """
    Parse days input which can be single day or range
    Example: "1" returns [1]
            "1-5" returns [1,2,3,4,5]
            "1,3,5" returns [1,3,5]
            "1-5,7,9-11" returns [1,2,3,4,5,7,9,10,11]
    """
    if not days:
        return []
        
    result = set()
    parts = days.split(',')
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    
    return sorted(list(result))

def get_schedule_dates(months: str, days: str, days_of_week: str, hour: str) -> list:
    """
    get_schedule_dates() generates actual schedule dates based on input criteria:

    Takes months, days, days_of_week, and hour as inputs
    Handles two scenarios:
    a. If specific days are provided: creates dates for each day in specified months
    b. If weekdays are provided: generates dates for specified weekdays in given months
    Returns a sorted list of datetime object
    Generate all schedule dates based    on input criteria
    """
    current_year = datetime.now().year
    schedule_dates = set()
    
    # Convert inputs to lists
    months_list = [int(m.strip()) for m in months.split(',') if m.strip()] if months else []
    days_list = parse_days_input(days) if days else []
    weekdays_list = [d.strip() for d in days_of_week.split(',')] if days_of_week else []
    
    # If specific days are provided, use them
    if days_list:
        for month in months_list:
            for day in days_list:
                try:
                    date = datetime.strptime(f"{month}/{day}/{current_year} {hour}", "%m/%d/%Y %H:%M")
                    schedule_dates.add(date)
                except ValueError:
                    continue  # Skip invalid dates (e.g., Feb 30)
    
    # If no specific days but weekdays are provided, calculate dates based on weekdays
    elif weekdays_list:
        weekday_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        target_weekdays = [weekday_map[day] for day in weekdays_list]
        
        for month in months_list:
            # Get all dates for the month
            start_date = datetime.strptime(f"{month}/1/{current_year}", "%m/%d/%Y")
            end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() in target_weekdays:
                    schedule_dates.add(datetime.combine(current_date.date(), 
                                                      datetime.strptime(hour, "%H:%M").time()))
                current_date += timedelta(days=1)
    
    return sorted(list(schedule_dates))

def run_scheduled_test(schedule_id: int, system_name: str, template_names: list, test_type: str, created_by: int):
    """Enhanced function to execute scheduled test with multiple templates"""
    logging.info(f"Executing scheduled test for Schedule ID: {schedule_id}")
    
    template_str = ', '.join(template_names)
    print(template_names,'templatenameeeeeeeeeeeeeeeeee')
    print(f"""
        Executing scheduled test:
        Schedule ID: {schedule_id}
        System: {system_name}
        Templates: {template_str}
        Test Type: {test_type}
        Triggered by: {created_by}
        Time: {datetime.now()}
    """)
#########################################################testing call ###################################################################



def get_timestamp_from_filename(filename: str) -> datetime:
    # Extract the date and time part from the filename
    # print(filename)
    basename = os.path.basename(filename)
    # print(basename,'basenamenameeeeeeeeeeeeeeeeeeeeee')
    date_str = basename.split('-')[1] + basename.split('-')[2].split('.')[0]
    # Convert to datetime object
    return datetime.strptime(date_str, "%Y%m%d%H%M%S")


def insert_regression_test_schedule(
    system_name: str, execution_date: str, total_suite: int, total_pass: int, total_fail: int,
    description: str, result_file: str, created_by: int, updated_by: int, schedule_id: int
):
    conn = initialize_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO regression_tests (
            system_name, execution_date, total_suite, total_pass, total_fail, description,
            result_file, created_by, updated_by, schedule_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        system_name, execution_date, total_suite, total_pass, total_fail, description,
        result_file, created_by, updated_by, schedule_id
    ))
    conn.commit()
    
def get_latest_file(directory: str, pattern: str):
    # Get a list of all files matching the pattern
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None, None
    # Sort files based on the timestamp extracted from the filename
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    # Return the latest file and its timestamp
    latest_file = files[0]
    timestamp = get_timestamp_from_filename(latest_file)
    return os.path.basename(latest_file), timestamp, latest_file


def insert_unit_test_schedule(
    execution_date: str, total_pass: int, total_fail: int, parent_system_name: str, system_name: str,
    task_name: str, description: str, result_file: str, modex: str, created_by: int, updated_by: int,schedule_id: int
):
    conn = initialize_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO unit_tests (
            execution_date, total_pass, total_fail, parent_system_name, system_name,
            task_name, description, result_file, modex, created_by, updated_by,schedule_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        execution_date, total_pass, total_fail, parent_system_name, system_name,
        task_name, description, result_file, modex, created_by, updated_by,schedule_id
    ))
    conn.commit()

with open("system_name.json", "r") as file:
    parent_systems = json.load(file)

def get_parent_system_name(system_name: str) -> str:
    # Iterate through each parent and its templates dictionary
    for parent, templates in parent_systems.items():
        # Iterate over each template key in the dictionary
        for template_key in templates.keys():
            # Check if the template key matches the system name pattern
            if system_name == template_key.replace("templates", "").lower():
                return parent
  


def testing_execution(schedule_id, system_name, test_type, created_by, template_name, modex):
    try:
        # Step 1: Update status to 'In Progress' at the start of execution
        cursor = get_cursor()
        cursor.execute("""
            UPDATE table_scheduler 
            SET status = 'In Progress' 
            WHERE id = ?
        """, (schedule_id,))
        conn.commit()
        
        # Debug print to confirm initial status
        print(f"Initial status set to: In Progress for schedule_id: {schedule_id}")

        # Step 2: Parse the template names
        template_names = [name.strip() for name in template_name.split(',') if name.strip()]
        responses = []

        # Step 3: Execute tests for each template
        for template in template_names:
            opcodekey = ""
            if test_type == "Regression":
                opcodekey = "All"
                modex = ""  # Reset modex for regression tests
            else:
                opcodekey = template  # Treat the template as an individual opcode
            
            print(f"Running test for template: {template}")
            print("opcodekey:", opcodekey)
            print("modex:", modex)
            print("system name:", system_name)

            
            if system_name=="opcode":
                res=process_opcode(opcodekey, modex)
            elif system_name=="soap":
                 res=process_soap(opcodekey, modex)
            elif system_name=="oepsoap":
                 res=process_oepsoap(opcodekey, modex)
            elif system_name=="oap":
                res=process_gui(opcodekey, modex)
            #await asyncio.sleep(5)
            response=json.loads(res)
            # Simulate test response
            """
            response = {
                "Suite": {
                    "TotalSuite": 1,
                    "TotalPassed": 0,
                    "TotalFailed": 1,
                    "ErrorDescription": f"Error unknown in template {template}",
                    "MetricsFileName": f"metrics-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
                }
            }
            """
            # Insert data into the database
            if opcodekey == "All":
                # Insert regression test details
                insert_regression_test_schedule(
                    system_name=system_name,
                    execution_date=get_timestamp_from_filename(response["Suite"]["MetricsFileName"]),
                    total_suite=int(response["Suite"]["TotalSuite"]),
                    total_pass=int(response["Suite"]["TotalPassed"]),
                    total_fail=int(response["Suite"]["TotalFailed"]),
                    description=response["Suite"]["ErrorDescription"],
                    result_file=response["Suite"]["MetricsFileName"],
                    created_by=created_by,
                    updated_by=created_by,
                    schedule_id=schedule_id
                )
            else:
                # Insert unit test details
                insert_unit_test_schedule(
                    execution_date=get_timestamp_from_filename(response["Suite"]["MetricsFileName"]),
                    total_pass=int(response["Suite"]["TotalPassed"]),
                    total_fail=int(response["Suite"]["TotalFailed"]),
                    parent_system_name=get_parent_system_name(system_name),
                    system_name=system_name,
                    task_name=opcodekey,  # Use template as the task name
                    description=response["Suite"]["ErrorDescription"],
                    result_file=response["Suite"]["MetricsFileName"],
                    modex=modex,
                    created_by=created_by,
                    updated_by=created_by,
                    schedule_id=schedule_id
                )
            
            # Construct the file path for the metrics file
            file_path = f"http://127.0.0.1:8000/Output/Metrics/Result/{response['Suite']['MetricsFileName']}"
            response["Suite"]["MetricsFileName"] = file_path
            responses.append(response)

            print(f"Completed test for template: {template}")

            # Try to update status to 'Completed' right after the print
            try:
                cursor = get_cursor()
                cursor.execute("""
                    UPDATE table_scheduler 
                    SET status = 'Completed' 
                    WHERE id = ?
                """, (schedule_id,))
                conn.commit()
                
                # Debug print to confirm status update
                cursor.execute("""
                    SELECT status FROM table_scheduler WHERE id = ?
                """, (schedule_id,))
                current_status = cursor.fetchone()[0]
                print(f"Status updated to: {current_status} for schedule_id: {schedule_id}")
                
            except Exception as update_error:
                print(f"Error updating status to Completed: {update_error}")

        # Return the results
        return {"status": "success", "results": responses}

    except Exception as e:
        # In case of any error, update the status to 'Failed'
        try:
            cursor = get_cursor()
            cursor.execute("""
                UPDATE table_scheduler 
                SET status = 'Failed' 
                WHERE id = ?
            """, (schedule_id,))
            conn.commit()
            print(f"Status updated to: Failed for schedule_id: {schedule_id} due to error")
        except Exception as fail_error:
            print(f"Error updating status to Failed: {fail_error}")

        # Log the error and return the error message
        print("Error:", e)
        return {"status": "error", "message": str(e)}


# Helper function to parse range or list input
def parse_range_or_list(input_str, valid_range):
    parsed = set()
    for part in input_str.split(','):
        part = part.strip()
        if '-' in part:  # Handle ranges like 1-5
            try:
                start, end = map(int, part.split('-'))
                if start < valid_range[0] or end > valid_range[1] or start > end:
                    raise ValueError
                parsed.update(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Invalid range: {part}")
        else:  # Handle single values
            try:
                value = int(part)
                if value < valid_range[0] or value > valid_range[1]:
                    raise ValueError
                parsed.add(value)
            except ValueError:
                raise ValueError(f"Invalid value: {part}")
    return sorted(parsed)


def insert_and_schedule_test(system_name, template_name, hour, day_of_week, months, days, test_type, modex, created_by):
    from main import scheduler  # Import the global scheduler

    # Validate and process input
    try:
        datetime.strptime(hour, "%H:%M")
        hour, minute = hour.split(':')
    except ValueError:
        return {"status": "error", "message": "Invalid hour format. Use HH:MM"}

    try:
        months_list = parse_range_or_list(months, (1, 12))
    except ValueError as e:
        return {"status": "error", "message": f"Invalid months format: {e}"}
    
    # Ensure either days or day_of_week is mandatory
    if not day_of_week and not days:
        return {"status": "error", "message": "Either 'days' or 'day_of_week' must be provided"}
    elif day_of_week and days:
        return {"status": "error", "message": "Only one of 'days' or 'day_of_week' can be provided"}

    try:
        if days:
            days_list = parse_range_or_list(days, (1, 31))
        else:
            days_list = '*'
    except ValueError as e:
        return {"status": "error", "message": f"Invalid days format: {e}"}
    

    try:
        valid_days = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        if day_of_week:
            day_of_week_list = []
            for part in day_of_week.split(','):
                part = part.strip().lower()
                if '-' in part:
                    start, end = part.split('-')
                    start_idx = valid_days[start.strip()]
                    end_idx = valid_days[end.strip()]
                    if start_idx > end_idx:
                        raise ValueError("Start day must precede end day in range.")
                    day_of_week_list.extend(range(start_idx, end_idx + 1))
                else:
                    day_of_week_list.append(valid_days[part])
            day_of_week_list = sorted(set(day_of_week_list))
        else:
            day_of_week_list = '*'
    except KeyError:
        return {"status": "error", "message": f"Invalid day of week: {part}"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    cron_trigger = CronTrigger(
        month=','.join(map(str, months_list)),
        day=','.join(map(str, days_list)) if days_list != '*' else '*',
        day_of_week=','.join(map(str, day_of_week_list)) if day_of_week_list != '*' else '*',
        hour=hour,
        minute=minute
    )

    task_id = hash((system_name, template_name, hour, minute, day_of_week, months, days, test_type, created_by, template_name, modex))


    #  Database operation
    
    try:
        cursor = get_cursor()
        """
        Check if a task_id exists and its deletion status
        Returns: (exists: bool, is_deleted: bool)
        """
        query = """
            SELECT deleted_at, id 
            FROM table_scheduler 
            WHERE task_id = ?
        """
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        if result is None:
            print("No existing record")
        else:
            deleted_at, schedule_id = result

            if not deleted_at:
                return {"status": "error", "message": f"Schedule with id {schedule_id} already exist"}
        
        template_name_list = template_name.split(',')  #convert to list
        hour_and_minute = f"{hour}:{minute}"  # Combined format HH:MM
        cursor = get_cursor()
        insert_query = """
            INSERT INTO table_scheduler (system_name, template_name, hour, day_of_week, months, days, test_type, created_by, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(insert_query, (
            system_name, str(template_name_list), hour_and_minute,
            day_of_week or "", ','.join(map(str, months_list)),
            days or "", test_type, created_by, task_id
        ))
        conn.commit()
        schedule_id = cursor.lastrowid
        # print(f"Jobs in scheduler: {[job.id for job in scheduler.get_jobs()]}")

        scheduler.add_job(
        testing_execution,
        trigger=cron_trigger,
        args=[schedule_id, system_name, test_type, created_by, template_name, modex],  # Include opcode and modex
        id=f"task_{task_id}",
        replace_existing=True  # Replace job if it already exists
        )
        cursor.execute("""
            UPDATE table_scheduler 
            SET status = 'Scheduled' 
            WHERE id = ?
        """, (schedule_id,))
        conn.commit()
        
        
        print(scheduler.get_jobs())
    except sql.Error as err:
        print(f"Error: {err}")
        return None

    return {"status": "success", "message": f"Task {task_id} scheduled using cron"}
  


def fetch_table_scheduler_details(login_username):
    """
    Fetch schedule details from table_scheduler table for a specific user.
    Only returns current and future schedules that haven't been deleted.
    
    Args:
        login_username (str): Username of the currently logged-in user.
    
    Returns:
        dict: Dictionary containing the status, message, and data.
    """
    conn = None
    try:
        # Initialize database connection
        conn = initialize_connection()
        cursor = conn.cursor()
        
        # Query to fetch scheduler details (only non-deleted records)
        query = """
        SELECT 
            id, system_name, template_name, hour, day_of_week,
            months, days, test_type, created_by, created_at,
            updated_by, updated_at, deleted_by, deleted_at
        FROM table_scheduler
        WHERE created_by = ? AND deleted_at IS NULL
        ORDER BY created_at DESC
        """
        cursor.execute(query, (login_username,))
        rows = cursor.fetchall()
        
        # If no schedules are found, return early
        if not rows:
            return {
                "status": "success",
                "message": f"No active schedules found for user {login_username}.",
                "data": []
            }
        
        # Get current date and time for filtering
        current_datetime = datetime.now()
        
        # Define weekday mapping
        weekday_mapping = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        schedules = []
        for row in rows:
            try:
                # Parse months to ensure they are valid
                months = row[5]
                if '-' in months:
                    start, end = map(int, months.split('-'))
                    if start < 1 or end > 12 or start > end:
                        raise ValueError("Invalid month range.")
                    months_list = list(range(start, end + 1))
                else:
                    months_list = [int(month.strip()) for month in months.split(',') if month.strip()]
                
                if any(month < 1 or month > 12 for month in months_list):
                    raise ValueError("Months must be between 1 and 12.")
                
                # Special handling for day_of_week if it contains named weekdays
                day_of_week = row[4]
                if day_of_week and isinstance(day_of_week, str) and day_of_week.lower() in weekday_mapping:
                    # Process by weekday name
                    target_weekday = weekday_mapping[day_of_week.lower()]
                    hour_str = row[3]
                    
                    # Parse hour
                    try:
                        if ':' in hour_str:
                            hour, minute = map(int, hour_str.split(':'))
                        else:
                            hour = int(hour_str)
                            minute = 0
                    except ValueError:
                        hour = 0
                        minute = 0
                    
                    # Calculate the next occurrence of this weekday
                    today = current_datetime.date()
                    days_ahead = target_weekday - today.weekday()
                    if days_ahead < 0:  # Target day already happened this week
                        days_ahead += 7
                    
                    next_occurrence = today + timedelta(days=days_ahead)
                    
                    # Get the next few occurrences (4 weeks worth)
                    occurrences = []
                    for i in range(4):  # Get 4 future occurrences
                        occurrence_date = next_occurrence + timedelta(days=i*7)
                        # Check if the month is in our list
                        if occurrence_date.month in months_list:
                            # Check if specific days were also specified
                            if not row[6] or str(occurrence_date.day) in str(row[6]).split(','):
                                occurrence_datetime = datetime.combine(
                                    occurrence_date, 
                                    datetime.min.time()
                                ).replace(hour=hour, minute=minute)
                                
                                # Only add if it's in the future
                                if occurrence_datetime > current_datetime:
                                    occurrences.append(occurrence_datetime.strftime("%Y-%m-%d %H:%M:%S"))
                    
                    schedule_dates = occurrences
                else:
                    # Generate schedule dates using existing method
                    schedule_dates = get_schedule_dates(
                        ','.join(map(str, months_list)),
                        row[6],  # days
                        row[4],  # day_of_week
                        row[3]   # hour
                    )
                
                if not schedule_dates:
                    continue  # Skip if no valid dates (empty list is not an error)
                
                # Filter out past schedules - only keep those in the future
                future_schedule_dates = []
                for date in schedule_dates:
                    # Check if date is already a datetime object
                    if isinstance(date, datetime):
                        date_obj = date
                    else:
                        # If it's a string, parse it
                        try:
                            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # Try alternative format if the first one fails
                            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M")
                    
                    # Add to future dates if it's in the future
                    if date_obj >= current_datetime:
                        future_schedule_dates.append(date if isinstance(date, str) else date_obj.strftime("%Y-%m-%d %H:%M:%S"))
                
                # Skip this schedule if all dates are in the past
                if not future_schedule_dates:
                    continue
                
            except ValueError as ve:
                return {"status": "error", "message": f"Invalid data in schedule ID {row[0]}: {ve}"}
            except Exception as e:
                return {"status": "error", "message": f"Error processing schedule ID {row[0]}: {e}"}
            
            # Build the schedule entry
            schedule = {
                "schedule_id": row[0],
                "schedule_details": {
                    "system_name": row[1],
                    "template_name": row[2],
                    "test_type": row[7],
                    "next_schedule": future_schedule_dates[0] if future_schedule_dates else None
                },
                "audit_info": {
                    "created": {
                        "by": row[8],
                        "at": row[9]
                    },
                   
                },
                "status": "ACTIVE"
            }
            schedules.append(schedule)
        
        return {
            "status": "success",
            "message": f"Found {len(schedules)} active current and future schedules for user {login_username}.",
            "data": schedules
        }
    
    except sql.Error as e:
        return {"status": "error", "message": f"Database error: {e}"}
def delete_schedule(schedule_id, deleted_by=None):
    from main import scheduler
    from datetime import datetime  # Make sure datetime is imported
    """
    Soft delete a test schedule and remove any associated scheduled tasks based on task_id.
    
    Args:
        schedule_id: ID of the schedule to delete
        deleted_by: ID of the user performing the deletion (optional)
        
    Returns:
        bool: True if successful, None if error occurred
    """
    try:
        # Get cursor
        cursor = get_cursor()

        # Retrieve the task_id associated with the schedule_id
        query = "SELECT task_id FROM table_scheduler WHERE id = ?"
        cursor.execute(query, (schedule_id,))
        result = cursor.fetchone()
        
        if result:
            task_id = result[0]
            print(f"Found task_id: {task_id} for schedule_id: {schedule_id}")
        else:
            print(f"No task found for schedule_id: {schedule_id}")
            return None

        # First, remove any scheduled tasks based on task_id
        current_jobs = scheduler.get_jobs()
        # print(f"Current jobs before deletion: {current_jobs}")

        job_found = False

        for job in current_jobs:
            # print(f"Checking job: {job.id}")
            if job.id == f"task_{task_id}":
                scheduler.remove_job(job.id)
                print(f"Canceled scheduled job with ID: {job.id}")
                job_found = True

        if not job_found:
            print(f"No job found with task_id: {task_id}")

        # Prepare the SQL query to perform soft delete
        query = """
        UPDATE table_scheduler
        SET deleted_at = ?, deleted_by = ?
        WHERE id = ?"""
        
        # Execute the query with parameters
        cursor.execute(query, (datetime.now(), deleted_by, schedule_id))
        
        # Commit changes
        conn.commit()
        print("Schedule soft delete executed and committed successfully")
        
        return True
        
    except sql.Error as err:
        print(f"Error: {err}")
        return None
    except Exception as e:
        print(f"Error while canceling scheduled tasks: {e}")
        return None

"""
def fetch_table_scheduler_details(login_username):
    
    Fetch schedule details from table_scheduler table for a specific user.

    Args:
        login_username (str): Username of the currently logged-in user.

    Returns:
        dict: Dictionary containing the status, message, and data.
    
    conn = None
    try:
        # Initialize database connection
        conn = initialize_connection()
        cursor = conn.cursor()

        # Query to fetch scheduler details
        query = 
        SELECT 
            id, system_name, template_name, hour, day_of_week, 
            months, days, test_type, created_by, created_at, 
            updated_by, updated_at, deleted_by, deleted_at 
        FROM table_scheduler 
        WHERE created_by = ?
        ORDER BY created_at DESC
        
        cursor.execute(query, (login_username,))
        rows = cursor.fetchall()

        # If no schedules are found, return early
        if not rows:
            return {
                "status": "success",
                "message": f"No schedules found for user {login_username}.",
                "data": []
            }

        schedules = []
        for row in rows:
            try:
                # Parse months to ensure they are valid
                months = row[5]
                if '-' in months:
                    start, end = map(int, months.split('-'))
                    if start < 1 or end > 12 or start > end:
                        raise ValueError("Invalid month range.")
                    months_list = list(range(start, end + 1))
                else:
                    months_list = [int(month.strip()) for month in months.split(',') if month.strip()]

                if any(month < 1 or month > 12 for month in months_list):
                    raise ValueError("Months must be between 1 and 12.")

                # Generate schedule dates
                schedule_dates = get_schedule_dates(
                    ','.join(map(str, months_list)),
                    row[6],  # days
                    row[4],  # day_of_week
                    row[3]   # hour
                )
                if not schedule_dates:
                    raise ValueError("No valid schedule dates generated.")
            except ValueError as ve:
                return {"status": "error", "message": f"Invalid data in schedule ID {row[0]}: {ve}"}
            except Exception as e:
                return {"status": "error", "message": f"Error processing schedule ID {row[0]}: {e}"}
            status = "DELETED"if row[13] else"ACTIVE"
            # Build the schedule entry
            schedule = {
                "schedule_id": row[0],
                "schedule_details": {
                    "system_name": row[1],
                    "template_name": ast.literal_eval(row[2]),
                    "schedule_time": {
                        "hour": row[3],
                        "day_of_week": row[4],
                        "months": months_list,
                        "days": row[6]
                    },
                    "test_type": row[7],
                    "schedule_dates": schedule_dates
                },
                "audit_info": {
                    "created": {
                        "by": row[8],
                        "at": row[9]
                    }
                },
                "status": status
            }
            schedules.append(schedule)

        return {
            "status": "success",
            "message": f"Found {len(schedules)} active schedules for user {login_username}.",
            "data": schedules
        }

    except sql.Error as e:
        return {"status": "error", "message": f"Database error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
"""

def get_test_details_by_system_and_creator(system_name: str, created_by: int):
    """
    Retrieve test details from both regression_tests and unit_tests tables
    based on system_name and created_by, only for completed schedule_ids.
    
    Args:
        system_name (str): Name of the system to query
        created_by (int): ID of the creator
        
    Returns:
        tuple: Two dictionaries containing regression and unit test details
    """
    conn = initialize_connection()
    cursor = conn.cursor()
    
    # Query for regression tests
    regression_query = """
        SELECT 
            system_name,
            execution_date,
            total_suite,
            total_pass,
            total_fail,
            description,
            result_file,
            schedule_id
        FROM regression_tests
        WHERE system_name = ? 
        AND created_by = ?
        AND schedule_id IS NOT NULL
        ORDER BY execution_date DESC
    """
    
    # Query for unit tests
    unit_query = """
        SELECT 
            execution_date,
            total_pass,
            total_fail,
            parent_system_name,
            system_name,
            task_name,
            description,
            result_file,
            schedule_id
        FROM unit_tests
        WHERE system_name = ? 
        AND created_by = ?
        AND schedule_id IS NOT NULL
        ORDER BY execution_date DESC
    """
    
    # Execute queries
    cursor.execute(regression_query, (system_name, created_by))
    regression_tests = cursor.fetchall()
    
    cursor.execute(unit_query, (system_name, created_by))
    unit_tests = cursor.fetchall()
    
    # Convert results to dictionaries for easier handling
    regression_results = []
    unit_results = []
    
    # Process regression tests
    for test in regression_tests:
         if test[7] != 0:   # Exclude entries with schedule_id == 0
            # Check if result file exists
            html_url = ""
            if test[6]:  # If result_file is not None or empty
                file_path = os.path.join("Output", "Metrics", "Result", test[6])
                if os.path.isfile(file_path):
                    html_url = f"http://127.0.0.1:8000/Output/Metrics/Result/{test[6]}"
                    print("File exists!")
                else:
                    print("File does not exist.")
                
            regression_results.append({
                'system_name': test[0],
                'execution_date': test[1],
                'total_suite': test[2],
                'total_pass': test[3],
                'total_fail': test[4],
                'description': test[5],
                'html': html_url,
                'schedule_id': test[7]
            })
            
    # Process unit tests
    for test in unit_tests:
        if test[8] != 0:  # Exclude entries with schedule_id == 0
            # Check if result file exists
            html_url = ""
            if test[7]:  # If result_file is not None or empty
                file_path = os.path.join("Output", "Metrics", "Result", test[7])
                if os.path.isfile(file_path):
                    html_url = f"http://127.0.0.1:8000/Output/Metrics/Result/{test[7]}"
                    print("File exists!")
                else:
                    print("File does not exist.")
            
            unit_results.append({
                'execution_date': test[0],
                'total_pass': test[1],
                'total_fail': test[2],
                'parent_system_name': test[3],
                'system_name': test[4],
                'task_name': test[5],
                'description': test[6],
                'html': html_url,
                'schedule_id': test[8]
            })
    
    return regression_results, unit_results

def insert_and_schedule_test(system_name, template_name, hour, day_of_week, months, days, test_type, modex, created_by):
    from main import scheduler  # Import the global scheduler

    # Validate and process input
    try:
        datetime.strptime(hour, "%H:%M")
        hour, minute = hour.split(':')
    except ValueError:
        return {"status": "error", "message": "Invalid hour format. Use HH:MM"}

    try:
        months_list = parse_range_or_list(months, (1, 12))
    except ValueError as e:
        return {"status": "error", "message": f"Invalid months format: {e}"}
    
    # Ensure either days or day_of_week is mandatory
    if not day_of_week and not days:
        return {"status": "error", "message": "Either 'days' or 'day_of_week' must be provided"}
    elif day_of_week and days:
        return {"status": "error", "message": "Only one of 'days' or 'day_of_week' can be provided"}

    try:
        if days:
            days_list = parse_range_or_list(days, (1, 31))
        else:
            days_list = '*'
    except ValueError as e:
        return {"status": "error", "message": f"Invalid days format: {e}"}
    

    try:
        valid_days = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        if day_of_week:
            day_of_week_list = []
            for part in day_of_week.split(','):
                part = part.strip().lower()
                if '-' in part:
                    start, end = part.split('-')
                    start_idx = valid_days[start.strip()]
                    end_idx = valid_days[end.strip()]
                    if start_idx > end_idx:
                        raise ValueError("Start day must precede end day in range.")
                    day_of_week_list.extend(range(start_idx, end_idx + 1))
                else:
                    day_of_week_list.append(valid_days[part])
            day_of_week_list = sorted(set(day_of_week_list))
        else:
            day_of_week_list = '*'
    except KeyError:
        return {"status": "error", "message": f"Invalid day of week: {part}"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    cron_trigger = CronTrigger(
        month=','.join(map(str, months_list)),
        day=','.join(map(str, days_list)) if days_list != '*' else '*',
        day_of_week=','.join(map(str, day_of_week_list)) if day_of_week_list != '*' else '*',
        hour=hour,
        minute=minute
    )

    task_id = hash((system_name, template_name, hour, minute, day_of_week, months, days, test_type, created_by, template_name, modex))


    #  Database operation
    
    try:
        cursor = get_cursor()
        """
        Check if a task_id exists and its deletion status
        Returns: (exists: bool, is_deleted: bool)
        """
        query = """
            SELECT deleted_at, id 
            FROM table_scheduler 
            WHERE task_id = ?
        """
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        if result is None:
            print("No existing record")
        else:
            deleted_at, schedule_id = result

            if not deleted_at:
                return {"status": "error", "message": f"Schedule with id {schedule_id} already exist"}
        
        template_name_list = template_name.split(',')  #convert to list
        hour_and_minute = f"{hour}:{minute}"  # Combined format HH:MM
        cursor = get_cursor()
        insert_query = """
            INSERT INTO table_scheduler (system_name, template_name, hour, day_of_week, months, days, test_type, created_by, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(insert_query, (
            system_name, str(template_name_list), hour_and_minute,
            day_of_week or "", ','.join(map(str, months_list)),
            days or "", test_type, created_by, task_id
        ))
        conn.commit()
        schedule_id = cursor.lastrowid
        # print(f"Jobs in scheduler: {[job.id for job in scheduler.get_jobs()]}")

        scheduler.add_job(
        testing_execution,
        trigger=cron_trigger,
        args=[schedule_id, system_name, test_type, created_by, template_name, modex],  # Include opcode and modex
        id=f"task_{task_id}",
        replace_existing=True  # Replace job if it already exists
        )
        print(scheduler.get_jobs())
    except sql.Error as err:
        print(f"Error: {err}")
        return None

    return {"status": "success", "message": f"Task {task_id} scheduled using cron"}

def view_link(schedule_id):
    """
    Fetch and display detailed information for a specific schedule based on its ID.
    Only shows current and upcoming schedule dates (filters out past dates).
    
    Args:
        schedule_id (int): ID of the schedule to view.
    
    Returns:
        dict: Dictionary containing the status, message, and detailed data for the requested schedule.
    """
    import datetime  # Add this import for date comparison
    
    conn = None
    try:
        # Initialize database connection
        conn = initialize_connection()
        cursor = conn.cursor()
        
        # Query to fetch scheduler details for the specific ID
        query = """
        SELECT 
            id, system_name, template_name, hour, day_of_week,
            months, days, test_type, created_by, created_at,
            updated_by, updated_at, deleted_by, deleted_at,
            task_id
        FROM table_scheduler
        WHERE id = ?
        """
        cursor.execute(query, (schedule_id,))
        row = cursor.fetchone()
        
        # If no schedule is found, return early
        if not row:
            return {
                "status": "error",
                "message": f"No schedule found with ID {schedule_id}.",
                "data": None
            }
        
        # Format the schedule data for display
        schedule_data = {
            "id": row[0],
            "system_name": row[1],
            "template_name": row[2],
            "hour": row[3],
            "day_of_week": row[4],
            "months": row[5],
            "days": row[6],
            "test_type": row[7],
            "created_by": row[8],
            "created_at": row[9],
            "updated_by": row[10],
            "updated_at": row[11],
            "deleted_by": row[12],
            "deleted_at": row[13],
            "task_id": row[14],
            "status": "ACTIVE"  # Assuming the schedule is active if it exists
        }
        
        # Generate schedule dates
        try:
            # Parse month data
            months = row[5]
            if '-' in str(months):
                start, end = map(int, str(months).split('-'))
                months_list = list(range(start, end + 1))
            else:
                months_list = [int(month.strip()) for month in str(months).split(',') if month.strip()]
            
            # Generate schedule dates
            all_schedule_dates = get_schedule_dates(
                ','.join(map(str, months_list)),
                row[6],  # days
                row[4],  # day_of_week
                row[3]   # hour
            )
            
            # Filter out past schedule dates
            current_date = datetime.datetime.now()
            # Assuming schedule_dates are datetime objects or strings in a format that can be parsed
            filtered_schedule_dates = []
            
            for date_item in all_schedule_dates:
                # If date_item is a string, convert to datetime object for comparison
                if isinstance(date_item, str):
                    try:
                        # Adjust this parsing format to match your actual date format
                        schedule_date = datetime.datetime.strptime(date_item, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Try another common format if the first one fails
                        schedule_date = datetime.datetime.strptime(date_item, "%Y-%m-%d")
                else:
                    schedule_date = date_item
                
                # Keep only current and future dates
                if schedule_date >= current_date:
                    filtered_schedule_dates.append(date_item)
            
        except Exception as e:
            return {"status": "error", "message": f"Error processing schedule dates: {e}", "data": schedule_data}
        
        # Format the response with filtered dates
        response = {
            "status": "success",
            "message": f"Current and upcoming schedule details retrieved successfully for ID {schedule_id}.",
            "data": {
                "schedule_id": row[0],
                "schedule_details": {
                    "system_name": row[1],
                    "template_name": row[2],
                    "schedule_time": {
                        "hour": row[3],
                        "day_of_week": row[4],
                        "months": months_list,
                        "days": row[6]
                    },
                    "test_type": row[7],
                    "schedule_dates": filtered_schedule_dates
                },
                "status": "ACTIVE",
            }
        }
        
        return response
    
    except sql.Error as e:
        return {"status": "error", "message": f"Database error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}




