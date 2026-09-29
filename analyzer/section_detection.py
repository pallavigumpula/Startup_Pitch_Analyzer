import re

from nltk.stem import PorterStemmer

SECTION_KEYWORDS = {
    "problem": ["problem", "issue", "challenge", "pain point"],
    "solution": ["solution", "we provide", "our product", "our platform"],
    "market": ["market", "customer", "customers", "target market", "target audience"],
    "business_model": ["revenue", "pricing", "subscription", "business model"],
    "competition": ["competitor", "competitors", "existing solution", "alternative"],
    "team": ["team", "founder", "founders", "cofounder", "developer"]
}


class SectionDetector:
    """Detects which pitch sections are present.

    Single-word keywords are matched by Porter stem (via NLTK), so variants
    such as competitor/competitors/competing or founder/founders count as the
    same concept. Multi-word phrases are matched as literal word-boundary
    substrings, since stemming a whole phrase token-by-token is unreliable.
    """

    SECTION_KEYWORDS = SECTION_KEYWORDS
    _stemmer = PorterStemmer()

    def __init__(self, text):
        self.text = text
        self._lowered = text.lower()
        self._tokens = re.findall(r"[a-z']+", self._lowered)
        self._stems = {self._stemmer.stem(t) for t in self._tokens}

    def _keyword_hits(self, section):
        hits = []
        for kw in self.SECTION_KEYWORDS.get(section, []):
            if " " in kw:
                if re.search(r"\b" + re.escape(kw) + r"\b", self._lowered):
                    hits.append(kw)
            elif self._stemmer.stem(kw) in self._stems:
                hits.append(kw)
        return hits

    def keyword_ratio(self, section):
        # Keywords for a section are mostly synonyms of one concept (e.g. problem /
        # issue / challenge), so a single hit already indicates solid coverage.
        # Extra distinct hits add a smaller bonus rather than being weighted equally.
        keywords = self.SECTION_KEYWORDS.get(section, [])
        if not keywords:
            return 0.0

        hits = len(self._keyword_hits(section))
        if hits == 0:
            return 0.0
        if len(keywords) == 1:
            return 1.0

        return min(1.0, 0.5 + 0.5 * (hits - 1) / (len(keywords) - 1))

    def detect(self):
        return {section: bool(self._keyword_hits(section)) for section in self.SECTION_KEYWORDS}


def _keyword_hits(text, section):
    return SectionDetector(text)._keyword_hits(section)


def keyword_ratio(text, section):
    return SectionDetector(text).keyword_ratio(section)


def detect_sections(text):
    return SectionDetector(text).detect()
