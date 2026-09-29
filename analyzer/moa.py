import re


class MarketAnalyzer:
    """Real market-opportunity analysis (MOA).

    Instead of only checking whether a "market" section was detected, this
    looks for quantified market-size mentions and a clearly defined target
    audience in the pitch text.
    """

    SIZE_PATTERN = re.compile(
        r"\b\d[\d,\.]*\s*(?:million|billion|thousand|[kmb])\b"
        r"|\b\d[\d,\.]*\+?\s*(?:users|customers|people|farmers|businesses|hospitals|clinics|schools|students)\b",
        re.IGNORECASE,
    )

    AUDIENCE_KEYWORDS = [
        "target market", "target audience", "target users", "target customers",
        "customers", "users", "businesses", "consumers",
    ]

    def __init__(self, sections, text=""):
        self.sections = sections
        self.text = text or ""

    def _size_mentions(self):
        seen = []
        for match in self.SIZE_PATTERN.finditer(self.text):
            value = match.group(0).strip()
            if value not in seen:
                seen.append(value)
        return seen[:5]

    def _audience_defined(self):
        lowered = self.text.lower()
        return any(kw in lowered for kw in self.AUDIENCE_KEYWORDS)

    def analyze(self):
        has_section = bool(self.sections.get("market"))
        sizes = self._size_mentions()
        audience_defined = self._audience_defined()

        if not has_section:
            level = "Weak"
            analysis = "Market isn't clearly described. Define who your customers are and how many of them exist."
        elif sizes and audience_defined:
            level = "Strong"
            analysis = "A clear target audience and a quantified market size are both present."
        elif audience_defined:
            level = "Moderate"
            analysis = "Target audience is defined, but adding a market-size number would make this more convincing."
        else:
            level = "Moderate"
            analysis = "Market is mentioned but lacks a clearly defined audience or size."

        return {
            "level": level,
            "market_size_mentions": sizes,
            "audience_defined": audience_defined,
            "analysis": analysis,
        }


def analyze_moa(sections, text=""):
    return MarketAnalyzer(sections, text).analyze()
