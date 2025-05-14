from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb+srv://personalprojects123400:personalprojects786@cluster0.gamusij.mongodb.net/securefileshare2?retryWrites=true&w=majority&appName=Cluster0")
MongoClient = client["securefileshare2"]