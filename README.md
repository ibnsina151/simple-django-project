# Grok Django Upgrade Demo
## Installation

### Prerequisites

#### 1. Install Python
Install ```python-3.7.2``` and ```python-pip```. Follow the steps from the below reference document based on your Operating System.
Reference: [https://docs.python-guide.org/starting/installation/](https://docs.python-guide.org/starting/installation/)

#### 2. Install MySQL
Install ```mysql-8.0.15```. Follow the steps form the below reference document based on your Operating System.
Reference: [https://dev.mysql.com/doc/refman/5.5/en/](https://dev.mysql.com/doc/refman/5.5/en/)
#### 3. Setup virtual environment
```bash
# Install virtual environment
sudo pip install virtualenv

# Make a directory
mkdir envs

# Create virtual environment
virtualenv ./envs/

# Activate virtual environment
source envs/bin/activate
```

#### 4. Clone git repository
```bash
git clone "https://github.com/Manisha-Bayya/simple-django-project.git"
```

#### 5. Install requirements
```bash
cd simple-django-project/
pip install -r requirements.txt
```

#### 6. Load sample data into MySQL
```bash
# open mysql bash
mysql -u <mysql-user> -p

# Give the absolute path of the file
mysql> source ~/grok-django-upgrade-demo/world.sql
mysql> exit;

```
#### 7. Edit project settings
```bash
# open settings file
vim grok_django_upgrade_demo/settings.py

# Edit Database configurations with your MySQL configurations.
# Search for DATABASES section.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'world',
        'USER': '<mysql-user>',
        'PASSWORD': '<mysql-password>',
        'HOST': '<mysql-host>',
        'PORT': '<mysql-port>',
    }
}

# Edit email configurations.
# Search for email configurations
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<your-email>'
EMAIL_HOST_PASSWORD = '<your-email-password>'
EMAIL_PORT = 587

# save the file
```
#### 8. Run the server
```bash
# Make migrations
python manage.py makemigrations
python manage.py migrate

# The search feature is now handled by django-watson and does not require manual indexing.

# Run the server
python manage.py runserver 0:8000

# your server is up on port 8000
```
Try opening [http://localhost:8000](http://localhost:8000) in the browser.
Now you are good to go.

### 9. URLs
#### Signup: [http://localhost:8000/signup](http://localhost:8000/signup)
#### Login: [http://localhost:8000/login](http://localhost:8000/login)
#### home for search: [http://localhost:8000/](http://localhost:8000/)
#### country page: [http://localhost:8000/country/kenya](http://localhost:8000/country/kenya)
#### Logout: [http://localhost:8000/logout](http://localhost:8000/logout)

