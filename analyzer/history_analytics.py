import numpy as np
import pandas as pd


class PitchHistoryAnalyzer:
    """Aggregate analytics over a user's past pitch submissions - pandas for
    tabular aggregation, numpy for the score trend line."""

    def __init__(self, ideas):
        self.ideas = ideas or []

    def analyze(self):
        if not self.ideas:
            return {
                "count": 0,
                "average_score": 0,
                "best_score": 0,
                "worst_score": 0,
                "trend": "No data yet",
                "latest_readiness": None,
                "score_history": [],
            }

        df = pd.DataFrame(self.ideas)
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)

        count = int(len(df))
        average_score = round(float(df["score"].mean()), 2)
        best_score = round(float(df["score"].max()), 2)
        worst_score = round(float(df["score"].min()), 2)
        latest_readiness = self.ideas[-1].get("readiness")
        score_history = [
            {"date": idea.get("date", ""), "score": round(float(idea.get("score", 0)), 2)}
            for idea in self.ideas
        ]

        if count >= 2:
            x = np.arange(count)
            slope = float(np.polyfit(x, df["score"].to_numpy(), 1)[0])

            if slope > 0.5:
                trend = "Improving \U0001F4C8"
            elif slope < -0.5:
                trend = "Declining \U0001F4C9"
            else:
                trend = "Steady ➖"
        else:
            trend = "Not enough data yet"

        return {
            "count": count,
            "average_score": average_score,
            "best_score": best_score,
            "worst_score": worst_score,
            "trend": trend,
            "latest_readiness": latest_readiness,
            "score_history": score_history,
        }


def analyze_history(ideas):
    return PitchHistoryAnalyzer(ideas).analyze()
