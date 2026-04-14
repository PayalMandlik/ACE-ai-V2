import asyncio
import os
from typing import Any, Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from backend.core.db_schema import COLLECTION_VALIDATORS, INDEX_DEFINITIONS


async def _ensure_collection_schema(db, name: str, validator: Dict[str, Any]) -> None:
    existing_collections = await db.list_collection_names()
    if name not in existing_collections:
        await db.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
        print(f"Created collection '{name}' with strict schema validation.")
        return

    await db.command(
        {
            "collMod": name,
            "validator": validator,
            "validationLevel": "moderate",
            "validationAction": "error",
        }
    )
    print(f"Updated schema validation for existing collection '{name}' (moderate level).")


async def _create_indexes(db) -> None:
    for collection_name, indexes in INDEX_DEFINITIONS.items():
        for index in indexes:
            keys = index["keys"]
            options = index.get("options", {})
            await db[collection_name].create_index(keys, **options)
            print(f"Ensured index on {collection_name}: {keys}, options={options}")


async def main():
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "ace_ai")

    print(f"Connecting to {uri}, database: {db_name}")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    print("Ensuring schema validators and indexes for all production collections...")
    for collection_name, validator in COLLECTION_VALIDATORS.items():
        try:
            _ensure_collection_schema(db, collection_name, validator)
        except Exception as exc:
            print(f"Failed to ensure schema for collection '{collection_name}': {exc}")

    print("Ensuring indexes and TTL settings...")
    try:
        _create_indexes(db)
    except Exception as exc:
        print(f"Failed to create indexes: {exc}")

    print("MongoDB schema and index setup complete.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
