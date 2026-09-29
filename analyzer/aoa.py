import re


class CompetitorAnalyzer:
    """Real competitor / alternative-landscape analysis (AOA).

    Instead of only checking whether a "competition" section was detected,
    this looks for actual competitor names and differentiation language in
    the pitch text.
    """

    COMPETITOR_PATTERNS = [
        re.compile(r"compet(?:e|es|ing|itors?)\s+(?:with|against|include[s]?|are|is)\s+([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,3})"),
        re.compile(r"unlike\s+([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,3})"),
        re.compile(r"\b(?:vs\.?|versus)\s+([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,3})"),
    ]

    DIFFERENTIATOR_PHRASES = [
        "unique", "unlike", "better than", "faster", "cheaper", "only platform",
        "first to", "instead of", "unlike traditional", "competitive advantage",
    ]

    def __init__(self, sections, text=""):
        self.sections = sections
        self.text = text or ""

    def _named_competitors(self):
        found = []
        for pattern in self.COMPETITOR_PATTERNS:
            for match in pattern.finditer(self.text):
                name = match.group(1).strip().rstrip(".,;: ")
                if name and name not in found:
                    found.append(name)
        return found[:5]

    def _differentiators(self):
        lowered = self.text.lower()
        return [phrase for phrase in self.DIFFERENTIATOR_PHRASES if phrase in lowered]

    def analyze(self):
        has_section = bool(self.sections.get("competition"))
        named = self._named_competitors()
        differentiators = self._differentiators()

        if not has_section:
            level = "Missing"
            analysis = "No competitor analysis found. Investors will ask who else is solving this problem."
        elif named and differentiators:
            level = "Strong"
            analysis = "Competitors are named and a clear differentiation is called out."
        elif differentiators:
            level = "Moderate"
            analysis = "You highlight a differentiation, but naming specific competitors would strengthen this further."
        else:
            level = "Weak"
            analysis = "You mention competition but don't clearly explain your advantage over them."

        return {
            "level": level,
            "competitors_named": named,
            "differentiators_found": differentiators,
            "analysis": analysis,
        }


def analyze_aoa(sections, text=""):
    return CompetitorAnalyzer(sections, text).analyze()
