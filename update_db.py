import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def main():
    # Load env for URI
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "ace_ai")

    print(f"Connecting to {uri}, database: {db_name}")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    # 1. MIGRATION: Add default values to existing documents to prevent validation issues
    print("Running migration to add missing fields to existing documents...")
    now = datetime.utcnow()
    
    # We update documents that might be missing the required fields
    result = await db.resumes.update_many(
        {
            "$or": [
                {"user_id": {"$exists": False}},
                {"resume_text": {"$exists": False}},
                {"created_at": {"$exists": False}},
                {"updated_at": {"$exists": False}},
            ]
        },
        [
            {
                "$set": {
                    "user_id": {"$ifNull": ["$user_id", "default_user"]},
                    "resume_text": {"$ifNull": ["$resume_text", {"$ifNull": ["$raw_text", ""]}]},
                    "created_at": {"$ifNull": ["$created_at", now]},
                    "updated_at": {"$ifNull": ["$updated_at", now]}
                }
            }
        ]
    )
    print(f"Migration complete! Modified {result.modified_count} existing documents.")

    # 2. SCHEMA UPDATE: Apply schema validation using collMod with validationLevel: "moderate"
    print("Applying schema validation (collMod)...")
    
    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "resume_text", "analysis", "created_at", "updated_at"],
            "properties": {
                "user_id": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "resume_text": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "analysis": {
                    "bsonType": ["string", "object"],
                    "description": "must be a string or object and is required"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                }
            }
        }
    }

    try:
        await db.command({
            "collMod": "resumes",
            "validator": schema,
            "validationLevel": "moderate",
            "validationAction": "error"
        })
        print("Schema validation successfully updated!")
    except Exception as e:
        if "ns does not exist" in str(e):
            print("Collection 'resumes' doesn't exist yet, creating it with the schema...")
            await db.create_collection("resumes", validator=schema, validationLevel="moderate")
            print("Collection created with schema validation!")
        else:
            print(f"Error updating schema: {e}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
