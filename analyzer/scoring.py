import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyzer.section_detection import SectionDetector

WEIGHTS = {
    "problem": 15,
    "solution": 20,
    "market": 15,
    "business_model": 20,
    "competition": 10,
    "team": 20
}

# Canonical description of what a well-written section should cover.
# Each sentence of the pitch is compared against these via TF-IDF cosine
# similarity to score semantic relevance, not just keyword presence.
REFERENCE_TEXT = {
    "problem": "a clear problem or pain point that customers face today and why it matters",
    "solution": "a product or service solution and how it effectively solves the stated problem",
    "market": "the target market customer segments market size and addressable opportunity",
    "business_model": "the revenue model pricing strategy subscription plans and how the business makes money",
    "competition": "existing competitors alternative solutions and the unique competitive advantage",
    "team": "the founding team their experience technical expertise and track record"
}


class PitchScorer:
    """Scores each pitch section by blending keyword coverage with TF-IDF
    semantic similarity against a reference description, then weighting the
    result per section (NumPy is used for the vectorised weighting math)."""

    def __init__(self, sections, text):
        self.sections = sections
        self.text = text.lower()
        self.detector = SectionDetector(text)

    def _split_sentences(self):
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", self.text) if s.strip()]
        return sentences or ([self.text.strip()] if self.text.strip() else [])

    def _max_similarity_per_section(self):
        sections = list(REFERENCE_TEXT.keys())
        sentences = self._split_sentences()

        if not sentences:
            return {s: 0.0 for s in sections}

        corpus = sentences + [REFERENCE_TEXT[s] for s in sections]

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform(corpus)
        except ValueError:
            # Empty vocabulary (e.g. pitch text is only stopwords/numbers)
            return {s: 0.0 for s in sections}

        sentence_vectors = tfidf[:len(sentences)]
        reference_vectors = tfidf[len(sentences):]

        similarity_matrix = cosine_similarity(sentence_vectors, reference_vectors)
        max_per_section = np.asarray(similarity_matrix).max(axis=0)

        return dict(zip(sections, max_per_section))

    def score(self):
        similarity = self._max_similarity_per_section()

        section_names = list(WEIGHTS.keys())
        weights = np.array([WEIGHTS[s] for s in section_names], dtype=float)
        keyword_ratios = np.array([self.detector.keyword_ratio(s) for s in section_names])
        similarity_ratios = np.array([similarity.get(s, 0.0) for s in section_names])

        combined_ratio = np.clip(0.6 * keyword_ratios + 0.4 * similarity_ratios, 0.0, 1.0)
        section_scores = np.round(weights * combined_ratio, 2)

        scores = dict(zip(section_names, (float(v) for v in section_scores)))
        total = round(float(section_scores.sum()), 2)

        return scores, total


def calculate_score(sections, text):
    return PitchScorer(sections, text).score()
