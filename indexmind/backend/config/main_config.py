from .db import DatabaseConfig 
from .app import AppConfig 


class Settings(DatabaseConfig, AppConfig):
    
     class Config:
         env_file=".env"