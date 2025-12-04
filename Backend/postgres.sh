#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Now you can use the environment variables
echo "Postgres User: $POSTGRES_USER"
echo "Postgres Password: $POSTGRES_PASSWORD"
echo "Postgres Database: $POSTGRES_DB"

# Example of using the variables to reset the PostgreSQL password
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"

psql -u postgres psql < database.sql


exit