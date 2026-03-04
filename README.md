# Task_Tracker_API

API to allow users to manage their to-do list. 

Provides user registration, login, and authentication through JWT tokens. CRUD operations for tasks. Users and tasks stored in a PostgreSQL database interfaced with through psycopg2. 

Built with Flask and psycopg2. Additional libraries such as Argon2, PyJWT, jsonschema used for user authentication, data validation, etc. 

Future additions: 
 - Redis cache for revoked tokens 
 - Move some logic into separate directories and files. For example a directory for routes and separate files for user and todo list functions. 
 - Change encryption scheme to RS256



From: https://roadmap.sh/projects/todo-list-api 
