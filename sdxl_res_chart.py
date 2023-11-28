from fractions import Fraction

COMMON_ASPECT_RATIOS = [
    Fraction(1, 1),
    Fraction(5, 4),
    Fraction(4, 3),
    Fraction(3, 2),
    Fraction(16, 10),
    Fraction(5, 3),
    Fraction(16, 9),
]
COMMON_ASPECT_RATIOS.extend([ar**-1 for ar in COMMON_ASPECT_RATIOS])


def get_nearest_ar(ar: Fraction):
    return min(COMMON_ASPECT_RATIOS, key=lambda common_ar: abs(common_ar - ar))


def quantize(n: int, q: int) -> int:
    return round(n / q) * q


def main():
    target_pix = 1024 * 1024
    pix_leeway = 0.1
    min_pix = target_pix * (1 - pix_leeway)
    max_pix = target_pix * (1 + pix_leeway)
    min_ar = 0.5
    max_ar = 2.0

    options = set()

    for w in range(64, 2048, 8):
        for h in range(64, 2048, 8):
            w = quantize(w, 64)
            h = quantize(h, 64)
            pix = w * h
            ar = w / h
            if min_pix <= pix <= max_pix and min_ar <= ar <= max_ar:
                options.add((w, h))

    for w, h in sorted(options, key=lambda wh: wh[0] / wh[1]):
        pix = w * h
        ar = Fraction(w, h)
        nearest_common_ar = get_nearest_ar(ar)
        ar_diff = (float(ar) - float(nearest_common_ar)) * 100

        print(
            f"| {w:4} | {h:4} | "
            f"{pix / (1024 * 1024):.02f} MPix | "
            f"{str(ar):7} | "
            f"{float(ar):.3f} | "
            f"{nearest_common_ar}{ar_diff:+.01f}% |",
        )


if __name__ == "__main__":
    main()
