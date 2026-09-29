class InvestorSimulator:
    """Simulates reactions from a small panel of investor personas, each
    focused on a different part of the pitch."""

    PERSONAS = [
        {
            "name": "Skeptical VC",
            "focus": ["business_model", "competition"],
            "style": "financial and competitive risk",
        },
        {
            "name": "Product-Focused Angel",
            "focus": ["problem", "solution"],
            "style": "product-market fit",
        },
        {
            "name": "Growth Investor",
            "focus": ["market", "team"],
            "style": "scale and execution",
        },
    ]

    def __init__(self, sections, score=0):
        self.sections = sections
        self.score = score

    def _persona_reaction(self, persona):
        focus = persona["focus"]
        weak = [f for f in focus if not self.sections.get(f)]

        if not weak:
            reaction = f"Solid coverage on {' and '.join(f.replace('_', ' ') for f in focus)}. This holds up under {persona['style']} scrutiny."
            question = f"How do you plan to defend your {focus[-1].replace('_', ' ')} position as you scale?"
            verdict = "Interested" if self.score >= 60 else "Cautiously interested"
        else:
            reaction = f"I'm not convinced yet on {' and '.join(f.replace('_', ' ') for f in weak)} - that's central to {persona['style']}."
            question = f"Can you walk me through your {weak[0].replace('_', ' ')} in more detail?"
            verdict = "Needs more information"

        return {
            "persona": persona["name"],
            "reaction": reaction,
            "question": question,
            "verdict": verdict,
        }

    def simulate(self):
        return [self._persona_reaction(p) for p in self.PERSONAS]


def simulate_investor_panel(sections, score=0):
    return InvestorSimulator(sections, score).simulate()
