# In The Bank
Here are the steps to get this app running locally.

### Clone the repository

####  Generate a new secret key

I like using [Djecrety](https://djecrety.ir/) to quickly generate secure secret keys.

```
vim inthebank/SECRET_KEY
export SECRET_KEY='<secret_keys>'
```

#### Run using docker:

```
$ docker-compose up
 ```

or to run without docker: 

#### Create your own virtual environment
```
$ cd inthebank/
$ python3 -m venv env
$ source env/bin/activate
```
Virtual environments are where dependencies are stored, similar to node_modules in JavaScript. Every time you start your machine, you must activate the virtual environment using source venv/bin/activate.

#### Install your requirements
```
$ pip install -r requirements.txt
```

#### Create a new superuser
```
$ python manage.py createsuperuser
```

#### Final checks
Start the development server and ensure everything is running without errors.

```
$ python manage.py runserver
```