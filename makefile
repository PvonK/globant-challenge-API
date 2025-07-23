build:
	docker build . -t rick-and-morty-api
	docker run -p 5000:5000 --env-file .env rick-and-morty-api:latest
