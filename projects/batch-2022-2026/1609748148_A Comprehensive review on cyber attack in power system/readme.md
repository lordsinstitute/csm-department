### Check for python Version
python --version
You should see Python 3.11.9

### Create Virtual Environment
python -m venv venv

Activate it:

Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

You'll see (venv) in your terminal. ✅

### Install Requirements 

pip install -r requirements.txt

### Create a database 

## Open MySQL Workbench or MySQL Command Line

CREATE DATABASE npp_cyber_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



### Run in this exact order
```
python manage.py makemigrations authentication
python manage.py migrate
python manage.py createsuperuser
```


When prompted:
```
Username: admin
Email: admin@npp.gov
Password: (your choice)
Password (again): (repeat)
```


### Load Sample Data
```
python generate_data.py
```


### Run the Server
```
python manage.py runserver