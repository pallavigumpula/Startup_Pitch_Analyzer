class IndustryClassifier:
    """Detects the likely industry vertical of a pitch from keyword hits and
    offers industry-specific evaluation tips."""

    INDUSTRY_KEYWORDS = {
        "Healthcare": ["hospital", "patient", "clinic", "healthcare", "doctor", "medical", "diagnosis", "telemedicine"],
        "FinTech": ["payment", "bank", "banking", "loan", "credit", "wallet", "insurance", "fintech", "investment"],
        "EdTech": ["student", "school", "curriculum", "teacher", "learning", "course", "education", "edtech"],
        "E-commerce": ["e-commerce", "ecommerce", "marketplace", "shopping", "seller", "buyer", "retail"],
        "AgriTech": ["farmer", "crop", "agriculture", "farm", "agri", "harvest", "livestock"],
        "SaaS / Enterprise Tech": ["saas", "software", "platform", "api", "dashboard", "enterprise", "cloud"],
        "Food & Beverage": ["restaurant", "food delivery", "recipe", "kitchen", "cafe", "beverage"],
        "Transportation & Logistics": ["logistics", "delivery", "shipping", "fleet", "transport", "supply chain", "tracking"],
    }

    INDUSTRY_TIPS = {
        "Healthcare": [
            "Address regulatory and compliance requirements (e.g. data privacy, licensing).",
            "Clarify how patient or clinical outcomes improve, not just operational efficiency.",
        ],
        "FinTech": [
            "Explain your regulatory/compliance approach (KYC, licensing, data security).",
            "Clarify unit economics - transaction fees, interest margins, or subscription revenue.",
        ],
        "EdTech": [
            "Explain the learning outcomes or pedagogy behind the product, not just the technology.",
            "Clarify who the buyer is - the institution, the parent, or the learner.",
        ],
        "E-commerce": [
            "Address logistics, fulfillment, and customer acquisition cost.",
            "Clarify your margin structure versus existing marketplaces.",
        ],
        "AgriTech": [
            "Explain last-mile reach to farmers with limited connectivity or literacy.",
            "Clarify how you build trust with a traditionally offline customer base.",
        ],
        "SaaS / Enterprise Tech": [
            "Clarify your pricing tiers, churn rate, and customer acquisition cost.",
            "Explain integration effort and switching cost for enterprise buyers.",
        ],
        "Food & Beverage": [
            "Address supply chain, perishability, and unit economics per order.",
            "Clarify your differentiation versus existing delivery platforms.",
        ],
        "Transportation & Logistics": [
            "Explain your fleet/asset ownership model (owned vs. partner network).",
            "Clarify how you handle scale, routing efficiency, and delivery SLAs.",
        ],
    }

    def __init__(self, text):
        self.text = (text or "").lower()

    def _keyword_hits(self):
        hits = {}
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in self.text)
            if count:
                hits[industry] = count
        return hits

    def classify(self):
        hits = self._keyword_hits()

        if not hits:
            return {
                "industry": "General / Uncategorized",
                "confidence": "Low",
                "tips": [
                    "Name the specific industry or vertical you're targeting - it helps investors calibrate expectations.",
                ],
            }

        industry = max(hits, key=hits.get)
        top_hits = hits[industry]
        confidence = "High" if top_hits >= 3 else "Moderate" if top_hits == 2 else "Low"

        return {
            "industry": industry,
            "confidence": confidence,
            "tips": self.INDUSTRY_TIPS.get(industry, []),
        }


def classify_industry(text):
    return IndustryClassifier(text).classify()
