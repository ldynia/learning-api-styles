### Title

Application framework

### Date

01.08.2023

### Status

ACCEPTED

### Context

This project uses Python, so we must select a compatible with its framework.
The framework should support the following:

- Built-in user management
- Authentication & authorization
- Have Content Management System
- Have ORM for relational database access
- Implementation of ATOM, GraphQL, REST and WebSocket APIs
- Integrate well with relational databases

The following frameworks are considered:

- Django
- FastAPI
- Flask
- Starlette
- Tornado

### Decision

#### First Choice

We will choose [Django](https://www.djangoproject.com/). The framework fits the above criteria. The leading factors for this decision are:

- Maturity of the framework
- Community size
- Large collection of packages

#### Alternative Choice

We will choose [Flask](https://flask.palletsprojects.com/en/3.0.x/) as the next best option. It is a lightweight framework that is easy to learn. The drawback is that it has fewer built-in features than Django, forcing us to rely on third-party packages for the missing features.

### Consequences

#### Positive

* It will be easy to onboard new developers. There are a lot of tutorials, and Django has good documentation.

#### Negative

* Django is not the newest framework. It might not appeal to developers who want to work with the latest technology.

#### Risks

* Django doesn't support async programming natively. This might be a problem in the future if the project decides to go async.
* Django ORM was designed for relational databases. It might be difficult to use it with schemaless databases.
* Django has a reputation for being slow. This might be a problem in the future.