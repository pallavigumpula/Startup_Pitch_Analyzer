def check_eligibility(exp):
    exp = int(exp)

    if exp <= 1:
        return {"level": "Fresher", "multiplier": 0.7}

    elif exp <= 3:
        return {"level": "Beginner", "multiplier": 0.8}

    elif exp <= 5:
        return {"level": "Intermediate", "multiplier": 0.9}

    elif exp <= 7:
        return {"level": "Advanced", "multiplier": 1.0}

    else:
        return {"level": "Expert", "multiplier": 1.1}