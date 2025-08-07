"""Development tools and utilities."""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def create_test_data():
    """Create test data for development."""
    print("🧪 Creating test data...")
    
    try:
        from config.database import db
        from bot.services.user_service import user_service
        from bot.services.pokemon_service import pokemon_service
        
        await db.connect()
        
        # Create test user
        test_user = await user_service.get_or_create_user(
            user_id=999999999,
            username="testtrainer",
            first_name="Test",
            last_name="Trainer"
        )
        
        print(f"✅ Created test user: {test_user.user_id}")
        
        # Give test user some Pokémon
        starter_pokemon = [1, 4, 7]  # Bulbasaur, Charmander, Squirtle
        
        for species_id in starter_pokemon:
            pokemon = await pokemon_service.create_pokemon(
                owner_id=test_user.user_id,
                species_id=species_id,
                level=5
            )
            if pokemon:
                print(f"✅ Created {pokemon.species} for test user")
        
        # Add some coins
        await user_service.add_coins(test_user.user_id, 5000)
        print("✅ Added 5000 coins to test user")
        
        await db.disconnect()
        print("🎉 Test data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")


async def cleanup_test_data():
    """Clean up test data."""
    print("🧹 Cleaning up test data...")
    
    try:
        from config.database import db
        
        await db.connect()
        
        # Remove test user and their Pokémon
        await db.db.users.delete_many({"user_id": 999999999})
        await db.db.pokemon.delete_many({"owner_id": 999999999})
        await db.db.pokemon.delete_many({"owner_id": -1})  # AI Pokémon
        
        print("✅ Test data cleaned up")
        await db.disconnect()
        
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")


async def reset_database():
    """Reset the entire database (DANGEROUS!)."""
    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != "YES":
        print("❌ Operation cancelled")
        return
    
    try:
        from config.database import db
        
        await db.connect()
        
        # Drop all collections
        collections = await db.db.list_collection_names()
        for collection in collections:
            await db.db.drop_collection(collection)
        
        # Recreate indexes
        await db.create_indexes()
        
        print("✅ Database reset complete")
        await db.disconnect()
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")


async def show_stats():
    """Show development statistics."""
    print("📊 Development Statistics")
    print("=" * 30)
    
    try:
        from config.database import db
        
        await db.connect()
        
        # Count documents
        user_count = await db.db.users.count_documents({})
        pokemon_count = await db.db.pokemon.count_documents({})
        spawn_count = await db.db.spawns.count_documents({})
        battle_count = await db.db.battles.count_documents({})
        
        print(f"Users: {user_count}")
        print(f"Pokémon: {pokemon_count}")
        print(f"Spawns: {spawn_count}")
        print(f"Battles: {battle_count}")
        
        # Show recent activity
        print("\n🔥 Recent Spawns:")
        recent_spawns = await db.db.spawns.find().sort("spawned_at", -1).limit(5).to_list(5)
        for spawn in recent_spawns:
            status = "✅ Caught" if spawn.get('is_caught') else "🔍 Available"
            print(f"  • {spawn['species'].title()} (Level {spawn['level']}) - {status}")
        
        await db.disconnect()
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")


async def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "-v", "--tb=short"
        ], cwd=project_root)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")


def main():
    """Main development script."""
    parser = argparse.ArgumentParser(description="PokéBot Development Tools")
    
    parser.add_argument("command", choices=[
        "create-test-data",
        "cleanup-test-data", 
        "reset-database",
        "stats",
        "test"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "create-test-data":
        asyncio.run(create_test_data())
    elif args.command == "cleanup-test-data":
        asyncio.run(cleanup_test_data())
    elif args.command == "reset-database":
        asyncio.run(reset_database())
    elif args.command == "stats":
        asyncio.run(show_stats())
    elif args.command == "test":
        asyncio.run(run_tests())


if __name__ == "__main__":
    main()
