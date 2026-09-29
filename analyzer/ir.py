class InvestorReadinessEvaluator:
    """Maps the overall pitch score to an investor-readiness verdict."""

    def __init__(self, score):
        self.score = score

    def evaluate(self):
        if self.score >= 80:
            return "Investor Ready"
        elif self.score >= 50:
            return "Moderate - Needs improvement"
        else:
            return "Not ready for investors"


def analyze_ir(score):
    return InvestorReadinessEvaluator(score).evaluate()
