# User Manager
Microservice for players authentication and authorization logic


## How to run locally \*:
1. Make sure you have installed Python 3.6, pip and virtualenv.  

2. Create new virtualenv using \**:  
```sh
mkvirtualenv <virtual_env_name> -p <full_path_to_python>
``` 
where:
  - `<virtual_env_name>` is the name of the new virtualenv  
  - `<full_path_to_python>` is the full path to Python 3.6

3. Activate the virtualenv by:  
```sh
source <virtual_env_name>/bin/activate
```

4. Install the requirements for this microservice:  
```sh
pip install -r requirements.txt
```

5. Run the server locally:  
```sh
python manage.py runserver <port>
```  



\* All described commands are true for Linux terminal. For Windows and OS X are almost the same.
\** Run this command outside of this git repo 
