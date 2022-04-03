# Stack Exchange Data ETL
## Purpose of this Project
An anonymized dump of some of Stats Stack Exchange network for the year 2009-2014 is available at https://relational.fit.cvut.cz/dataset/Stats 
within the database call `stats`. However, the database is not as cleaned and prepared as desired; therefore, this project is created to provide
an application to extract the data, perform transformations into the desired schema, then load to a destination database.

This project is part of database preparation for a course work of subject **2190436 Data Warehousing** being taught in Chulalongkorn University. The libraries 
mainly used are **SQLAlchemy ORM** for table creations, and **PySpark** for ETL processes.

## Data Movement
The original `stats` database is residing in a **MariaDB** database, which when connected is relatively slow to query, making data exploration relatively
troublesome. Consequently, the data is first replicated to a local **Postgres** database. As for the final destination, the cleaned and prepared data will land 
in a database residing in **Azure SQL Server**. In addition, another database will be created in **Azure SQL Server** to be used as the location for data
warehouse.

The mentioned tasks are done by the following modules:
  - `src/maria_to_postgres.py` = Replicate data from **MariaDB** to **Postgres**.
  - `src/data_preparation.py` = Perform transformation on the data before loading them to **Azure SQL Server**.
  - `src/warehouse_creation` = Create tables in the data warehouse residing in **Azure SQL Server**.

## Changes Made to Source Database
The following changes are made to the source database before loading to the final database:
  - Change all table and column names to snake case to eliminate the concern if a database system is case sensitive or insensitive; moreover, it simplifies
    writing queries, such as using `SELECT post_id, owner_user_id FROM posts` as opposed to `SELECT "Id", "PostTypeId" FROM posts` where user must add `""`.
  - Add tables to show the description of the different entity types, for example `post_types`.
  - Make the relationship between certain tables clearer, for example adding `posts_tags` table to show relationship between `posts` and `tags` tables.
  - Add timezone to the datetime types (this project assumes the souce database has the time saved as UTC time).

The following diagrams show the difference between the original schema and final schema:

### Original `stats` Schema
![Original `stats` schema](/assets/orig_schema.png)

### Final `stats` Schema
![Final `stats` schema](/assets/stats_schema.png)

## Installation
This project requires [***poetry***](https://python-poetry.org/) and [***Python 3.8.x***](https://www.python.org/) installed in the machine.
  1. Clone this git repository.
  2. Change the working directory to the root of the repository.
  3. Run the command `poetry install` in the terminal.

## Configurations
This project expects the following environment variables to be present in the machine.
  - `POSTGRES_HOSTNAME` = \<hostname to local Postgres\>
  - `POSTGRES_PORT` = \<port to the local Postgres\>
  - `POSTGRES_USER` = \<user to connect to the Postgres database\>
  - `POSTGRES_PASSWORD` = \<password to authenticate the user to connect to Postgres\>
  - `POSTGRES_DATABASE` = \<database to replicate the data to in Postgres\>
  - `MSSQL_HOSTNAME` = \<Azure SQL Server hostname\>
  - `MSSQL_PORT` = \<port to connect to Azure SQL Server\>
  - `MSSQL_USER` = \<user to connect to Azure SQL Server\>
  - `MSSQL_PASSWORD` = \<password to authenticate the user to connect to Azure SQL Server\>
  - `MSSQL_DATABASE` = \<database to load the data to in Azure SQL Server\>
  - `MSSQL_WAREHOUSE_DATABASE` = \<database to create the warehouse tables in Azure SQL Server\>
 
 If you do not wish to change your system environment variables, you can create a `.env` file at the root of repository and use 
 [`python-dotenv`](https://github.com/theskumar/python-dotenv) to load the environment variables.
 
 ## Running the Application
 - Run the application to replicate data from **MariaDB** to **Postgres** using command `make replicate_data` in terminal
 - Run the application to transform and load data from **Postgres** to **Azure SQL Server** using command `make load_data` in terminal
 - Run the application to create tables in the data warehouse that is hosted on **Azure SQL Server** using command `make create_warehouse_tables` in terminal
