def predict_success_probability(score, sections):
    """Heuristic startup success / investor-interest probability.

    Blends the overall pitch score with how many of the expected sections
    are actually present, so a high score built on only one or two strong
    sections doesn't read as a fully investor-ready idea.
    """
    total_sections = len(sections) or 1
    completeness = sum(1 for present in sections.values() if present) / total_sections

    probability = round(min(97, max(3, score * 0.7 + completeness * 30)), 1)

    if probability >= 75:
        label = "High potential for investor interest"
    elif probability >= 50:
        label = "Moderate potential - worth refining further"
    else:
        label = "Low potential - significant improvements needed"

    return {"probability": probability, "label": label}
