def calculate_aqi(co2: float, temperature: float, humidity: float) -> float:

    co2_score = max(0, min(100, (co2 - 400) / 16))
    

    if 20 <= temperature <= 24:
        temp_score = 0
    else:
        temp_score = min(100, abs(temperature - 22) * 10)
        

    if 40 <= humidity <= 60:
        hum_score = 0
    else:
        hum_score = min(100, abs(humidity - 50) * 2)
        

    total_score = (co2_score * 0.7) + (temp_score * 0.2) + (hum_score * 0.1)
    return round(total_score, 1)
