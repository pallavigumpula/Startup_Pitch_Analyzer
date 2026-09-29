def pvb_check(sections):
    required = ["problem", "solution", "market"]

    missing = [sec for sec in required if not sections.get(sec)]

    if not missing:
        return "PVB Passed"
    else:
        return f"PVB Failed - Missing: {missing}"