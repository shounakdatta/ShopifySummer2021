from distutils.core import setup

setup(
    name="shopify_winter_2021",
    version="0.0.1",
    install_requires=[
        "Flask >= 1.1.2",
        "autopep8 >= 1.5.4",
        "flake8 >= 3.8.3",
        "pytest >= 6.0.1",
        "python-dotenv >= 0.15.0",
        "gunicorn >= 20.0.4",
        "psycopg2 >= 2.8.6",
    ]
)
