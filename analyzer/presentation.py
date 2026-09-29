import re

from analyzer.section_detection import SECTION_KEYWORDS


class PresentationAnalyzer:
    """Heuristic feedback on how a pitch would come across when *presented*
    (structure, tone, length, use of evidence) - separate from the section
    content scoring done in scoring.py."""

    FILLER_WORDS = [
        "maybe", "perhaps", "i think", "i guess", "kind of", "sort of",
        "hopefully", "probably", "not sure", "i believe"
    ]

    SECTION_ORDER = ["problem", "solution", "market", "business_model", "competition", "team"]

    def __init__(self, text, sections):
        self.text = text
        self.sections = sections
        self.words = re.findall(r"[A-Za-z']+", text)
        self.sentences = [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]

    def _word_count(self):
        return len(self.words)

    def _avg_sentence_length(self):
        if not self.sentences:
            return 0
        return self._word_count() / len(self.sentences)

    def _filler_hits(self):
        lowered = self.text.lower()
        return [w for w in self.FILLER_WORDS if re.search(r"\b" + re.escape(w) + r"\b", lowered)]

    def _has_metrics(self):
        return bool(re.search(r"\d", self.text))

    def _section_positions(self):
        lowered = self.text.lower()
        positions = {}

        for sec in self.SECTION_ORDER:
            if not self.sections.get(sec):
                continue

            hits = [lowered.find(kw) for kw in SECTION_KEYWORDS.get(sec, []) if kw in lowered]
            hits = [p for p in hits if p != -1]

            if hits:
                positions[sec] = min(hits)

        return positions

    def _section_order_ok(self):
        positions = self._section_positions()

        if "problem" in positions and "solution" in positions:
            return positions["problem"] < positions["solution"]

        return True

    def analyze(self):
        feedback = []
        score = 100

        word_count = self._word_count()
        if word_count < 60:
            feedback.append("Your pitch is quite short - add more detail to each section so it reads as a complete narrative.")
            score -= 20
        elif word_count > 600:
            feedback.append("Your pitch is lengthy - tighten the language so investors can grasp it quickly.")
            score -= 10

        avg_len = self._avg_sentence_length()
        if avg_len > 28:
            feedback.append("Several sentences are long and complex - shorter sentences are easier to deliver with confidence.")
            score -= 10

        fillers = self._filler_hits()
        if fillers:
            feedback.append(
                "Avoid uncertain language (" + ", ".join(fillers) + ") - it can make you sound less confident to investors."
            )
            score -= 10

        if not self._has_metrics():
            feedback.append("Add concrete numbers or metrics (market size, growth rate, pricing) to make your pitch more credible.")
            score -= 15

        if not self._section_order_ok():
            feedback.append("Present the problem before the solution - it creates a stronger narrative for your audience.")
            score -= 10

        if not feedback:
            feedback.append("Your pitch reads clearly and confidently. Practice your delivery to match the strong content.")

        score = max(0, min(100, score))

        return {"feedback": feedback, "presentation_score": score}


def analyze_presentation(text, sections):
    return PresentationAnalyzer(text, sections).analyze()
