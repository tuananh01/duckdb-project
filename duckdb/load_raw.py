#!/usr/bin/env python3
"""Load tutorial CSVs into duckdb/raw.duckdb (same layout as snowflake/raw_data.sql)."""

import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent  
"""
(__file__) represents "load_raw.py" or "raw_data.sql" in this case
Path(__file__).resolve() evaluates to the absolute path: 
Path("C:/Projects/dbt-Fundamental/duckdb/load_raw.py")
parent extracts the containing folder: Path("C:/Projects/dbt-Fundamental/duckdb")
"""
RAW_DB = ROOT / "source_data.duckdb"    ## duckdb is DuckDB extension
SQL_FILE = ROOT / "raw_data.sql"


def main() -> None:  # indicating that the main function does not return any data when it finishes.
    
    ###########################Checking the database####################################
    os.chdir(ROOT)
    if RAW_DB.exists():
        RAW_DB.unlink()  # permanent delete the existing database
    wal = Path(str(RAW_DB) + ".wal")
    if wal.exists():
        wal.unlink()
    ###################################################################################
    
    ###########################Create schema and table in DuckDB####################################
    con = duckdb.connect(str(RAW_DB))  #connect to DuckDB 
    statements = [
        stmt.strip()
        for stmt in SQL_FILE.read_text().split(";")
        if stmt.strip() and not stmt.strip().lower().startswith("select")
    ]
    '''
    SQL_FILE.read_text() Python opens the file and reads the entire document into memory as one giant, raw string
    .split(";"): Chops that string into a list of smaller strings every time it encounters a semicolon (;). 
    This isolates each CREATE SCHEMA and CREATE TABLE command.
    if stmt.strip(): Filters out empty strings and whitespace left over from splitting line breaks.
    and not stmt.strip().lower().startswith("select"): This explicitly drops the 
    diagnostic SELECT * queries located at the bottom of the raw_data.sql file
    '''
    for statement in statements:
        con.execute(statement)         #execute SQL commands to create real schema in DuckDB
        
    ##################################################################################################


    ###########################Automated validation and cleanup####################################

    counts = {
        "jaffle_shop.customers": con.execute(
            "select count(*) from jaffle_shop.customers"
        ).fetchone()[0],
        '''
        .fetchone() retrieves the first (and in this case, only) row of that result. 
        It returns the data as a Python tuple, such as (100,).
        '''
        "jaffle_shop.orders": con.execute(
            "select count(*) from jaffle_shop.orders"
        ).fetchone()[0],
        "stripe.payment": con.execute("select count(*) from stripe.payment"
        ).fetchone()[0],
    }
    con.close()
    '''
    con.close(): This is a critical step. Because DuckDB is an embedded database, 
    it places a strict file lock on the .duckdb file while it is connected. 
    Closing the connection explicitly releases Python's lock on the file, ensuring that downstream tools 
    (like dbt or the ui.py script) can successfully attach to it later without crashing.
    '''

    print(f"Wrote {RAW_DB}")
    for relation, n in counts.items():
        print(f"  {relation}: {n} rows")

    ##################################################################################################

if __name__ == "__main__":
    main()
