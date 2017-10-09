## Get start
**!! Using `python3.6` or later version.**
```bash
$> git clone [this project]
$> # replace appname with your application name
$> make rename
```

## Commands
There are 2 scripts in this project directory. `Makefile` and `manage.py`.
Open your terminal to check its capabilities.
```bash
make
```
or
```
python manage.py`
```

## Database Migration
```bash
$ # do it only if no `migrations` folder under your project folder
$ python manage.py db init
$ # do it every time before submitting changes of models
$ python manage.py db migrate
$ # do it so database is upgraded with your changes of models
$ python manage.py db upgrade
$ python manage.py db --help
```

## Configuration & Environment
```bash
$ export SQLALCHEMY_DATABASE_URI='mysql+pymysql://[usr:pwd]@localhost:32768/enmon?charset=utf8'
$ # [usr:pwd] are placehoder of database user and password
```

## Localization
```bash
$ python manage.py babel
$ update
$ # edit translations/zh/messages.po, then
$ python manage.py babel
$ compile
```
