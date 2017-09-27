# GridIX.Web API

GridIX.Web exposes a RESTful API for accessing and managing target resources for the application. The url path for the API root is `/api/v?/` where _**?**_ is the API version number. Thus the complete HTTP url (for the API root) for host `gridix.example.ng` would be `http://gridix.example.ng/api/v?/`.


## Authentication

Access to the API is secured using JSON Web Tokens (JWT). All resource paths via the API require authenticated access except for the root url path at `/api/v?/` which exposes available endpoints on the API.

Authenticate to obtain a valid token by making a POST request to `/api/v?/auth/` with json data having `username` and `password` (object) members which contain the login credentials. 

The default admin login credentials are as follows:

	username: manager
	password: gridix


A raw sample HTTP post request for authentication using the credentials above is given below:

    POST /api/v?/auth/ HTTP/1.1
    Host: gridix.example.ng
    Cache-Control: no-cache

    {
        "username": "manager", 
        "password": "gridix"
    }

The response for a well-formed request returns json data with `result` and `token` (object) members. The `result` carries `OK` if the supplied credentials are valid and `token` carries the token to use for subsequent request. Should the credentials be invalid, the returned json data contains only the `result` with value `error: invalid username and/or password`.


## Managing Users

Users can be managed from the command line using the `manage_gridix_user` command. Available subcommands (termed task) are `list`, `add`, `del`, `change_passwd`.



## Making Request

The token gotten after a successful authentication must be supplied as a Authorization HTTP Header type for JWT for every single request. A sample GET request for all voltages is show below:

    GET /api/v?/voltages/
    HOST: gridix.example.ng
    Authorization: JWT <retrieved-token-goes-here>


## API Endpoints
The table below itemizes resources for which an API endpoint exists for access and management.

Resource      | Key      | Url
--------------|----------|----
Organisations | orgs     | `http://gridix.example.ng/api/v?/orgs/`
Voltages      | voltages | `http://gridix.example.ng/api/v?/voltages/`
Electric Lines    | electric_lines    | `http://gridix.example.ng/api/v?/electric_lines/`
Electric Stations | electric_stations | `http://gridix.example.ng/api/v?/electric_stations/`


## Data Pagination

Data returned at the API endpoits can be paged using `page` and `pageSize` within the query string. The sample url below shows how to access page **5** for items collected at a page size of **10** items.

    http://gridix.example.ng/api/v?/electric_lines?pageSize=10&page=5


## Data Filtering

The API endpoints also support data filtering via url query string entries. For each resource type, only select fields are available for use for filtering and these are provided in the table below.

**Common Fields**
uuid, dateUpdated


Resource       | Available Fields
---------------|-----------------
Organisations  | description, fncode, identifier, name, parentId, dateEstablished
Voltages       | value
Electric Lines | name, owner, lineCode, registerCode, subType *[feeder=1, upriser=2]*, voltageId, sourceStationId, dateCommissioned
Electric Stations | name, owner, isPublic, isManned, isAutomated, facilityCode, registerCode, subType *[transmission=1, injection=2, distribution=3]*, organisationId, dateInstalled, sourceLineId 



# GridIX.Web CLI Commands

GridIX.Web at the moment barely exposes any UI other than for login and import. Management tasks have to be performed using the command-line interface (CLI). Available commands are described below:


### initialize_gridix_db

This creates the database schema for tables and relationships that is required for operating GridIX.Web. To run the command:

    $ initialize_gridix_db <config_uri>
    # example: initialize_gridix_db development.ini
    
    
### import_gridix_data

This imports data into the GridIX database from a specified Microsoft Excel document formated in a way as expected by the import engine. To run the command:

	$ import_gridix_data <config_uri> [file=filepath-to-excel-file]
    # example: import_gridix_data development.ini file=</path/to/excel-file.xlsx>
    

### manage_gridix_user

This helps manage users for GridIX.Web. It supports listing, adding, deleting users as well as changing user password. To run the command:

	$ manage_gridix_user <config_uri> task=(list|add|del|change_passwd) [username=...] [role=...] [password=...] [oldpassword=...]
    ## examples:
    # manage_gridix_user development.ini task=list
    # manage_gridix_user development.ini task=add username=... password=...
    # manage_gridix_user development.ini task=del username=...
    # manage_gridix_user development.ini task=change_passwd username=... oldpassword=... password=...