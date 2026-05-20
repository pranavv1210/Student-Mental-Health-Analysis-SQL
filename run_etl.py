from __future__ import annotations

from dotenv import load_dotenv

from etl.load import run_load


if __name__ == "__main__":
    load_dotenv()
    run_load()