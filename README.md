# DB Testing Repo

This repo will be used for doing misc DB feature and functionality testing for the project up until we have our official app repo made.


# Python Virtual Environment

This project uses a python virtual environment to hold all required libraries. The virtual environment must be updated if you are adding libraries into the repo. 
**Tested only for Python 3.13**

## Create The Virtual Environment (first time only)

### MacOS/Unix/Linux
```python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt```
### Windows Command Prompt
```python -m venv venv && venv\Scripts\activate && pip3 install -r requirements.txt```
### Windows Power Shell
```python -m venv venv; .\venv\Scripts\Activate; pip3 install -r requirements.txt```

## Enter Your Existing Environment

### MacOS/Unix/Linux
``source venv/bin/activate``
### Windows Command Prompt
``venv/Scripts/activate``
### Windows Power Shell
``.\venv\Scripts\activate``


## Update Your Environment 
Once in the environment run: ``pip3 install -r requirements.txt``

## Change The Virtual Environment (Add/Remove Libs)
- Enter the virtual environment first
- Add / Remove libraries with pip/pip3 as you wish
- Run ```pip3 freeze > requirements.txt``` to update the requirements file

