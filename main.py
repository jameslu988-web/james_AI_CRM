from src.crm.database import init_db
from src.crm.dashboard import main as crm_main


def init():
    init_db()


if __name__ == "__main__":
    init()
    crm_main()
