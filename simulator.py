"""
Mine Rescue & Safety Monitoring System (MRSMS)
Telemetry Simulator Module (Python Edition)

Generates stochastic Brownian motion sensor data for underground mining drifts,
with support for simulated hazard scenarios:
- NORMAL
- METHANE_SURGE
- CAVE_IN
- FIRE_OUTBREAK
"""

import random
from datetime import datetime, timedelta

DEFAULT_SECTORS = [
    {
        'node_id': 'NODE-01',
        'sector_name': 'Sector 4 - Sub-level B Extraction Stope',
        'elevation_m': -420,
        'status': 'ACTIVE'
    },
    {
        'node_id': 'NODE-02',
        'sector_name': 'Sector 2 - Level 300 Deep Drift',
        'elevation_m': -300,
        'status': 'ACTIVE'
    },
    {
        'node_id': 'NODE-03',
        'sector_name': 'Sector 7 - North Airway Shaft',
        'elevation_m': -180,
        'status': 'ACTIVE'
    },
    {
        'node_id': 'NODE-04',
        'sector_name': 'Sector 5 - East Refuge Chamber',
        'elevation_m': -350,
        'status': 'ACTIVE'
    }
]


def generate_initial_history(count=40):
    """
    Generates historical data points leading up to the current moment.
    """
    history = []
    now = datetime.now()
    dist = 215.0
    ch4 = 650.0
    co = 8.5
    so2 = 1.8
    co2 = 420.0
    o2 = 20.88

    for i in range(count, 0, -1):
        ts = now - timedelta(seconds=i * 2)
        dist = max(195.0, min(235.0, dist + (random.random() - 0.5) * 1.5))
        ch4 = max(400.0, min(1100.0, ch4 + (random.random() - 0.5) * 20.0))
        co = max(5.0, min(14.0, co + (random.random() - 0.5) * 0.4))
        so2 = max(0.5, min(3.5, so2 + (random.random() - 0.5) * 0.1))
        co2 = max(380.0, min(500.0, co2 + (random.random() - 0.5) * 8.0))
        o2 = max(20.7, min(20.95, o2 + (random.random() - 0.5) * 0.02))

        history.append({
            'timestamp': ts.strftime('%H:%M:%S'),
            'node_id': 'NODE-01',
            'sector_name': 'Sector 4 - Sub-level B',
            'distance_cm': round(dist, 1),
            'ch4_ppm': round(ch4, 1),
            'ch4_lel_percent': round((ch4 / 50000.0) * 100.0, 2),
            'co_ppm': round(co, 1),
            'so2_ppm': round(so2, 1),
            'co2_ppm': round(co2, 0),
            'o2_percent': round(o2, 2),
            'battery': 94,
            'rssi': -78
        })

    return history


def step_simulation(prev, scenario='NORMAL', step_count=1):
    """
    Computes the next telemetry sample based on the active scenario.
    """
    dist = prev.get('distance_cm', 215.0)
    ch4 = prev.get('ch4_ppm', 650.0)
    co = prev.get('co_ppm', 8.5)
    so2 = prev.get('so2_ppm', 1.8)
    co2 = prev.get('co2_ppm', 420.0)
    o2 = prev.get('o2_percent', 20.88)

    if scenario == 'METHANE_SURGE':
        # Rapid methane puncture from coal seam
        ch4 = min(18500.0, ch4 + 400.0 + random.random() * 250.0)
        co = min(45.0, co + random.random() * 2.0)
        o2 = max(18.0, o2 - 0.05)
    elif scenario == 'CAVE_IN':
        # Ultrasonic convergence towards collapse
        dist = max(45.0, dist - 6.5 + (random.random() - 0.5) * 2.0)
        ch4 += (random.random() - 0.2) * 50.0
    elif scenario == 'FIRE_OUTBREAK':
        # Toxic smoke combustion byproduct
        co = min(320.0, co + 12.0 + random.random() * 8.0)
        so2 = min(40.0, so2 + 1.2 + random.random() * 0.5)
        co2 = min(6000.0, co2 + 180.0)
        o2 = max(14.0, o2 - 0.12)
    else:
        # Normal stochastic drift
        dist = max(195.0, min(235.0, dist + (random.random() - 0.5) * 1.5))
        ch4 = max(400.0, min(1200.0, ch4 + (random.random() - 0.5) * 25.0))
        co = max(4.0, min(14.0, co + (random.random() - 0.5) * 0.4))
        so2 = max(0.5, min(4.0, so2 + (random.random() - 0.5) * 0.15))
        co2 = max(380.0, min(550.0, co2 + (random.random() - 0.5) * 10.0))
        o2 = max(20.7, min(20.95, o2 + (random.random() - 0.5) * 0.02))

    return {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'node_id': prev.get('node_id', 'NODE-01'),
        'sector_name': prev.get('sector_name', 'Sector 4 - Sub-level B'),
        'distance_cm': round(dist, 1),
        'ch4_ppm': round(ch4, 1),
        'ch4_lel_percent': round((ch4 / 50000.0) * 100.0, 2),
        'co_ppm': round(co, 1),
        'so2_ppm': round(so2, 1),
        'co2_ppm': round(co2, 0),
        'o2_percent': round(o2, 2),
        'battery': max(10, prev.get('battery', 95) - (1 if random.random() < 0.05 else 0)),
        'rssi': -78 + random.randint(-2, 2)
    }
