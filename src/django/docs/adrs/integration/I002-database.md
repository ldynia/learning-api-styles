### Title

Database

### Date

02.08.2023

### Status

ACCEPTED

### Context

The application needs to store data in a relational database. Therefore, we need to choose a database that will be used in the project. The following candidates are considered:

- MariaDB
- MySQL
- PostgreSQL
- SQLite

### Decision

We will use PostgreSQL as the main database. The leading factors for this decision were:

* It integrates well with Django ORM.
* PostgreSQL is free and open source.
* PostgreSQL has extensive documentation and a big community.
* PostgreSQL supports various data types: JSON and JSONB data types.
* PostgreSQL offers full-text search.
* PostgreSQL offers advanced GIS features.

### Consequences

#### Positive

It's easy to transition from other SQL databases to PostgreSQL. The database has its image on the docker hub.

#### Risks

The database has its own license - PostgreSQL Database Management System. It might be a problem if the project decides to change it.