import sys
import traceback
import signal
import threading
import time

def timeout_handler(signum, frame):
    print("⏱️ Import timeout after 10 seconds!")
    import threading
    print(f"Active threads: {threading.active_count()}")
    for thread in threading.enumerate():
        print(f"  - {thread.name}: {thread.daemon}")
    sys.exit(1)

print("Testing imports...")

# Set 10 second timeout
signal.signal(signal.SIGALRM, timeout_handler) if hasattr(signal, 'SIGALRM') else None

try:
    print("Importing main module...")
    from src.api import main
    print("✅ Module imported!")
    print("Getting app object...")
    app = main.app
    print("✅ Import successful!")
except KeyboardInterrupt:
    print("\n❌ Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"❌ Import failed: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
