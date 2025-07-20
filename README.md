Technical test: RickAndMortyAPI
Goal: Create a Rick and Morty data API.

General rules:

    - [ ] Commit your changes to a public repository in GitHub.
    - [ ] Add a README.md with instructions to run the code.
    - [ ] Support the following endpoints:


- [ ] `GET /characters`

    Response: 
    ```json
    {
        "character_names": [],
        "human_count": 0,
        "not_human_count": 0,
        "dead_count": 0,
        "alive_count": 0
    }

    ```


- [ ] `GET /location?name=earth&type=planet`

    Response:
    ```json
    {
        "name": "",
        "type": ""
    }
    ```


These endpoints should consume an external API to get the proper info, here is the documentation page: https://rickandmortyapi.com/documentation/

    - [ ] The data must be human-readable.
    - [ ] Use environment variables for configuration.
    - [ ] The response must include the content-type header (application/json)
    - [ ] Functions must be tested.


For extra points:

    - [ ] Create custom exceptions to contemplate possible errors when these endpoints are consumed.
    - [ ] Dockerize the project
