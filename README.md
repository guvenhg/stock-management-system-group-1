# Stock Management System

CMPE341 Database Design and Management course project.

A small web application to follow the stock of a company: products, categories,
suppliers, warehouses and the stock movements (IN / OUT) of every product.

- **Database:** PostgreSQL 16
- **Web application:** Python (Flask)
- **Runs with:** Docker Compose

## How to run

You only need Docker. After cloning the repository, run this command in the
project folder:

```bash
docker compose up
```

This single command starts the PostgreSQL database (the tables and the sample
data are created automatically) and the web application.

Then open this address in a browser:

**http://localhost**

If port 80 is already used on your computer, choose another port:

```bash
APP_PORT=8080 docker compose up
```

and open http://localhost:8080 instead.

## Test users

| Role                 | Username | Password   | What the role can do                                                        |
|----------------------|----------|------------|-----------------------------------------------------------------------------|
| Admin                | `admin`  | `admin123` | Everything: insert, update and delete all records, manage users             |
| Standard user        | `user`   | `user123`  | See all lists and the current stock, record new stock movements             |

Passwords are stored hashed in the database (PBKDF2-SHA256), never as plain text.

## Project files

| File / folder         | Content                                                    |
|-----------------------|------------------------------------------------------------|
| `db/01_schema.sql`    | `CREATE TABLE` statements with the constraints             |
| `db/02_seed.sql`      | Sample data                                                |
| `db/03_queries.sql`   | The example queries of the report (join, group by, subquery) |
| `app.py`              | The Flask web application                                  |
| `templates/`, `static/` | HTML pages and the style sheet                           |
| `Dockerfile`          | Image of the web application                               |
| `docker-compose.yml`  | Starts the database and the web application together       |

## Resetting the database

The sample data is loaded only the first time the database is created. To start
again with a clean database:

```bash
docker compose down -v
docker compose up
```
