# How to install the website:

- Open cmd

- Change directory to where you installed the repository : `cd [YOUR PATH HERE]`

- Create a venv by typing: `python -m venv .venv`

- Activate your venv with `.venv\Scripts\activate`

- Install the dependencies with `pip install -r requirements.txt`

- Create the database with `python createdb.py` (if you already have a file named `slowrun.db`, manually delete it first in order to refresh it)

- Finally, to run the website, type `flask --app slowrun run`
