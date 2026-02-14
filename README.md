# Campus Marketplace – Backend

## Team

> 1. Kaden Leis
> 2. Quincy Cole
> 3. Mitch Dorbor
> 4. Amin Taha

## What You Need Installed

- Everyone must install:

1. Python 3.11+
2. PostgreSQL
3. pgAdmin

## Install PostgreSQL + pgAdmin

- Download here:
  `https://www.postgresql.org/download/`

## During setup:

- Username: `postgres`
- Password: `postgres`
- Port: `5432` (default)

## After install:

1. Open pgAdmin
2. Create a database:
3. Right click Databases
4. Click Create → Database
5. Name it: `campus_marketplace`
6. Click Save.

## Backend Setup

### Create Virtual Environment

> Windows
>
> ````powershell py -m venv .venv
> .\.venv\Scripts\Activate.ps1```
> ````

> Mac / Linux
>
> ````bash python3 -m venv .venv
> source .venv/bin/activate```
> ````

- You should now see: `(.venv)`

1. Install Dependencies: `pip install -r requirements.txt`
2. Create .env file
3. Inside backend/, create a file called: `.env`

Add:

```DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/campus_marketplace
FRONTEND_ORIGIN=http://localhost:3000
```

## Run Backend

- uvicorn app.main:app --reload

1. Open:
2. `http://localhost:8000/docs`
3. If Swagger loads, you’re good. If you run into **any** issues, pleas let Kaden know.
