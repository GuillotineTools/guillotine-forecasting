#!/usr/bin/env python3
"""
Verify that all 7 tournaments are properly configured in main.py
"""

import re

def check_tournament_integration():
    print("🔍 Checking tournament integration in main.py...")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # List of expected tournaments
    expected_tournaments = [
        ('ai_comp_questions', 'AI Competition'),
        ('minibench_questions', 'MiniBench'),
        ('fall_aib_questions', 'Fall AIB 2025'),
        ('potus_questions', 'POTUS Predictions'),
        ('rand_questions', 'RAND Policy Challenge'),
        ('market_pulse_questions', 'Market Pulse Challenge 25Q4'),
        ('kiko_questions', 'Kiko Llaneras Tournament')
    ]
    
    # Check for tournament question variables
    print("\n📋 Tournament question variables:")
    all_found = True
    for var_name, display_name in expected_tournaments:
        if var_name in content:
            print(f"  ✅ {var_name} - {display_name}")
        else:
            print(f"  ❌ {var_name} - {display_name}")
            all_found = False
    
    # Check for tournament report variables
    print("\n📊 Tournament report variables:")
    report_vars = [
        'seasonal_tournament_reports',
        'minibench_reports', 
        'fall_aib_reports',
        'potus_reports',
        'rand_reports',
        'market_pulse_reports',
        'kiko_reports'
    ]
    
    for var in report_vars:
        if var in content:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var}")
            all_found = False
    
    # Check final aggregation
    print("\n🔗 Final forecast aggregation:")
    aggregation_pattern = r'forecast_reports = (.+)'
    match = re.search(aggregation_pattern, content)
    if match:
        aggregation_line = match.group(1)
        included_reports = []
        for var in report_vars:
            if var in aggregation_line:
                included_reports.append(var)
        
        print(f"  Found aggregation: {aggregation_line}")
        print(f"  Included reports: {len(included_reports)}/{len(report_vars)}")
        
        for var in report_vars:
            if var in aggregation_line:
                print(f"    ✅ {var}")
            else:
                print(f"    ❌ {var} (missing from aggregation)")
                all_found = False
    else:
        print("  ❌ Could not find forecast_reports aggregation")
        all_found = False
    
    # Check logging statement
    print("\n📝 Tournament logging:")
    logging_pattern = r'Found questions: AI Comp:.*, MiniBench:.*, Fall AIB:.*, POTUS:.*, RAND:.*, Market Pulse:.*, Kiko:.*'
    if re.search(logging_pattern, content):
        print("  ✅ Complete tournament logging found")
    else:
        print("  ❌ Incomplete tournament logging")
        all_found = False
    
    # Overall result
    print(f"\n🎯 Overall result: {'✅ PASS' if all_found else '❌ FAIL'}")
    return all_found

if __name__ == "__main__":
    success = check_tournament_integration()
    exit(0 if success else 1)