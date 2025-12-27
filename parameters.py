# parameters.py

# Safe lower and upper thresholds for selected crops
thresholds = {
    'rice': {
        'N': (80, 120), 'P': (40, 60), 'K': (40, 80),
        'temperature': (20, 35), 'humidity': (70, 90),
        'ph': (5.5, 7.0), 'rainfall': (150, 300)
    },
    'cotton': {
        'N': (50, 90), 'P': (30, 60), 'K': (30, 60),
        'temperature': (25, 35), 'humidity': (60, 80),
        'ph': (6.0, 7.5), 'rainfall': (50, 150)
    },
    'apple': {
        'N': (60, 110), 'P': (20, 200), 'K': (30, 210),
        'temperature': (22, 35), 'humidity': (50, 80),
        'ph': (6.5, 7.5), 'rainfall': (100, 250)
    },
    'maize': {
        'N': (70, 110), 'P': (30, 50), 'K': (35, 60),
        'temperature': (18, 32), 'humidity': (50, 75),
        'ph': (5.8, 7.2), 'rainfall': (75, 200)
    },
    'jute': {
        'N': (80, 120), 'P': (35, 55), 'K': (35, 65),
        'temperature': (22, 34), 'humidity': (75, 90),
        'ph': (6.2, 7.4), 'rainfall': (120, 250)
    }
}

# Fertilizer recommendations for each crop and parameter
fertilizers = {
    'rice': {
        'N': 'Urea',
        'P': 'Single Super Phosphate (SSP)',
        'K': 'Muriate of Potash (MOP)',
        'pH_low': 'Lime (Calcium Carbonate)',
        'pH_high': 'Sulfur or Aluminum Sulfate'
    },
    'cotton': {
        'N': 'Ammonium Sulfate',
        'P': 'Diammonium Phosphate (DAP)',
        'K': 'Sulphate of Potash (SOP)',
        'pH_low': 'Dolomite',
        'pH_high': 'Sulfur'
    },
    'apple': {
        'N': 'Calcium Ammonium Nitrate',
        'P': 'Rock Phosphate',
        'K': 'Potassium Sulphate',
        'pH_low': 'Wood ash or Lime',
        'pH_high': 'Sulfur'
    },
    'maize': {
        'N': 'Urea',
        'P': 'Diammonium Phosphate (DAP)',
        'K': 'Muriate of Potash (MOP)',
        'pH_low': 'Agricultural Lime',
        'pH_high': 'Sulfur'
    },
    'jute': {
        'N': 'Ammonium Nitrate',
        'P': 'Single Super Phosphate (SSP)',
        'K': 'Muriate of Potash (MOP)',
        'pH_low': 'Dolomitic Lime',
        'pH_high': 'Sulfur'
    }
}
