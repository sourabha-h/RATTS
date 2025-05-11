from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, status,Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form, HTTPException , Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,RedirectResponse, HTMLResponse, FileResponse
from urllib.parse import quote
from typing import List, Dict
from uuid import uuid4 
from fastapi import Request
from typing import Optional, Union
from fastapi.staticfiles import StaticFiles
import logging
import glob
import pandas as pd
from io import StringIO
from urllib.parse import urlparse
import calendar
from sql_connectors import *
from form import *


from Tests.oepsoap_testsuite import *
#from Tests.test_process import *
from Tests.generate_csv import *
from Tests.soap_testsuite import *
#from Tests.oepsoap_testsuite import *
from Tests.gui_testsuite import *
from Tests.opcode_testsuite import *


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

SECRET_KEY = "test"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/Output/Metrics/Result", StaticFiles(directory="Output/Metrics/Result"), name="static")
app.mount("/Data/csvfiles", StaticFiles(directory="Data/csvfiles"), name="static1")

from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Configure persistent job store
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')  # Database file to store jobs
}
scheduler = BackgroundScheduler(jobstores=jobstores, timezone=timezone("Asia/Kolkata"))  # Replace with your timezone

# Initialize the scheduler with the job store
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

# Function to gracefully shut down the scheduler
def shutdown_scheduler():
    scheduler.shutdown()

# Ensure the scheduler stops gracefully on app shutdown
import atexit
atexit.register(shutdown_scheduler)
 
 

class UserLogin(BaseModel):
    username: str
    password: str

class AdminFunction(BaseModel):
    function: str
    user_name: str
    user_email: str
    user_password: str
    user_address: str
    user_country: str
    user_phone: str
    device_type: str
    device_address: str
    user_group: str
    user_role: str
    user_verified: str
    user_display_name: str
class TestSchedule(BaseModel):
    system_name: str
    template_name: str
    hour: str
    day_of_week: str
    months: str
    days : str
    # year: str
    test_type: str
    created_by: int
    modex: str = None


class TestScheduleUpdate(TestSchedule):
    updated_by: int

class TestDetails(BaseModel):
    regression_tests: List[dict]
    unit_tests: List[dict]

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
# Custom middleware to log incoming requests
async def log_requests(request: Request, call_next):
    # Log the request
    logging.info(f"Request received: {request.method} {request.url}")
    # Continue processing the request
    response = await call_next(request)
    return response



def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    print(hashed_password)
    return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(plain_password, hashed_password)

async def get_path_from_url(url):
    parsed_url = urlparse(url)
    print(parsed_url)
    return parsed_url.path

async def get_current_user(request: Request,token: str = Depends(oauth2_scheme)):
    print('token',token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentialsss",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)

        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role_id: int = payload.get("user_role")
        print(username,user_id)
        print(role_id)
        if username is None or user_id is None:
            raise credentials_exception

        path = await get_path_from_url(request.url.path)
        print(path)
        # if user_id != 7:
        permission_results = display_permissions_by_user_id(user_id)
        # permission_results = display_permissions_by_role(role_id)
        #print(permission_results)
        if path not in permission_results['permission_names']:
            raise HTTPException(status_code=403, detail="Permission denied")
        # if path not in permission_results['permission_names']:
        #     raise HTTPException(status_code=403, detail="Permission denied")
        return payload
    except JWTError:
        raise credentials_exception



@app.post("/token",tags=["User Management"])
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate JWT token
    user_id, user_role, user_group, display_name = get_user_id_role_by_username(form_data.username)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user[1],"user_id":user_id,"user_role":user_role,"user_group": user_group}, expires_delta=access_token_expires)

    # Return access token in response
    return {"access_token": access_token, "token_type": "bearer"}

# Add your authentication logic here
async def authenticate_user(username: str, password: str):
    user = get_authenticate_user(username)
    if user and verify_password(password, user[4]):
        return user
    return None


    
@app.post("/admin",tags=["User Management"])
async def process_admin(admin: AdminFunction):
    return admin_func(admin)

