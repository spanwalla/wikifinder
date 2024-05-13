# Thanks to the napsternxg, url: https://github.com/napsternxg/WikiUtils

import argparse
import re
import gzip
import sys
from typing import Tuple

from tqdm import tqdm
from collections import namedtuple

from server import models
from server.crud import get_page_id_by_title
from server.database import SessionLocal, engine

FILEPROPS = namedtuple("Fileprops", "parser num_fields column_indexes")

CATEGORYLINKS_PARSER = re.compile(
    r'^(?P<row0>[0-9]+?),(?P<row1>\'.*?\'?),(?P<row2>\'.*?\'?),(?P<row3>\'[0-9\-:]+\'?),(?P<row4>\'.*?\'?),'
    r'(?P<row5>\'[a-z\-]*?\'?),(?P<row6>\'[a-z]+\'?)$')
PAGELINKS_PARSER = re.compile(r'^(?P<row0>[0-9]+?),(?P<row1>[0-9]+?),'
                              r'(?P<row2>\'.*?\'?),(?P<row3>[0-9]+?),(?P<row4>[0-9]+?)$')
REDIRECT_PARSER = re.compile(
    r'^(?P<row0>[0-9]+?),(?P<row1>-?[0-9]+?),(?P<row2>\'.*?\'?),(?P<row3>\'.*?\'?),(?P<row4>\'.*?\'?)$')
CATEGORY_PARSER = re.compile(
    r'^(?P<row0>[0-9]+?),(?P<row1>\'.*?\'?),(?P<row2>[0-9]+?),(?P<row3>[0-9]+?),(?P<row4>[0-9]+?)$')
PAGE_PARSER = re.compile(r'^(?P<row0>[0-9]+?),(?P<row1>[0-9]+?),(?P<row2>\'.*?\'?),(?P<row3>[0-9]+?),(?P<row4>[0-9]?),'
                         r'(?P<row5>[0-9.]+?),(?P<row6>\'.*?\'?),(?P<row7>(?P<row7val>\'.*?\'?)|(?P<row8null>NULL)),'
                         r'(?P<row9>[0-9]+?),(?P<row10>[0-9]+?),(?P<row11>(?P<row11val>\'.*?\'?)|(?P<row11null>NULL)),'
                         r'(?P<row12>(?P<row13val>\'.*?\'?)|(?P<row12null>NULL))$')

FILETYPE_PROPS = dict(
    pagelinks=FILEPROPS(PAGELINKS_PARSER, 5, (0, 1, 2, 3)),
    page=FILEPROPS(PAGE_PARSER, 12, (0, 1, 2, 3)),
    # redirect=FILEPROPS(REDIRECT_PARSER, 5, (0, 1, 2)),
    # categorylinks=FILEPROPS(CATEGORYLINKS_PARSER, 7, (0, 1, 6)),
    # category=FILEPROPS(CATEGORY_PARSER, 5, (0, 1, 2, 3, 4)),
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_match(match, column_indexes):
    row = match.groupdict()
    return tuple(row[f"row{i}"] for i in column_indexes)


def parse_value(value, parser, column_indexes: Tuple, value_idx=0):
    # replace unicode dash with ascii dash
    value = value.replace("\\xe2\\x80\\x93", "-")
    parsed_correctly = False
    for i, match in enumerate(parser.finditer(value)):
        parsed_correctly = True
        try:
            row = parse_match(match, column_indexes)
            yield row
        except Exception as e:
            print(f"Line: {value}, exception: {e}.", file=sys.stderr)

    if not parsed_correctly:
        print(f"Line: {value}, idx: {value_idx}, exception: unable to parse.", file=sys.stderr)


def process_insert_line(line, parser, column_indexes, count_inserts=0, pbar=None):
    _, _, values = line.partition(" VALUES ")

    # Each insert statement has format:
    # INSERT INTO "table_name" VALUES (v1,v2,v3),(v1,v2,v3),(v1,v2,v3);
    # When splitting by "),(" we need to only consider string from values[1:-2]
    # This ignores the starting "(" and ending ");"
    values = values.strip()[1:-2].split("),(")
    pbar.set_postfix(found_values=len(values), insert_num=count_inserts)
    for value_idx, value in enumerate(values):
        for row in parse_value(value, parser, column_indexes, value_idx):
            yield row


def process_file(fp, filetype, silent=False):
    if filetype not in FILETYPE_PROPS:
        raise ValueError(f"Invalid filetype {filetype}.")

    parser, num_fields, column_indexes = FILETYPE_PROPS[filetype]
    print(f"Parser: {filetype}, number of fields: {num_fields}, column indexes: {column_indexes}.")
    db = SessionLocal()

    try:
        data = list()
        with tqdm(disable=silent) as progress_bar:
            insert_count = 0
            for line_no, line in enumerate(fp, start=1):
                if line.startswith(f"INSERT INTO `{filetype}` VALUES "):
                    insert_count += 1
                    for row in process_insert_line(line, parser, column_indexes, insert_count, progress_bar):
                        if progress_bar is not None:
                            progress_bar.update(1)

                        if filetype == "page":
                            page_id, page_namespace, page_title, page_is_redirect = row
                            if int(page_namespace) == 0:
                                data.append(
                                    models.Page(id=int(page_id), title=page_title, is_redirect=(int(page_is_redirect) == 1)))

                        elif filetype == "pagelinks":
                            page_from_id, page_target_namespace, page_target_title, page_from_namespace = row
                            if int(page_target_namespace) == 0 and int(page_from_namespace) == 0:
                                page_target_id = get_page_id_by_title(db, page_target_title)
                                if page_target_id is not None:
                                    data.append(models.PageLink(page_from=int(page_from_id), page_target=page_target_id))

                    if len(data) > 1000000:
                        db.bulk_save_objects(data)
                        db.commit()
                        data.clear()

            if len(data) > 0:
                db.bulk_save_objects(data)
                db.commit()

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to sql.gz file.")
    parser.add_argument("filetype",
                        help=f"following file types are supported:\n[{', '.join(FILETYPE_PROPS.keys())}")
    parser.add_argument("--silent", "-s", default=False, action="store_true", help="disable progress bar")
    args = parser.parse_args()
    with gzip.open(args.filename, 'rt', encoding='utf-8', errors='backslashreplace') as fp:
        process_file(fp, args.filetype, silent=args.silent)


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    main()
