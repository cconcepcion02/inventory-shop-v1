# System Architecture
Frontend and Backend are separate deployments.

frontend/
- Angular
- Angular Material
- JWT Authentication

backend/
- FastAPI
- SQLAlchemy
- PostgreSQL

Communication:
Frontend -> REST API -> Backend -> PostgreSQL
