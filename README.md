# Prerequisites:

- Python version 3.11 or higher

- Access to a CLI like cmd for Windows or shell for Linux

# How to install the website:

- Open your CLI

- Change directory to where you installed the repository : `cd [YOUR PATH HERE]`

- Create a venv by typing: `python -m venv .venv`

- Activate your venv with `.venv\Scripts\activate`

- Install the dependencies inside your venv with `pip install -r requirements.txt`

- Create or reset the database with `python createdb.py`
> The database will come with pre-registered games and categories so you can experiment with it

- Finally, to run the website, type `flask --app slowrun run`
