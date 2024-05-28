# dashboard-backend

The backend of [dashboard.huyfififi.com](https://dashboard.huyfififi.com)

## System Components

Please see more details in compose.yaml (TODO: Refine/fix the compose file when I have some time)

- VPS (Amazon Lightsail)
	- Reverse Proxy Server (NGINX)
	- Backend
		- API server (Django)
		- Database (PostgreSQL)
		- Message Queue (Redis)
		- Worker/Scheduler (Celery)
	- Frontend (React)
- DNS service (Cloudflare)

## Run tests in local

```zsh
$ docker compose -f compose-test.yaml up --build
$ docker exec -it backend pytest
```

Reset test database (TODO: Check pytest option not to reuse db)

```zsh
$ docker exec -it database psql --user postgres
# DROP DATABASE test_postgres;
```