@app.post("/login/",tags=["User Management"])
async def login_user(user_login: UserLogin):
    # query = users.select().where(users.c.username == user_login.username)
    # user = await db.fetch_one(query)
    user = login_user_details(user_login.username)
    if user and verify_password(user_login.password.strip(), user[4]) and user[23] == 1:
        user_id, user_role, user_group, display_name = get_user_id_role_by_username(user_login.username)
        # Split the comma-separated user_role into a list of role IDs
        role_ids = user_role.split(",")
        # Fetch role details from the database
        roles = get_role_details(role_ids)
        # Generate JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user[1],"user_id":user_id,"user_role":user_role,"user_group": user_group}, expires_delta=access_token_expires)

        # Return access token in response
        return {"access_token": access_token, "token_type": "bearer",'user_id':user_id, "user_role": roles, "user_group": user_group,"display_name" : display_name}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/item")
def get_item(template_name: str, system_name:str, current_user: dict = Depends(get_current_user)):
    return get_template_content(template_name, system_name)

@app.get("/system_names")
def get_system_names(current_user: dict = Depends(get_current_user)):
    return get_system_name()

@app.get("/templates")
def get_templates(system_name:str, current_user: dict = Depends(get_current_user)):
    return get_template_names(system_name)

@app.post("/item_submit")
async def template_content_from_user(request: Request, template_name: str, system_name: str, current_user: dict = Depends(get_current_user)):
    response = await request.json()
    print(response)
    print(template_name)
    print(system_name)

    # Check if the response is empty or contains only empty objects
    if not response or all(isinstance(v, dict) and not v for v in response.values()):
        return "Failed to add"
    
    #process_testing(system_name, template_name, response, src=1)
    #return "Test case is executed"


@app.get("/last_5_runs", tags=["dashboard"])
def last_runs(current_user: dict = Depends(get_current_user)):
#     last_runs = [{"ExecutionDate": "20240708120000",  
#     "Total": 123,
#     "Success": 88,
#     "Failed": 35,
#     "Completed": "0",
#     "html": "http://127.0.0.1:8000/static/metrics-20240628-112527.html#"
#   },
#   {
#     "ExecutionDate": "20240709090000",  
#     "Total": 456,
#     "Success": 222,
#     "Failed": 234,
#     "Completed": "1",
#     "html": "http://127.0.0.1:8000/static/metrics-20240628-112527.html"
#   },
#     {
#     "ExecutionDate": "20240709090000",  
#     "Total": 456,
#     "Success": 222,
#     "Failed": 234,
#     "Completed": "1",
#     "html": "http://127.0.0.1:8000/static/metrics-20240628-112527.html"
#   }]
#     return last_runs
    return last_5_reg_runs()

