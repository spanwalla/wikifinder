import argparse
import os.path
import re
import csv

from tqdm import tqdm
from server import models
from sqlalchemy.orm import Session
from server.database import SessionLocal, engine


def reload_table(db: Session, file: str, table: str):
    pattern = re.compile(r"^\w+-(\d{8})-.+\.sql\.csv")
    result = re.match(pattern, os.path.basename(file)).groups()
    if result is None:
        raise ValueError("Incorrect file name or path to file.")

    available_tables = models.Base.metadata.tables.keys()
    if table not in available_tables:
        raise ValueError(f"Incorrect table type, use one of the following: {list(available_tables)}")

    models.Base.metadata.drop_all(bind=engine, tables=[models.Base.metadata.tables[table]])
    models.Base.metadata.create_all(bind=engine)

    data = list()
    with open(file, 'r', encoding='utf-8') as csvfile, tqdm(disable=False) as progress_bar:
        csv_reader = csv.reader(csvfile, delimiter='\t')

        for row in csv_reader:
            # data.append(models.Page(id=int(row[0]), title=row[1], is_redirect=(int(row[2]) == 1)))
            data.append(models.PageLink(page_from=int(row[0]), page_target=int(row[1])))
            if len(data) > 1000000:
                db.bulk_save_objects(data)
                data.clear()
            progress_bar.update(1)

        if len(data) > 0:
            db.bulk_save_objects(data)
        db.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to [wiki]-[date]-[type].sql.csv file. Check its name.")
    parser.add_argument("table", help="table to reload (drop and insert values from .sql.csv).")

    args = parser.parse_args()
    db = SessionLocal()
    try:
        reload_table(db, args.filename, args.table)

    finally:
        db.close()


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    main()
