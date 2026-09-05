import os
from typing import List, Dict, Any
import matplotlib
# Use a non-GUI backend so charts generate cleanly in headless environments, servers, or Docker
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class VisualReportingService:
    """
    Generates comparative visual summaries from experiment benchmark data.
    """

    @staticmethod
    def generate_delta_bar_chart(
        records: List[Dict[str, Any]], 
        output_filepath: str = "results/complexity_maintainability_delta.png"
    ) -> str:
        """
        Creates a grouped bar chart comparing Delta Complexity and Delta Maintainability
        across different experimental runs.
        """
        if not records:
            raise ValueError("No records provided to plot.")

        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

        labels = [f"{r['model_name']}\n({r['prompt_strategy']})" for r in records]
        delta_complexity = [r["delta_complexity"] for r in records]
        delta_mi = [r["delta_maintainability_index"] for r in records]

        x = range(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        # Complexity reduction is good (negative delta), MI increase is good (positive delta)
        ax.bar([i - width/2 for i in x], delta_complexity, width, label="Δ Cyclomatic Complexity", color="#d9534f")
        ax.bar([i + width/2 for i in x], delta_mi, width, label="Δ Maintainability Index", color="#5cb85c")

        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_ylabel("Metric Change")
        ax.set_title("AI Refactoring Impact: Complexity vs Maintainability Delta")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=9)
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.7)

        plt.tight_layout()
        plt.savefig(output_filepath, dpi=300)
        plt.close(fig)

        return output_filepath