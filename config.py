from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import motor.motor_asyncio
import os


# ----------------- Database variables (MongoDB) --------------------------
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["DB_URL"])
db = client.myTestDB
