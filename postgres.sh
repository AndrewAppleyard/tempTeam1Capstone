#!/bin/bash

# install postgresql
sudo zypper in postgresql postgresql-server postgresql-contrib

sudo zypper in postgresql-plperl postgresql-plpython postgresql-pltcl

sudo systemctl enable postgresql

sudo systemctl start postgresql

# update postgres user password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'us3URownP4\$sword8410';"

# change peer and ident auth to md5 for local and host
sudo sed -i -E '/^(local|host)[[:space:]]/s/(peer|ident|trust)/md5/g' /var/lib/pgsql/data/pg_hba.conf

sudo systemctl reload postgresql 

sudo systemctl restart postgresql 

# run database sql (assuming the directories arent changed)
sudo -u postgres psql < database.sql

exit
