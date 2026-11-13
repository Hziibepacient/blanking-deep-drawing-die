"""Arithmetic review added on 2026-11-13, not an original course deliverable.

Run from any directory with Python 3. No external packages are required.
This script does not validate empirical coefficients or manufacturing feasibility.
"""

import json
import math


def calculate():
    # Parameters transcribed from the report; lengths in mm, stresses in N/mm^2.
    blank_d = 141.0
    mean_d = 109.0
    thickness = 1.0
    strip_width = 144.0
    pitch = 141.8
    report_pi = 3.14

    blanking = 1.3 * report_pi * blank_d * thickness * 300 / 1000
    drawing = report_pi * mean_d * thickness * 520 / 1000
    holding = report_pi / 4 * (blank_d**2 - (mean_d + thickness + 2*2)**2) * 3 / 1000
    first_cut = math.floor(1500 / strip_width) * math.floor(1000 / pitch)
    second_cut = math.floor(1000 / strip_width) * math.floor(1500 / pitch)
    die_edge = blank_d - 0.5 * 0.90
    punch_edge = die_edge - 0.16

    return {
        "review_date": "2026-11-13",
        "scope": "Arithmetic only; report inputs are not independently validated.",
        "source": "docs/design-report.pdf (PDF page numbers)",
        "checks": [
            {"name": "drawing_ratio", "pages": [4], "expression": "109/141",
             "calculated": mean_d / blank_d, "report_approximation": 0.77},
            {"name": "relative_thickness_percent", "pages": [4], "expression": "1/141*100",
             "calculated": thickness / blank_d * 100, "report_approximation": 0.7},
            {"name": "blanking_edge_nominal_mm", "pages": [4, 5],
             "die": die_edge, "punch": punch_edge,
             "diametral_clearance": die_edge-punch_edge,
             "tolerance_sum": 0.010+0.015, "clearance_range_width": 0.22-0.16},
            {"name": "blanking_force_kN", "pages": [5],
             "expression": "1.3*3.14*141*1*300/1000",
             "calculated": blanking, "report_value": 172.8},
            {"name": "drawing_force_kN", "pages": [5],
             "expression": "3.14*109*1*520/1000",
             "calculated": drawing, "report_value": 80.35},
            {"name": "blank_holder_force_kN", "pages": [5],
             "expression": "3.14/4*(141**2-(109+1+2*2)**2)*3/1000",
             "calculated": holding, "report_value": 14.03},
            {"name": "drawing_plus_holding_kN", "pages": [5, 6],
             "calculated": drawing+holding, "report_page_6_value": 158.05,
             "calculated_sum_less_than_blanking": drawing+holding < blanking,
             "warning": "Actual peak press load depends on the process sequence and stroke."},
            {"name": "sheet_cut_comparison", "pages": [6],
             "first_direction_count": first_cut, "second_direction_count": second_cut},
            {"name": "nominal_blank_area_share_percent", "pages": [4, 6],
             "expression": "70*pi*141**2/4/(1000*1500)*100",
             "calculated": first_cut*math.pi*blank_d**2/4/(1000*1500)*100,
             "origin": "Added in portfolio review; not finished-part material utilization."},
        ],
    }


if __name__ == "__main__":
    print(json.dumps(calculate(), ensure_ascii=False, indent=2, allow_nan=False))
