def process_user_records(raw_data_string):
    if not raw_data_string:
        return {"valid_count": 0, "total_score": 0, "errors": []}
    
    records = raw_data_string.strip().split(";")
    valid = 0
    score_sum = 0
    errors = []

    for item in records:
        if not item:
            continue
        parts = item.split(",")
        if len(parts) != 3:
            errors.append(f"Invalid segment: {item}")
            continue
        
        uid, age_str, score_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
        
        if not uid.isalnum():
            errors.append(f"Invalid UID: {uid}")
            continue

        try:
            age = int(age_str)
            if age < 18 or age > 100:
                errors.append(f"Out of range age: {age}")
                continue
        except ValueError:
            errors.append(f"Non-integer age: {age_str}")
            continue

        try:
            score = float(score_str)
            if score < 0.0:
                errors.append(f"Negative score: {score}")
                continue
            score_sum += score
            valid += 1
        except ValueError:
            errors.append(f"Non-numeric score: {score_str}")
            continue

    return {
        "valid_count": valid,
        "total_score": round(score_sum, 2),
        "errors": errors
    }