Requirements:
-------------

* Python >= 2.7.3 (NOT Python 3)
* virtualenv
* pip


Steps:
------

* Setup the virtual environment.
```virtualenv chowk_env```

* Activate it
```./chowk_env/bin/activate```

* Install all required libraries inside it
```pip install -r requirements.txt```

* Put your Kannel & RapidPro server details inside settings.py.example 
and rename it
```
vim settings.py.example
mv setings.py.example settings.py
```

* Start celery (Preferably in a screen or a seperate terminal so that this process doesn't die when you logout)
```celery worker -A tasks.celery --loglevel=DEBUG```

* Run the main app! (Preferably in a screen or a seperate terminal so that this process doesn't die when you logout)
```python chowk.py```

Troubleshooting:
----------------
chowk produces 2 log files.

error.log -- for messages of ERROR and CRITICAL levels
debug.log -- for messages of DEBUG, INFO and WARNING levels

You can change this from inside chowk.py

Still facing issues ?
---------------------
File an issue here and I will try my best to help :)

