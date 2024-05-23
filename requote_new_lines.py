import sys

for line in sys.stdin:
    if (
        line.startswith("+")
        and not line.startswith("+++")
        and '"' not in line
        and line.count("'") % 2 == 0
    ):
        line = line.replace("'", '"')
    sys.stdout.write(line)
