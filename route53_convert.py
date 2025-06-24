# Convert Route53 `list-resource-record-sets` JSON output to
# a format that can be passed to `change-resource-record-sets`.
import argparse
import json


def by_name_aliases_last(change):
    rs = change["ResourceRecordSet"]
    weight = 1000 if "AliasTarget" in rs else 0
    return rs["Name"].lower(), weight


def chunk_for_output(changes):
    # * Each file can contain a maximum of 1,000 records.
    # * The maximum combined length of the values in all Value elements is 32,000 bytes.
    # (We'll approximate by checking that the JSON serialized length is less than 31,000 bytes.)
    chunk = []
    for record in changes:
        chunk.append(record)
        if len(chunk) >= 1000:
            yield chunk
            chunk = []
        if chunk:
            serialized_chunk = json.dumps({"Changes": chunk})
            if len(serialized_chunk) >= 31000:
                yield chunk
                chunk = []
    if chunk:
        yield chunk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, type=argparse.FileType("r"))
    ap.add_argument("-o", "--output-base-name", required=True)
    args = ap.parse_args()
    input_data = json.load(args.input)
    changes = []
    for record in input_data.get("ResourceRecordSets", []):
        # Skip SOA and NS records.
        if record["Type"] in ("SOA", "NS"):
            print("Skipping record:", record)
            continue
        changes.append(
            {
                "Action": "CREATE",
                "ResourceRecordSet": record,
            },
        )
    changes.sort(key=by_name_aliases_last)
    for index, chunk_changes in enumerate(chunk_for_output(changes), 1):
        output_file_name = f"{args.output_base_name}-{index:02d}.json"
        with open(output_file_name, "w") as output_file:
            json.dump(
                {
                    "Comment": "Converted from Route53 list-resource-record-sets output",
                    "Changes": chunk_changes,
                },
                output_file,
                indent=2,
            )
        print(f"Wrote {len(chunk_changes)} changes to {output_file_name}")


if __name__ == "__main__":
    main()
