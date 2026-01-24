"""
Alembic Database Migration Helper
Usage:
    python alembic_helper.py history        # Show migration history
    python alembic_helper.py upgrade        # Apply migrations
    python alembic_helper.py downgrade      # Rollback one migration
    python alembic_helper.py generate <msg> # Generate new migration
"""
import sys
import subprocess

def run_command(cmd):
    """Execute alembic command"""
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0

def show_history():
    """Show migration history"""
    print("=" * 60)
    print("Database Migration History")
    print("=" * 60)
    print()
    print("Current version:")
    run_command(".venv\\Scripts\\alembic.exe current")
    print()
    print("Migration history:")
    run_command(".venv\\Scripts\\alembic.exe history --verbose")

def apply_migrations():
    """Apply all pending migrations"""
    print("=" * 60)
    print("Apply Database Migrations")
    print("=" * 60)
    print()
    print("Current version:")
    run_command(".venv\\Scripts\\alembic.exe current")
    print()
    print("Applying migrations...")
    success = run_command(".venv\\Scripts\\alembic.exe upgrade head")
    print()
    if success:
        print("SUCCESS: Migrations applied successfully!")
        print()
        print("New version:")
        run_command(".venv\\Scripts\\alembic.exe current")
    else:
        print("ERROR: Migration failed!")

def rollback_migration():
    """Rollback one migration"""
    print("=" * 60)
    print("Rollback Database Migration")
    print("=" * 60)
    print()
    print("Current version:")
    run_command(".venv\\Scripts\\alembic.exe current")
    print()
    print("Rolling back...")
    success = run_command(".venv\\Scripts\\alembic.exe downgrade -1")
    print()
    if success:
        print("SUCCESS: Rolled back successfully!")
        print()
        print("New version:")
        run_command(".venv\\Scripts\\alembic.exe current")
    else:
        print("ERROR: Rollback failed!")

def generate_migration(message):
    """Generate a new migration"""
    print("=" * 60)
    print("Generate Database Migration")
    print("=" * 60)
    print()
    print(f"Migration message: {message}")
    print()
    success = run_command(f'.venv\\Scripts\\alembic.exe revision --autogenerate -m "{message}"')
    print()
    if success:
        print("SUCCESS: Migration file generated!")
        print()
        print("Next steps:")
        print("1. Check the generated migration file in alembic/versions/")
        print("2. Run 'python alembic_helper.py upgrade' to apply it")
    else:
        print("ERROR: Failed to generate migration!")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "history":
        show_history()
    elif command == "upgrade":
        apply_migrations()
    elif command == "downgrade":
        rollback_migration()
    elif command == "generate":
        if len(sys.argv) < 3:
            print("ERROR: Please provide a migration message")
            print("Example: python alembic_helper.py generate \"add_new_field\"")
            return
        message = sys.argv[2]
        generate_migration(message)
    else:
        print(f"ERROR: Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
