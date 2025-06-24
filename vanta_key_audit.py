"""
Audit the "keys" CSV and "computers" CSV files from Vanta to find keys that are associated with multiple devices.
"""

import argparse
import csv
from collections import defaultdict
from uuid import UUID


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys_csv")
    ap.add_argument("computers_csv")
    args = ap.parse_args()
    with open(args.computers_csv) as f:
        computers = {UUID(r["Device ID"]): r for r in csv.DictReader(f)}
    key_id_to_device = defaultdict(set)
    with open(args.keys_csv) as f:
        for row in csv.DictReader(f):
            for fingerprint in row["fingerprints"].split(", "):
                if fingerprint:
                    key_id_to_device[fingerprint].add(UUID(row["UUID"]))
    for key_id, devices in key_id_to_device.items():
        if len(devices) > 1:
            device_names = ", ".join(
                computers.get(device_id, {}).get("Name") or f"(??? {device_id})"
                for device_id in devices
            )
            print(f"Key {key_id} is on multiple devices: {device_names}")


if __name__ == "__main__":
    main()
