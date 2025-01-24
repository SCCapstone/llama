# ColdCall (llama)

The ColdCall application is a Django-based platform that is designed to assist professors 
by providing an effective interface for tracking student metrics, attendances, and 
engagement in the classroom. Professors have the ability to organize multiple classes of 
students, log attendance and performances, and randomize student selection for 
interactive participation. This application will be structured with a multi-page interface 
allowing users to edit/add students and import/export class data. 

## External Requirements

In order to build this project you first have to install:

- [Python 3.13.0](https://www.python.org/downloads/release/python-3130/)
- [Django 5.1.2](https://www.djangoproject.com/download/)
```pip install Django==5.1.2```

In order to deploy this project, you need [Gunicorn](https://gunicorn.org/). (UNIX only)
```pip install gunicorn```

## Setup

## Running

1. Clone the repo. ```https://github.com/SCCapstone/llama.git```
2. Create a `.env` file with the following:
```
SECRET_KEY=<put key here>
DEBUG=TRUE
```
3. Install the dependencies through ```pip install -r requirements.txt```
4. Initialize the database through ```python manage.py migrate```
5. Run the server through `python manage.py runserver`
# Deployment

1. Follow the prior steps to initialize the server.
2. Install Gunicorn ```pip install gunicorn```
3. Create the static directory thorugh ```python manage.py collectstatic```
4. Edit the .env to set `DEBUG=FALSE`.
5. Run `gunicorn llama.wsgi`

Additional configuration may be required depending on operating system setup. For this, we connected Gunicorn to [nginx](https://nginx.org/en/).

The current dev server is deployed at http://132.145.167.159/.

# Testing

The unit tests are located in  `/coldcall/tests/`.

The behavioral tests are in `coldcall/selenium_tests/`.

The test environment settings are located in `/llama/test_settings.py/`



## Testing Technology

In some cases you need to install test runners, etc. Explain how.

## Running Tests

To run unit tests, use `python manage.py test coldcall/tests/ --settings=llama.test_settings`.

To run behavioral tests, use `python manage.py test coldcall/selenium_tests/ --settings=llama.test_settings` (each test will take roughly 5 seconds)

To run all tests, use `python manage.py test --settings=llama.test_settings`

# Authors

Ankit Nath <ankitnath2004@gmail.com> (<anath@email.sc.edu>) <br>
Cade Stocker <cstocker@email.sc.edu> <br>
Colin Richard <colincr@email.sc.edu> <br>
Thomas Kareka <tkareka@email.sc.edu> <br>
Trevor Seestedt <seestedt@email.sc.edu> <br>

# Coding Style 
The following link provides the style of coding that will be used for the project. 
https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
