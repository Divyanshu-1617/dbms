import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_database, DB_PATH

if __name__ == "__main__":
    print(f"Initializing database from schema and seed files...")
    init_database(seed=True)
    print(f"SUCCESS: Database created and seeded at: {DB_PATH.resolve()}")
