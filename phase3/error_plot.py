from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

input_file = Path(__file__).parent / 'results/error_analysis.csv'
data = pd.read_csv(input_file)

metrics = data.columns[1:]

colors = {
    "Halluc. Entities": "#FFC924",
    "Missed Entities": "#FFDC72",
    "Halluc. Relations": "#5FCC67",
    "Missed Relations": "#8CCE91",
    "Halluc. Triples": "#5791E2",
    "Missed Triples": "#72ADFF",
    "Schema Violations": "#2862C1",
    "Extra Text": "#6B43A5",
    "Invalid RDF": "#A443A2",
}

color_list = [colors[m] for m in metrics]
ax = data.set_index("Configuration")[metrics].plot(
    kind="bar",
    figsize=(12, 5),
    width=0.9,
    **({"color": color_list} if all(color_list) else {}),
)
ax.legend(title=None, ncol=5)
ax.set_ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(Path(__file__).parent / "results/error_plot.png")
plt.show()
