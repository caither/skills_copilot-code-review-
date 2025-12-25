"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from backend.config import create_app, ProductionDatabaseInit
from backend import database

# Create and configure the application using production initialization strategy
app = create_app(ProductionDatabaseInit(database))

