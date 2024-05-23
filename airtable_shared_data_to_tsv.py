import json
import sys
import csv

data = json.load(sys.stdin)
table = data["data"]["table"]
column_order = [c["columnId"] for c in table["meaningfulColumnOrder"]]
column_map = {c["id"]: c for c in table["columns"]}
assert len(column_order) == len(
    column_map,
), "we don't know how to deal with this situation yet"

cw = csv.writer(sys.stdout, dialect=csv.excel_tab)

cw.writerow(["id", "ctime", *(column_map[c]["name"] for c in column_order)])

for row in table["rows"]:
    print_row = [row["id"], row["createdTime"]]
    for col_id in column_order:
        col = column_map[col_id]
        col_value = row["cellValuesByColumnId"].get(col_id)
        if col_value is not None:
            if col["type"] in ("select", "multiSelect"):
                if not isinstance(col_value, list):
                    col_value = [col_value]
                values = [col["typeOptions"]["choices"][v]["name"] for v in col_value]
                print_row.append(", ".join(values))
            else:
                print_row.append(str(col_value))
        else:
            print_row.append("")
    cw.writerow(print_row)
