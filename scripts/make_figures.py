"""Generate the README figures from the validation results.

Uses only the Python standard library and writes SVG files to figures/.
All numbers are copied from the caret confusionMatrix() output in
report/activity_prediction_report.pdf (validation set, n = 5,885).

    python3 scripts/make_figures.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, GRID = "#1f2328", "#656d76", "#d0d7de"
BEST, OTHER = "#1a7f37", "#8c959f"
CLASSES = "ABCDE"

# (model, accuracy, 95% CI low, 95% CI high)
MODELS = [
    ("Random forest", 0.9927, 0.9902, 0.9947),
    ("Gradient boosting", 0.9873, 0.9841, 0.9900),
    ("Decision tree", 0.5458, 0.5330, 0.5586),
]
NO_INFO_RATE = 0.2845

# Random forest confusion matrix: rows = predicted, cols = actual
RF_CONFUSION = [
    [1672, 3, 0, 0, 0],
    [2, 1130, 14, 0, 0],
    [0, 6, 1008, 6, 3],
    [0, 0, 4, 956, 3],
    [0, 0, 0, 2, 1076],
]


def svg_doc(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">\n'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>\n{body}</svg>\n')


def text(x, y, s, size=13, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>\n')


def model_comparison():
    width, height = 820, 310
    left, right, top, bar_h, gap = 170, 700, 104, 40, 22

    def px(v):
        return left + v * (right - left)

    body = text(24, 34, "Validation accuracy by model", 18, weight="600")
    body += text(24, 56, "Held-out 30% of the training data (n = 5,885). Whiskers show 95% CIs.", 12, MUTED)

    axis_y = top + len(MODELS) * (bar_h + gap) - gap + 10
    for tick in (0, 0.25, 0.5, 0.75, 1.0):
        body += f'<line x1="{px(tick):.1f}" y1="{top}" x2="{px(tick):.1f}" y2="{axis_y}" stroke="{GRID}"/>\n'
        body += text(px(tick), axis_y + 18, f"{tick:.0%}", 12, MUTED, "middle")

    nir = px(NO_INFO_RATE)
    body += f'<line x1="{nir:.1f}" y1="{top - 24}" x2="{nir:.1f}" y2="{axis_y}" stroke="{INK}" stroke-dasharray="4,3"/>\n'
    body += text(nir + 6, top - 12, "no-information rate (28%)", 11, MUTED)

    for i, (name, acc, lo, hi) in enumerate(MODELS):
        y = top + i * (bar_h + gap)
        color = BEST if i == 0 else OTHER
        body += f'<rect x="{left}" y="{y}" width="{px(acc) - left:.1f}" height="{bar_h}" fill="{color}" rx="3"/>\n'
        cy = y + bar_h / 2
        body += f'<line x1="{px(lo):.1f}" y1="{cy}" x2="{px(hi):.1f}" y2="{cy}" stroke="{INK}" stroke-width="1.5"/>\n'
        body += text(left - 12, cy + 5, name, 13, INK, "end", "600" if i == 0 else "normal")
        body += text(px(acc) + 10, cy + 5, f"{acc:.2%}", 13, color, weight="600")
    return svg_doc(width, height, body)


def confusion_heatmap():
    cell, left, top = 72, 150, 110
    n = len(CLASSES)
    width, height = left + cell * n + 60, top + cell * n + 60
    biggest = max(max(r) for r in RF_CONFUSION)

    body = text(24, 34, "Random forest confusion matrix", 18, weight="600")
    body += text(24, 56, "Validation set. 43 of 5,885 movements misclassified (0.73%).", 12, MUTED)
    body += text(left + cell * n / 2, top - 30, "Actual class", 12, MUTED, "middle", "600")
    body += (f'<text x="{left - 60}" y="{top + cell * n / 2}" font-size="12" fill="{MUTED}" '
             f'font-weight="600" text-anchor="middle" transform="rotate(-90 {left - 60} {top + cell * n / 2})">'
             f'Predicted class</text>\n')

    for j, c in enumerate(CLASSES):
        body += text(left + j * cell + cell / 2, top - 10, c, 13, INK, "middle", "600")
    for i, row in enumerate(RF_CONFUSION):
        body += text(left - 14, top + i * cell + cell / 2 + 5, CLASSES[i], 13, INK, "end", "600")
        for j, v in enumerate(row):
            x, y = left + j * cell, top + i * cell
            if i == j:
                fill, ink = BEST, "#ffffff"
            elif v:
                fill, ink = "#ffebe9", "#cf222e"
            else:
                fill, ink = "#f6f8fa", MUTED
            body += f'<rect x="{x}" y="{y}" width="{cell - 3}" height="{cell - 3}" fill="{fill}" rx="4"/>\n'
            weight = "600" if i == j or v else "normal"
            body += text(x + (cell - 3) / 2, y + cell / 2 + 4, f"{v:,}", 14 if i == j else 13, ink, "middle", weight)
    return svg_doc(width, height, body)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "model_comparison.svg").write_text(model_comparison())
    (OUT / "rf_confusion_matrix.svg").write_text(confusion_heatmap())
    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
