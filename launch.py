"""Quick launch script for PokéBot."""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=Colors.OKGREEN):
    """Print colored text."""
    print(f"{color}{text}{Colors.ENDC}")


def print_header():
    """Print the bot header."""
    header = """
╔══════════════════════════════════════════════════════════════╗
║                          🔥 PokéBot 🔥                       ║
║              Feature-Rich Pokémon Telegram Bot              ║
║                                                              ║
║  🎯 Catch, Battle, Trade & Collect Pokémon in Telegram!     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print_colored(header, Colors.HEADER)


def check_environment():
    """Check if environment is properly set up."""
    print_colored("🔧 Checking environment...", Colors.OKBLUE)
    
    # Check if .env exists
    if not Path(".env").exists():
        print_colored("❌ .env file not found!", Colors.FAIL)
        print_colored("💡 Run: python setup.py", Colors.WARNING)
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8+ required!", Colors.FAIL)
        return False
    
    # Check requirements
    try:
        import telegram
        import motor
        import redis
        print_colored("✅ Dependencies installed", Colors.OKGREEN)
    except ImportError as e:
        print_colored(f"❌ Missing dependency: {e}", Colors.FAIL)
        print_colored("💡 Run: pip install -r requirements.txt", Colors.WARNING)
        return False
    
    return True


def show_menu():
    """Show the main menu."""
    print_colored("\n🚀 Launch Options:", Colors.OKBLUE)
    print("1. 🤖 Start Bot (Production)")
    print("2. 🛠️  Setup Database")
    print("3. 🧪 Create Test Data")
    print("4. 📊 Show Statistics")
    print("5. 🧹 Cleanup Test Data")
    print("6. 🐳 Docker Setup")
    print("7. 🧪 Run Tests")
    print("8. 📚 Show Help")
    print("9. ❌ Exit")


async def start_bot():
    """Start the bot."""
    print_colored("🚀 Starting PokéBot...", Colors.OKGREEN)
    
    try:
        # Import and run main
        from main import main
        await main()
    except KeyboardInterrupt:
        print_colored("\n🛑 Bot stopped by user", Colors.WARNING)
    except Exception as e:
        print_colored(f"❌ Error starting bot: {e}", Colors.FAIL)


def run_setup():
    """Run setup script."""
    print_colored("🔧 Running setup...", Colors.OKBLUE)
    subprocess.run([sys.executable, "setup.py"])


def create_test_data():
    """Create test data."""
    print_colored("🧪 Creating test data...", Colors.OKBLUE)
    subprocess.run([sys.executable, "dev.py", "create-test-data"])


def show_stats():
    """Show statistics."""
    print_colored("📊 Getting statistics...", Colors.OKBLUE)
    subprocess.run([sys.executable, "dev.py", "stats"])


def cleanup_test_data():
    """Cleanup test data."""
    print_colored("🧹 Cleaning up test data...", Colors.OKBLUE)
    subprocess.run([sys.executable, "dev.py", "cleanup-test-data"])


def docker_setup():
    """Setup with Docker."""
    print_colored("🐳 Docker Setup", Colors.OKBLUE)
    print("\nChoose an option:")
    print("1. Start with Docker Compose")
    print("2. Build Docker Image")
    print("3. Stop Docker Services")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print_colored("🚀 Starting with Docker Compose...", Colors.OKGREEN)
        subprocess.run(["docker-compose", "up", "-d"])
    elif choice == "2":
        print_colored("🔨 Building Docker image...", Colors.OKGREEN)
        subprocess.run(["docker", "build", "-t", "pokebot", "."])
    elif choice == "3":
        print_colored("🛑 Stopping Docker services...", Colors.WARNING)
        subprocess.run(["docker-compose", "down"])


def run_tests():
    """Run tests."""
    print_colored("🧪 Running tests...", Colors.OKBLUE)
    subprocess.run([sys.executable, "dev.py", "test"])


def show_help():
    """Show help information."""
    help_text = """
🔥 PokéBot Quick Start Guide

📋 Prerequisites:
  • Python 3.8+
  • MongoDB running on localhost:27017
  • Redis running on localhost:6379
  • Telegram Bot Token (from @BotFather)

🚀 Quick Setup:
  1. Copy .env.example to .env
  2. Edit .env with your bot token
  3. Run 'python setup.py'
  4. Start the bot!

🎮 Basic Commands (in Telegram):
  • /start - Begin your journey
  • /spawn - Spawn a Pokémon
  • /catch - Catch the spawned Pokémon
  • /pokemon - View your collection
  • /profile - Check your stats

🛠️ Development:
  • Use option 3 to create test data
  • Use option 4 to monitor statistics
  • Check DEVELOPMENT.md for detailed docs

🐳 Docker:
  • Use option 6 for containerized setup
  • Includes MongoDB and Redis automatically

📧 Need Help?
  • Check README.md
  • Read DEVELOPMENT.md
  • Review the code comments
    """
    print_colored(help_text, Colors.OKCYAN)


async def main():
    """Main launcher function."""
    print_header()
    
    if not check_environment():
        print_colored("\n❌ Environment check failed!", Colors.FAIL)
        print_colored("Please fix the issues above before continuing.", Colors.WARNING)
        return
    
    while True:
        show_menu()
        choice = input(f"\n{Colors.OKBLUE}Enter your choice (1-9): {Colors.ENDC}").strip()
        
        if choice == "1":
            await start_bot()
        elif choice == "2":
            run_setup()
        elif choice == "3":
            create_test_data()
        elif choice == "4":
            show_stats()
        elif choice == "5":
            cleanup_test_data()
        elif choice == "6":
            docker_setup()
        elif choice == "7":
            run_tests()
        elif choice == "8":
            show_help()
        elif choice == "9":
            print_colored("👋 Goodbye! Happy Pokémon training!", Colors.OKGREEN)
            break
        else:
            print_colored("❌ Invalid choice! Please try again.", Colors.FAIL)
        
        if choice != "1":  # Don't pause after starting bot
            input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n👋 Goodbye!", Colors.OKGREEN)
