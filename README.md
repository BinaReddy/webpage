# Getting started

## Prerequisites

You need Python 3 and pip, as new as possible.
Virtualenvs are recommended to avoid messing up your system install of Python.

Flask is used as the 'backend' for the server.
If you plan to use this for something less experimental, it's worth [deploying it properly](https://flask.palletsprojects.com/en/2.2.x/deploying/#:~:text=Flask%20is%20a%20WSGI%20application,WSGI%20responses%20to%20HTTP%20responses.) instead of relying on ```flask run```.



## Venv setup

```bash
pip install virtualenv
cd /to/this/repo/dir
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
mkdir appimages # for storing your deployable images - or edit .env
flask run # for testing/light duty only
```



## Usage

.env file has the variables required in the application . Change these according to the usage. Create a folder 'appimages' to store the AppImages and give the location in the .env file.

You need to make an 'inventory.yaml' file in this folder before running the app. This defines what machines you have SSH access to.

Change the playbooks or paths in playbooks according to the usage.

[See the Ansible inventory documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)

Run the server with 'flask run', then use a browser to visit [localhost:5000](http://localhost:5000/).
