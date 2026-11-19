"""
Mine Rescue & Safety Monitoring System (MRSMS)
Prediction Engine Module (Python Edition)

Calibrated to MSHA & OSHA Title 30 underground mining safety standards.
Calculates accumulation velocity, 10-minute predictive forecast,
and composite Tunnel Safety Index (0-100).
"""

# Regulatory Safety Thresholds
THRESHOLDS = {
    'ch4_caution': 5000.0,    # 10% LEL (Combustible threshold)
    'ch4_critical': 10000.0,  # 20% LEL (Mandatory Evacuation)
    'co_caution': 35.0,       # 8-hr Time-Weighted Average (TWA)
    'co_critical': 100.0,     # Lethal Combustion Ceiling
    'so2_caution': 5.0,       # Acidic gas caution limit
    'so2_critical': 20.0,     # Immediately Dangerous to Life & Health (IDLH)
    'co2_caution': 2500.0,    # Air quality caution
    'co2_critical': 5000.0,   # Asphyxiant limit
    'o2_caution': 19.5,       # Minimum safe breathing threshold
    'o2_critical': 16.0,      # Acute Asphyxiation Hazard
    'dist_caution': 180.0,    # Convergence caution (cm)
    'dist_critical': 100.0    # Impending cave-in ceiling (cm)
}


def calculate_safety_index(telemetry):
    """
    Computes a composite Tunnel Safety Index from 0 to 100
    using standard penalty deductions.
    """
    if not telemetry:
        return 100

    score = 100

    # 1. Structural Roof Clearance (Ultrasonic)
    dist = telemetry.get('distance_cm', 215.0)
    if dist < THRESHOLDS['dist_critical']:
        score -= 45
    elif dist < THRESHOLDS['dist_caution']:
        score -= 15

    # 2. Methane (CH4)
    ch4 = telemetry.get('ch4_ppm', 650.0)
    if ch4 >= THRESHOLDS['ch4_critical']:
        score -= 45
    elif ch4 >= THRESHOLDS['ch4_caution']:
        score -= 25

    # 3. Carbon Monoxide (CO)
    co = telemetry.get('co_ppm', 8.0)
    if co >= THRESHOLDS['co_critical']:
        score -= 40
    elif co >= THRESHOLDS['co_caution']:
        score -= 15

    # 4. Sulphur Dioxide (SO2)
    so2 = telemetry.get('so2_ppm', 1.5)
    if so2 >= THRESHOLDS['so2_critical']:
        score -= 35
    elif so2 >= THRESHOLDS['so2_caution']:
        score -= 15

    # 5. Oxygen (O2)
    o2 = telemetry.get('o2_percent', 20.9)
    if o2 <= THRESHOLDS['o2_critical']:
        score -= 40
    elif o2 < THRESHOLDS['o2_caution']:
        score -= 20

    # 6. Battery Level
    batt = telemetry.get('battery', 95)
    if batt < 20:
        score -= 10

    return max(0, min(100, int(score)))


def forecast_gas(history, key='ch4_ppm', caution_limit=5000.0, critical_limit=10000.0, is_decreasing=False):
    """
    Calculates rate of change per minute and projects 10-minute forward values.
    """
    if not history or len(history) < 2:
        val = history[-1].get(key, 0) if history else 0
        return {
            'current_value': val,
            'rate_per_min': 0.0,
            'predicted_10m': val,
            'time_to_critical_sec': None,
            'hazard_level': 'NORMAL',
            'projected_points': []
        }

    # Window of recent samples (up to 30 points)
    window = history[-min(30, len(history)):]
    current_val = window[-1].get(key, 0.0)
    oldest_val = window[0].get(key, 0.0)

    # Telemetry interval ~ 1.2 seconds per sample
    elapsed_minutes = (len(window) * 1.2) / 60.0
    rate_per_min = (current_val - oldest_val) / elapsed_minutes if elapsed_minutes > 0 else 0.0

    # 10-minute projection with 0.85 dispersion damping factor
    predicted_10m = max(0.0, current_val + (rate_per_min * 10.0 * 0.85))

    time_to_critical_sec = None
    if not is_decreasing and rate_per_min > 0.1:
        if current_val < critical_limit:
            time_to_critical_sec = int(((critical_limit - current_val) / rate_per_min) * 60.0)
    elif is_decreasing and rate_per_min < -0.01:
        if current_val > critical_limit:
            time_to_critical_sec = int(((current_val - critical_limit) / abs(rate_per_min)) * 60.0)

    # Determine hazard level
    hazard_level = 'NORMAL'
    if not is_decreasing:
        if current_val >= critical_limit or (time_to_critical_sec and time_to_critical_sec < 300):
            hazard_level = 'CRITICAL'
        elif current_val >= caution_limit or (time_to_critical_sec and time_to_critical_sec < 600):
            hazard_level = 'CAUTION'
    else:
        if current_val <= critical_limit or (time_to_critical_sec and time_to_critical_sec < 300):
            hazard_level = 'CRITICAL'
        elif current_val <= caution_limit or (time_to_critical_sec and time_to_critical_sec < 600):
            hazard_level = 'CAUTION'

    # Generate forward minute steps (1m, 2m, 3m, 5m, 8m, 10m)
    projected_points = []
    for m in [1, 2, 3, 5, 8, 10]:
        val = max(0.0, current_val + (rate_per_min * m * 0.88))
        projected_points.append({'minute': m, 'predicted_value': round(val, 1)})

    return {
        'current_value': round(current_val, 1),
        'rate_per_min': round(rate_per_min, 2),
        'predicted_10m': round(predicted_10m, 1),
        'time_to_critical_sec': time_to_critical_sec,
        'hazard_level': hazard_level,
        'projected_points': projected_points
    }
