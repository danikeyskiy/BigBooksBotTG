import os
import datetime
import yadisk
import subprocess
from dotenv import load_dotenv

load_dotenv()

DB_PASSWORD = os.getenv('PASSWORD')
DB_USER = os.getenv('USER')
DB_NAME = os.getenv('DATABASE')
DB_HOST = os.getenv('HOST')
DB_PORT = os.getenv('PORT')

async def create_backup():
    os.environ['PGPASSWORD'] = DB_PASSWORD
    os.makedirs("backups", exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join("backups", f"{DB_NAME}_backup_{timestamp}.sql")
    command = [
        'pg_dump',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER, DB_NAME,
        '-f', backup_file
    ]
    try:
        subprocess.run(command, check=True)
        
        ydisk = yadisk.YaDisk(token=os.getenv('OAUTH_TOKEN'))

        ydisk.upload(f"backups/{DB_NAME}_backup_{timestamp}.sql", f"backups/{DB_NAME}_backup_{timestamp}.sql")
    except subprocess.CalledProcessError as e:
        print(f"Error occured while creating backup: {e}")