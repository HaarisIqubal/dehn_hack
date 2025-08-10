from dotenv import load_dotenv
import os

class LoadENV:

    def __init__(self) -> None:
        self.load_env_files()
        
    def load_env_files(self):
        """Load environment files with priority: .env.local first, then .env"""
        if os.path.exists('.env.local'):
            load_dotenv('.env.local')
            print("Loaded .env.local file")
        elif os.path.exists('.env'):
            load_dotenv('.env')
            print("Loaded .env file")
        else:
            print("No environment file found")