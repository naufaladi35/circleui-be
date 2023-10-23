import motor.motor_asyncio
import certifi, cloudinary, os
from dotenv import load_dotenv

load_dotenv()
ca = certifi.where()

def connect():
    cloudinary.config( 
        cloud_name = os.environ['CLOUDINARY_CLOUD_NAME'],
        api_key = os.environ['CLOUDINARY_API_KEY'],
        api_secret = os.environ['CLOUDINARY_API_SECRET'],
        secure = True
    )
    MONGODB_URL = os.environ['DEV_MONGODB_URL']
    DB_NAME = os.environ['DEV_DB_NAME']
    
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS = 5000, tlsCAFile = ca)

    try:
        return client[DB_NAME]
    except Exception:
        print("Unable to connect to the server")
        