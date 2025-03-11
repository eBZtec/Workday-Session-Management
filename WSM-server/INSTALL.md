General Environment Configuration

1 - Create the database, ensure privileges for the user 'wsm,' and make it the owner of the database.

    su - postgres
    createdb wsm_session_db
    createdb wsm_audit_db
    psql
    grant all privileges on database wsm_audit_db to wsm;
    grant all privileges on database wsm_session_db to wsm;
    ALTER DATABASE wsm_audit_db OWNER to wsm;
    ALTER DATABASE wsm_session_db OWNER to wsm;

2 - Restore the dump

    su - wsm
    psql -U wsm -d wsm_audit_db -f dump_audit_db.sql
    psql -U wsm -d wsm_session_db -f dump_session_db.sql

3 - As user 'wsm', execute:

    git clone http://gitea.ebz:3000/eBZ/Workday_Session_Management.git

4 - Create the virtual environment for the entire project in the same directory as Workday_Session_Management:

    python3.12 -m venv wsmvenv3.12

5 - For each WSM module directory, execute the library installation in the same virtual environment:

    pip install -r requirements.txt --ignore-installed