@app.get("/top_failed_test_cases", tags=["dashboard"])
def top_failed(
    system: Optional[str] = None, 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Pass parameters in the correct order as expected by the refactored function
        result = get_top_5_failed_consecutive_cases(system, date_from, date_to)
                 
        # If for some reason the result is None, return an empty structure
        if result is None:
            return {
                "date_range": "No data available",
                "data": []
            }
                 
        return result
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
        


def get_timestamp_from_filename(filename: str) -> datetime:
    # Extract the date and time part from the filename
    print(filename)
    basename = os.path.basename(filename)
    print(basename)
    date_str = basename.split('-')[1] + basename.split('-')[2].split('.')[0]
    # Convert to datetime object
    return datetime.strptime(date_str, "%Y%m%d%H%M%S")

# def get_latest_file(directory: str, pattern: str):
#     # Get a list of all files matching the pattern
#     files = glob.glob(os.path.join(directory, pattern))
#     if not files:
#         return None, None
#     # Sort files based on the timestamp extracted from the filename
#     files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
#     # Return the latest file and its timestamp
#     latest_file = files[0]
#     timestamp = get_timestamp_from_filename(latest_file)
#     return os.path.basename(latest_file), timestamp

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


@app.get("/last_completed_run", tags=["dashboard"])
def last_run(current_user: dict = Depends(get_current_user)):
    try:
        return get_latest_regression_test()
    except Exception as e:
        return {"error": f"Failed to get latest result: {str(e)}"}
    
    
@app.get('/metrics_folder/{filename}')
def get_report(filename: str, current_user: dict = Depends(get_current_user)):
    file_path = os.path.join('metrics_folder', filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Report not found")
    


@app.post("/add_mail")
async def api_add_mail(email:EmailStr, current_user: dict = Depends(get_current_user)):
    try:
        if add_mail(email):
            return {"response":"added"}
        else:
            return {"response":"unable to add"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete_mail")
async def api_delete_mail(email:EmailStr, current_user: dict = Depends(get_current_user)):
    try:
        if delete_mail(email):
            return {"response":"deleted"}
        else:
            return {"response":"unable to delete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_mail_ids")
async def api_get_all_mail_ids(current_user: dict = Depends(get_current_user)):
    try:
        mail_ids = []
        for mail in get_all_mail_ids():
            mail_ids.append(mail[0])
        return mail_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Mapping of opcode to corresponding JSON file
json_files = {
    "opcode": Path("Data/config/opcodes.json"),
    "oepsoap": Path("Data/config/oepsoap_requests.json"),
    "soap": Path("Data/config/soap_requests.json"),
    "gui": Path("Data/config/gui_url.json")
}

# Function to load JSON data from file
def load_json_data(file_path: Path):
    if file_path.exists():
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        # If file doesn't exist, initialize a basic structure
        if "opcode" in file_path.stem:
            return {"opcodes": {"general": {}, "multitask": [{}]}}
        elif "oepsoap" in file_path.stem:
            return {"oep_operation": {}}
        elif "soap" in file_path.stem:
            return {"operation": {}}
        elif "gui" in file_path.stem:
            return {"urls":{}}

# Function to save JSON data to file
def save_json_data(file_path: Path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

class GeneralTemplate(BaseModel):
    key: str
    value: str

class MultitaskStep(BaseModel):
    sequence: int
    opcode: str
    loop: int = 0

class AddOpcodeRequest(BaseModel):
    task_type: str  # "general" or "multitask"
    opcode: Union[GeneralTemplate, List[MultitaskStep]]  # General opcode or list of multitask steps
    task_name: str = None  # Required for multitask

# Endpoint to add to either "general" or "multitask"
@app.post("/add_opcode/")
async def add_opcode(request: AddOpcodeRequest, opcode_type: str = Query(..., description="The type of opcode: opcode, oepsoap, soap"), current_user: dict = Depends(get_current_user)):
    if opcode_type not in json_files:
        raise HTTPException(status_code=400, detail="Invalid opcode type provided")

    # Load existing data from the appropriate JSON file
    file_path = json_files[opcode_type]
    data = load_json_data(file_path)

    if opcode_type == "opcode":
        # Handle the case for "opcode"
        if request.task_type == "general":
            if isinstance(request.opcode, GeneralTemplate):
                if request.opcode.key not in data['opcodes']['general']:
                    data['opcodes']['general'][request.opcode.key] = request.opcode.value
                else:
                    raise HTTPException(status_code=400, detail="Opcode already exists in general")
            else:
                raise HTTPException(status_code=400, detail="Invalid input for general task type")
        
        elif request.task_type == "multitask":
            if request.task_name and isinstance(request.opcode, list):
                multitask_dict = data['opcodes']['multitask']
                if request.task_name not in multitask_dict:
                    multitask_dict[request.task_name] = [
                        {"sequence": step.sequence, "opcode": step.opcode, "loop": step.loop}
                        for step in request.opcode
                    ]
                else:
                    raise HTTPException(status_code=400, detail="Task already exists in multitask")
            else:
                raise HTTPException(status_code=400, detail="Invalid input for multitask type")
        else:
            raise HTTPException(status_code=400, detail="Invalid task type")
    
    elif opcode_type == "oepsoap":
        # Handle the case for "oepsoap"
        if request.task_type == "general" and isinstance(request.opcode, GeneralTemplate):
            if request.opcode.key not in data["oep_operation"]:
                data["oep_operation"][request.opcode.key] = request.opcode.value
            else:
                raise HTTPException(status_code=400, detail="Operation already exists in oepsoap")
        else:
            raise HTTPException(status_code=400, detail="Invalid input for oepsoap")
    
    elif opcode_type == "soap":
        # Handle the case for "soap"
        if request.task_type == "general" and isinstance(request.opcode, GeneralTemplate):
            if request.opcode.key not in data["operation"]:
                data["operation"][request.opcode.key] = request.opcode.value
            else:
                raise HTTPException(status_code=400, detail="Operation already exists in soap")
        else:
            raise HTTPException(status_code=400, detail="Invalid input for soap")
        
    elif opcode_type == "gui":
        # Handle the case for "soap"
        if request.task_type == "general" and isinstance(request.opcode, GeneralTemplate):
            if request.opcode.key not in data["urls"]:
                data["urls"][request.opcode.key] = request.opcode.value
            else:
                raise HTTPException(status_code=400, detail="Operation already exists in oap")
        else:
            raise HTTPException(status_code=400, detail="Invalid input for oap")
    
    # Save the updated data back to the respective JSON file
    save_json_data(file_path, data)

    return {"message": f"Data added successfully to {opcode_type}", "data": data}


# Endpoint to get JSON data based on the opcode type
@app.get("/get_opcode_general")
async def opcode_general(opcode: str = Query(..., description="The opcode to retrieve, e.g., oepsoap, soap, etc."), current_user: dict = Depends(get_current_user)):
    try:
        # Retrieve the correct file based on the input opcode
        if opcode in json_files:
            file_path = json_files[opcode]
        else:
            raise HTTPException(status_code=400, detail="Invalid opcode provided")

        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Read and return the JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(data)
            return JSONResponse(content=data) 

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


ROOT_DIR = './Data/Templates'

class TemplateRequest(BaseModel):
    template: str  # Replacing opcode with template
    system_name: str
    template_content: str = None  # Optional for "view" action
    action: str  # "add" or "view"

def generate_template_name(template: str, system_name: str) -> str:
    # Convert template to lowercase and remove underscores
    base_name = template.replace('_', '').lower()
    base_name = base_name.replace('-', '').lower()
    # If system name is 'soap', prefix the template name with 'soap'
    if system_name.lower() == "soap":
        return f"soap{base_name}.yaml.template"
    return f"{base_name}.yaml.template"

def get_system_folder(system_name: str) -> str:
    # Append 'templates' to all system names
    return os.path.join(ROOT_DIR, f"{system_name}templates")

@app.post("/template/")
async def manage_template(request: TemplateRequest, current_user: dict = Depends(get_current_user)):
    template = request.template  # Updated to use template
    system_name = request.system_name
    template_content = request.template_content
    action = request.action.lower()

    print(template)
    if action not in ["add", "view"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'add' or 'view'.")

    # Get the folder path for the system
    system_folder_path = get_system_folder(system_name)

    # Check if the system folder exists, if not create it
    if not os.path.exists(system_folder_path):
        os.makedirs(system_folder_path)

    # Generate template name based on system name
    template_name = generate_template_name(template, system_name)  # Updated to use template
    template_file_path = os.path.join(system_folder_path, template_name)

    if action == "add":
        print(template_content)
        # If the template content is missing, raise an error
        if not template_content:
            raise HTTPException(status_code=400, detail="Missing template content for 'add' action.")
        
        # Write the template content to the file, creating the file if it doesn't exist
        try:
            print(template_file_path)
            with open(template_file_path, 'w') as f:
                f.write(template_content)
                print("done")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing to file: {e}")
        
        return {"message": "saved successfully"}

    elif action == "view":
        # Check if the template file exists before reading it
        if not os.path.exists(template_file_path):
            # If the file does not exist, create an empty one and return that
            try:
                with open(template_file_path, 'w') as f:
                    f.write('')  # Create an empty file
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating file: {e}")
            return {"template_content": ""}  # Return empty content for newly created file

        # Read and return the content of the existing template
        try:
            with open(template_file_path, 'r') as f:
                content = f.read()
                print(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {e}")
        
        return {"template_content": content}


# @app.post("/upload-csv/")
# async def upload_csv(file: UploadFile = File(...)):
#     if file.content_type != 'text/csv':
#         return {"error": "Only CSV files are accepted"}

#     content = await file.read()
#     # Convert the byte content to a string
#     decoded_content = content.decode("utf-8")

#     # Use StringIO to simulate a file object for pandas
#     data = StringIO(decoded_content)
    
#     # Load CSV into a pandas dataframe
#     df = pd.read_csv(data)
    
#     # Return the dataframe as a dictionary or process it further
#     return {"filename": file.filename, "data": df.to_dict(orient="records")}

def generate_template_name_csv(template: str, system_name: str) -> str:
    # Convert template to lowercase and remove underscores
    base_name = template.replace('_', '').lower()
    base_name = base_name.replace('-', '').lower()
    # If system name is 'soap', prefix the template name with 'soap'
    if system_name.lower() == "soap":
        return f"soap{base_name}"
    return base_name

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), template_name: str = Form(...), system_name: str = Form(...), current_user: dict = Depends(get_current_user)):
    if file.content_type != 'text/csv':
        return {"error": "Only CSV files are accepted"}
    base_name = template_name.replace('_', '').lower()
    base_name = base_name.replace('-', '').lower()
    if base_name not in file.filename:
        raise HTTPException(status_code=404, detail="Invalid file name.")
    # Get the generated template name
    expected_name = generate_template_name_csv(template_name, system_name)
    expected_name = expected_name + "_template.csv"
    # If the file name doesn't match, rename it
    new_filename = file.filename
    if file.filename != expected_name:
        new_filename = expected_name

    content = await file.read()
    decoded_content = content.decode("utf-8")
    data = StringIO(decoded_content)
    
    # Define the folder where CSV files will be saved
    base_save_folder = "Data/csvfiles"
    

    # Create system_name folder inside 'csvfiles' if it doesn't exist
    system_folder = os.path.join(base_save_folder, system_name)
    os.makedirs(system_folder, exist_ok=True)  # Create folder if it doesn't exist

    # Save the file in the 'csvfiles/system_name' folder with the new name
    save_path = os.path.join(system_folder, new_filename)
    with open(save_path, "wb") as f:
        f.write(content)

    # Return the new file name and the dataframe as a dictionary
    return JSONResponse({"response": f"{new_filename} uploaded successfully"})


@app.post("/generate-csv/")
async def generate_csv(template_name: str = Form(...), system_name: str = Form(...), current_user: dict = Depends(get_current_user)):
    print(template_name)
    template_name = generate_template_name(template_name, system_name)
    # Convert system_name to lowercase and append "templates"

    system_name_modified = f"{system_name.lower()}templates"
    print(template_name)
    print(system_name_modified)
    
    # Pass the modified system_name to the create_csv function
    create_csv(template_name, system_name_modified)
    await asyncio.sleep(5)
    return {"response": "CSV file generated."}




@app.post("/download-csv/")
async def download_csv(template_name: str = Form(...), system_name: str = Form(...), current_user: dict = Depends(get_current_user)):

    print(generate_template_name_csv(template_name,system_name))
    # Construct the full file path for the CSV file

    system_folder = system_name
    file_path = f"http://127.0.0.1:8000/Data/csvfiles/{system_folder}/{generate_template_name_csv(template_name,system_name)}_template.csv"
    check_file_path = f"Data/csvfiles/{system_folder}/{generate_template_name_csv(template_name,system_name)}_template.csv"
    # Check if the file exists before sending the download path
    if not os.path.exists(check_file_path):
        raise HTTPException(status_code=404, detail="CSV file not found.")

    # Return the download URL or file path
    return {"file_path": file_path}


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

import asyncio
import time
@app.post("/testing/")
async def unit_regressive_testing(opcodekey: str = Form(...), modex: str = Form(...), system_name: str = Form(...), current_user: dict = Depends(get_current_user)):
        print(current_user)
        if opcodekey == "All":
            modex = ""
        print("opcodekey",opcodekey)
        print("modex", modex)
        print("system name", system_name)
        
        try:
            res=''
            
            if system_name=="opcode":
                res=process_opcode(opcodekey, modex)
            elif system_name=="soap":
                res=process_soap(opcodekey, modex)
            elif system_name=="oepsoap":
                res=process_oepsoap(opcodekey, modex)
            elif system_name=="gui":
                res=process_gui(opcodekey, modex)
            await asyncio.sleep(5)
            response=json.loads(res)
            #response=res
            print(response["Suite"]["MetricsFileName"])
            """
            response = {
                "Suite": {
                        "TotalSuite": 1,
                        "TotalPassed": 1,
                        "TotalFailed": 0,
                        "ErrorDescription": "",
                        "MetricsFileName": "metrics-20250120-182144.html"
                }
                }
            """
            # Check if the test is regression or unit
            if opcodekey == "All":
                # Insert into regression_tests
                insert_regression_test(
                    system_name=system_name,
                    execution_date=get_timestamp_from_filename(response["Suite"]["MetricsFileName"]),
                    total_suite=int(response["Suite"]["TotalSuite"]),
                    total_pass=int(response["Suite"]["TotalPassed"]),
                    total_fail=int(response["Suite"]["TotalFailed"]),
                    description=response["Suite"]["ErrorDescription"],
                    result_file=response["Suite"]["MetricsFileName"],
                    created_by=current_user["user_id"],
                    updated_by=current_user["user_id"]
                )
            else:
                
                # Insert into unit_tests
                insert_unit_test(
                    execution_date=get_timestamp_from_filename(response["Suite"]["MetricsFileName"]),  # Example execution date, replace as needed
                    total_pass=int(response["Suite"]["TotalPassed"]),
                    total_fail=int(response["Suite"]["TotalFailed"]),
                    parent_system_name=get_parent_system_name(system_name),  # Replace with actual value
                    system_name=system_name,
                    task_name=opcodekey,  # Replace with actual task name
                    description=response["Suite"]["ErrorDescription"],
                    result_file=response["Suite"]["MetricsFileName"],
                    modex=modex,
                    created_by=current_user["user_id"],
                    updated_by=current_user["user_id"]
                )
            file_path = f"http://127.0.0.1:8000/Output/Metrics/Result/{response['Suite']['MetricsFileName']}"
            response["Suite"]["MetricsFileName"] = file_path
            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred."+e)
    
   
      

@app.get("/display_all_permissions/",tags=["User Management"])
async def display_all_permissions(current_user: dict = Depends(get_current_user)):
    result = display_permissions()
    return result

@app.get("/display_all_permissions_by_role/",tags=["User Management"])
async def display_all_permissions_role(role_id:int, current_user: dict = Depends(get_current_user)):
    permission_result= display_permissions_by_role(role_id)
    #print(permission_result)
    # permission_result = []
    return permission_result

class PermissionIdsRequest(BaseModel):
    permission_ids: List[int]
@app.post("/insert_permissions_for_role/", tags=["User Management"])
async def insert_permissions_for_role(
    role_id: int,
    request: PermissionIdsRequest,
    current_user: dict = Depends(get_current_user)
):
    permission_ids = request.permission_ids
    result = insert_or_update_role_permissions(role_id, permission_ids)
    return result
 
@app.get("/user-role",tags=['User Management'])
async def get_user_role(current_user: dict = Depends(get_current_user)):
    # role_id = current_user['user_role']
    # return {"role_id": role_id}
    pass

@app.post("/create_role/",tags=["User Management"])
async def create_user_role(role_name:str, current_user: dict = Depends(get_current_user)):
    # print("permission id",permission_ids)
    result = create_role(role_name)
    return result

@app.post("/fetch_roles/",tags=["User Management"])
async def fetch_roles_list(current_user: dict = Depends(get_current_user)):
    # print("permission id",permission_ids)
    result = fetch_roles()
    return result



from fastapi.responses import HTMLResponse



@app.get('/get_metrics_html')
async def get_metrics():
    html_path = 'D:/OneDrive - BlueRose Technologies Pvt. Ltd/Desktop/Ratzz/fastapi/Output/Metrics/Result/metrics-20240621-122720.html'
    
    # Read the HTML file content
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Return the HTML content as an HTMLResponse
        return HTMLResponse(content=html_content, status_code=200)
    
    except Exception as e:
        return {"error": f"Failed to read HTML file: {str(e)}"}

@app.post("/update_role_for_user/", tags=["User Management"])
async def update_role_for_user_(user_id: int, role_ids: str = None, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to update roles for a specific user.

    Args:
        role_ids (str): Comma-separated string of role IDs.
        user_id (int): ID of the user to update.
        current_user (dict): The current authenticated user's details.

    Returns:
        dict: A response with a message and the result of the operation.
    """
    try:
        # Call the `update_role_for_user` function and get the result
        result = update_role_for_user(user_id, role_ids)

        # Handle success or error response from the function
        if result["status"] == "success":
            return {
                "status": "success",
                "message": result["message"],
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": result["message"],
                    "error_details": result.get("error_details")
                }
            )
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An unexpected error occurred.",
                "error_details": str(ex)
            }
        )


@app.get("/display_all_permission_user_id/", tags=["User Management"])
async def display_all_permission_user_by_(user_id: int, current_user: dict = Depends(get_current_user)) -> Dict:
    try:
        # Log to debug the incoming parameter
        #logging.info(f"Received user_role: {user_id}")
        #print("nigga",user_id)

        # Fetch permissions for the given user role
        permission_result = display_permissions_by_user_id(user_id)

        # Log or print the result (for debugging or monitoring)
        #logging.info(f"Permissions fetched for user_role {user_id}: {permission_result}")

        if not permission_result or not permission_result.get("details"):
            raise HTTPException(status_code=404, detail="No permissions found for the given role.")

        return permission_result

    except Exception as e:
        # Log any unexpected errors
        #logging.error(f"Unexpected error occurred while fetching permissions for user_role {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/create_test_schedule/", tags=["Test Schedular"])
async def create_test_schedule(schedule: TestSchedule , current_user: dict = Depends(get_current_user))-> Dict:
    """
    API endpoint to create a new test schedule
    
    Args:
        schedule (TestSchedule): Schedule data validated by Pydantic model
        
    Returns:
        dict: Status and schedule ID
    """
    try:
        schedule_id = insert_and_schedule_test(
            system_name=schedule.system_name,
            template_name=schedule.template_name,
            hour=schedule.hour,
            day_of_week=schedule.day_of_week,
            months=schedule.months,
            days = schedule.days,
            test_type=schedule.test_type,
            modex = schedule.modex,
            created_by=schedule.created_by
        )
        
        return {
            "message": schedule_id
        }

        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.delete("/delete_schedule_id", tags=["Test Schedular"])
async def delete_schedule_endpoint(schedule_id: int, deleted_by: int = None , current_user: dict = Depends(get_current_user))-> Dict:
    """
    API endpoint to delete a schedule
    """
    result = delete_schedule(schedule_id, deleted_by)
    if result:
        return {"status": "success", "message": "Schedule deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Error deleting schedule")



@app.get("/fetch_all_schedules_details",  tags=["Test Schedular"])
async def get_schedule_details(user_id: int,current_user: dict = Depends(get_current_user)) -> Dict:
    """
    API endpoint to fetch schedule details for the authenticated user
    
    Args:
        current_user (dict): Current authenticated user information from the JWT token
        
    Returns:
        Dict: Schedule details for the authenticated user
    """
    try:
        # Extract username or user identifier from the current_user
        logged_in_user = current_user.get('user_id')  # adjust this based on your user dict structure
        
        if not logged_in_user:
            raise HTTPException(
                status_code=400,
                detail="User information not found in the token"
            )
            
        # Pass the logged-in user to the fetch function
        result = fetch_table_scheduler_details(user_id)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching schedule details: {str(e)}"
        )
    
    
    
def get_all_endpoints(app: FastAPI) -> List[str]:
    return [route.path for route in app.routes]


@app.get("/tests/", response_model=TestDetails, tags=["Test Schedular"])
async def get_test_details(system_name: str, created_by: int,current_user: dict = Depends(get_current_user)) -> Dict:
    try:
        # Assuming this function returns a tuple of regression_tests and unit_tests
        regression_tests, unit_tests = get_test_details_by_system_and_creator(
            system_name=system_name,
            created_by=created_by
        )
        return TestDetails(
            regression_tests=regression_tests,
            unit_tests=unit_tests
        )
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/create_test_schedule/", tags=["Test Schedular"])
async def create_test_schedule(schedule: TestSchedule , current_user: dict = Depends(get_current_user))-> Dict:
    """
    API endpoint to create a new test schedule
    
    Args:
        schedule (TestSchedule): Schedule data validated by Pydantic model
        
    Returns:
        dict: Status and schedule ID
    """
    try:
        schedule_id = insert_and_schedule_test(
            system_name=schedule.system_name,
            template_name=schedule.template_name,#template_name take single it will schedule single test if i give multi
            hour=schedule.hour,
            day_of_week=schedule.day_of_week,
            months=schedule.months,
            days = schedule.days,
            test_type=schedule.test_type,
            modex = schedule.modex,
            created_by=schedule.created_by
        )
        
        return {
            "message": schedule_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
@app.get("/schedule_view_link", tags=["Test Schedular"]) 
async def schedule_view_link_id(schedule_id: int, current_user: dict = Depends(get_current_user)) -> Dict:
    """
    API endpoint to fetch schedule details for a specific schedule ID
    
    Args:
        schedule_id (int): ID of the schedule to view
        current_user (dict): Current authenticated user information from the JWT token
        
    Returns:
        Dict: Schedule details for the requested schedule ID
    """
    try:
        # Extract user_id from the current_user token
        user_id = current_user.get('user_id')
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="User ID not found in the token"
            )
        
        # Pass the schedule_id to the view function
        result = view_link(schedule_id)
        
        # Optional: Add authorization check to ensure the user can view this schedule
        # For example, check if the schedule belongs to this user or if they have admin rights
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching schedule details: {str(e)}"
        )
        
# Print all endpoints
endpoints = get_all_endpoints(app)
insert_permissions(endpoints)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)
    all_endpoints = get_all_endpoints(app)
















