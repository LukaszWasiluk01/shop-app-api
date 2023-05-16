# shop-app-api

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Local Development
Create .env file based on .env.sample.
Start the dev server for local development:
```bash
docker-compose up
```

Run a command inside the docker container:

```bash
docker-compose run --rm app sh -c "[command]"
```