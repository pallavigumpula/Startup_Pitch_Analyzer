class InsightGenerator:
    """Generates improvement suggestions and investor-style questions from
    which pitch sections are present or missing."""

    def __init__(self, sections):
        self.sections = sections

    def suggestions(self):
        suggestions = []

        if not self.sections.get("problem"):
            suggestions.append("Clearly define the problem your startup is solving.")

        if not self.sections.get("solution"):
            suggestions.append("Explain your solution in detail.")

        if not self.sections.get("market"):
            suggestions.append("Specify your target market and audience.")

        if not self.sections.get("business_model"):
            suggestions.append("Describe how your startup generates revenue.")

        if not self.sections.get("competition"):
            suggestions.append("Include competitor analysis and your unique advantage.")

        if not self.sections.get("team"):
            suggestions.append("Highlight your team and their expertise.")

        if not suggestions:
            suggestions.append("Your pitch looks strong. Consider adding more data and metrics.")

        return suggestions

    def questions(self):
        questions = []

        if not self.sections.get("competition"):
            questions.append("Who are your main competitors?")

        if not self.sections.get("business_model"):
            questions.append("How do you plan to generate revenue?")

        if not self.sections.get("market"):
            questions.append("What is your target market size?")

        if self.sections.get("solution"):
            questions.append("What makes your solution unique?")

        if self.sections.get("team"):
            questions.append("What experience does your team bring?")

        return questions


def generate_suggestions(sections):
    return InsightGenerator(sections).suggestions()


def generate_questions(sections):
    return InsightGenerator(sections).questions()
