# /// script
# dependencies = [
#     "numpy",
#     "scipy",
# ]
# ///

"""
Convert a cashflow CSV file into a resampled WAV.
"""

import csv
import datetime
from collections import defaultdict

import numpy as np
import scipy.io.wavfile


def read_events():
    aps = defaultdict(list)

    with open("cashflow.csv") as f:
        t0 = None
        for i, row in enumerate(csv.DictReader(f)):
            t = datetime.datetime.strptime(row["date"][:19], "%Y-%m-%d %H:%M:%S")
            if not t0:
                t0 = t
            a = float(row["cashflow"])
            aps[(t - t0).total_seconds()].append(a)

    return aps


def expand_groups(aps):
    aps = sorted(aps.items())
    for ps_idx, (t, ps) in enumerate(aps):
        next_t = aps[ps_idx + 1][0] if ps_idx + 1 < len(aps) else t + 60
        delta_t = next_t - t
        for i, v in enumerate(ps):
            yield (t + i / len(ps) * delta_t, v)


def next_power_of_2(x):
    return 1 << (x - 1).bit_length()


def main():
    aps = read_events()
    print(f"Read {len(aps)} event groups")
    aps_r = list(expand_groups(aps))
    print(f"Expanded event groups into {len(aps_r)} samples")
    x, y = zip(*aps_r)
    num_samples = next_power_of_2(len(x))
    print(f"Resampling to {num_samples} samples")
    xnew = np.linspace(np.min(x), np.max(x), num=num_samples)
    ynew = np.interp(xnew, x, y)
    ynew -= np.min(ynew)
    ynew /= np.max(ynew)
    ynew *= 65535
    ynew -= 32768
    ynew = ynew.astype(np.int16)
    scipy.io.wavfile.write(f"cashflow_{num_samples}.wav", 44100, ynew)


if __name__ == "__main__":
    main()
