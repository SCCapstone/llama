# ColdCall (llama)

This first paragraph should be a short description of the app. You can add links
to your wiki pages that have more detailed descriptions.

Your audience for the Readme.md are other developers who are joining your team.
Specifically, the file should contain detailed instructions that any developer
can follow to install, compile, run, and test your project. These are not only
useful to new developers, but also to you when you have to re-install everything
because your old laptop crashed. Also, the teachers of this class will be
following your instructions.

## External Requirements

In order to build this project you first have to install:

- [Python 3.13.0](https://www.python.org/downloads/release/python-3130/)
- [Django 5.1.2](https://www.djangoproject.com/download/)
```pip install Django==5.1.2```

In order to deploy this project, you need [Gunicorn](https://gunicorn.org/). (UNIX only)
```pip install gunicorn```

## Setup

Here you list all the one-time things the developer needs to do after cloning
your repo. Sometimes there is no need for this section, but some apps require
some first-time configuration from the developer, for example: setting up a
database for running your webapp locally.

## Running

1. Clone the repo. ```https://github.com/SCCapstone/llama.git```
2. Create a `.env` file with the following:
```
SECRET_KEY=<put key here>
DEBUG=TRUE
```
3. Initialize the database through ```python manage.py migrate```
4. Run the server through `python manage.py runserver`
# Deployment

1. Follow the prior steps to initialize the server.
2. Edit the .env to set `DEBUG=FALSE`.
3. Run `gunicorn llama.wsgi`

# Testing

In 492 you will write automated tests. When you do you will need to add a
section that explains how to run them.

The unit tests are in `/test/unit`.

The behavioral tests are in `/test/casper/`.

## Testing Technology

In some cases you need to install test runners, etc. Explain how.

## Running Tests

Explain how to run the automated tests.

# Authors

Ankit Nath <ankitnath2004@gmail.com> (<anath@email.sc.edu>)
Cade Stocker <cstocker@email.sc.edu>
Colin Richard <colincr@email.sc.edu>
Thomas Kareka <tkareka@email.sc.edu>
Trevor Seestedt <seestedt@email.sc.edu>

# Coding Style 
The following link provides the style of coding that will be used for the project. 
https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/