# Post Installation
To create the database structure for GridIX enter command below:

    $ initialize_gridix_db <development.ini>


To populate database with data already entered into excel file in the appropriate 
format enter the command below:

    $ import_gridix_data <development.ini> file=</path/to/data.xlxs>


# Run Application
To run the application issue the command below:

    $ pserve <development.ini> [--reload]
