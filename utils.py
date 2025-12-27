import pandas as pd

def load_data(path):
    """Load dataset from CSV"""
    return pd.read_csv(path)

def get_available_crops(df):
    """Return list of unique crops"""
    return sorted(df['label'].str.lower().unique())

def get_sample_for_crop(df, crop_name):
    """Return random sample row for selected crop"""
    return df[df['label'].str.lower() == crop_name].sample(1).iloc[0]

def check_parameters(crop_name, parameters, thresholds, fertilizers):
    """
    Check nutrient and climate parameters, suggest fertilizers.
    """
    if crop_name not in thresholds:
        return [f"Crop '{crop_name}' is not supported."]
    
    limits = thresholds[crop_name]
    ferts = fertilizers.get(crop_name, {})
    alerts = []

    for param, value in parameters.items():
        lower, upper = limits.get(param, (None, None))
        if lower is None or upper is None:
            continue
        
        if value < lower:
            msg = f"{param.upper()} is LOW ({value}) → Recommended ≥ {lower}"
            msg += f" → Suggest: {ferts.get(param, 'Consult agronomist')}"
            alerts.append(msg)
        elif value > upper:
            msg = f"{param.upper()} is HIGH ({value}) → Recommended ≤ {upper}"
            alerts.append(msg)
        
        # Special handling for pH
        if param.lower() == 'ph':
            if value < 5.5:
                alerts.append(f"pH is too acidic ({value}) → Suggest: {ferts.get('pH_low', 'Apply Lime')}")
            elif value > 8.0:
                alerts.append(f"pH is too alkaline ({value}) → Suggest: {ferts.get('pH_high', 'Apply Sulfur')}")
            elif 6.0 <= value <= 7.5:
                alerts.append("pH is ideal for most crops.")
    
    if not alerts:
        alerts.append("All parameters are healthy.")
    
    return alerts
