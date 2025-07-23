# Rick and Morty challenge API
This is an API made as a coding challenge for a job interview.

## Running instructions

First you will need to clone the repository.
- Either download the zip from the green code button
- Or run `git clone git@github.com:PvonK/globant-challenge-API.git`

Now, to deploy the API:

### Option 1: Deploy with Docker (recommended)

To deploy the API with docker, first make sure you have docker installed.

1. Run the following command: `docker`

> If the previous command returned usage instructions and no errors, you can continue. If you don't have docker installed you'll need to install it to continue.

2. In the project directory run: `docker build . -t rick-and-morty-api`
3. Then, run the command: `docker run -p 5000:5000 rick-and-morty-api:latest`

> Important: if you have changed the PORT variable on the .env file you have to add `--env-file .env` to the previous command and change the "5000" for the port value you have set.

4. Done! Now the project is running on localhost, port 5000.


### Option 2: Deploy with Make (one command) (on linux systems)
To deploy the API with make, first make sure you have "make" installed.

1. Run the following command: `make -h`

> If the previous command returned usage instructions and no errors, you can continue. If you don't have make installed you'll need to install it to continue.

2. In the project directory run `make`
3. Done! Now the project is running on localhost, port 5000



### Option 3: Deploy with no containers (not recommended)

To run the API locally without docker you need to first install all the dependencies. It is recommended that you install them on a virtual environment.

1. To create a virtual environment run: `python -m venv venv`
2. To activate the virtual environment run: `source venv/bin/activate` 
3. Install the dependencies with: `pip install -r requirements.txt`
4. Start the API server with: `python -m flask --app run run`
5. Done! Now the project is running on localhost, port 5000

---

## Technical info: RickAndMortyAPI


### Available endpoints:

`GET /characters`

- Response: 
    ```json
    {
        "character_names": [],
        "human_count": 0,
        "not_human_count": 0,
        "dead_count": 0,
        "alive_count": 0
    }

    ```


`GET /location?name=earth&type=planet`

- Response:
    ```json
    {
        "name": "",
        "type": ""
    }
    ```
