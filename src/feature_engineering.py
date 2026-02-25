def add_features(df):
    df['water_stress'] = df['average_rain_fall_mm_per_year'] / df['avg_temp']
    df["rain_temp_interaction"] = df['average_rain_fall_mm_per_year'] * df['avg_temp']
    df["input_intensity"] = df["pesticides_tonnes_log"] / df["average_rain_fall_mm_per_year"]
    df["pest_temp_interaction"] = df["pesticides_tonnes_log"] * df["avg_temp"]
    return df