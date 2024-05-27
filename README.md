# dashboard-backend

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
