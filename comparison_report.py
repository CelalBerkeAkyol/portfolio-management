
# English version, updated for new JSON structure
import json
import sys

PEOPLE_FILE = "data/people.json"
ASSET_FILE = "data/asset_info.json"

def load_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                print(f"Error: '{file_path}' is empty.")
                return [] if 'people.json' in file_path else {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please check the file location.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        return None

def select_person(people):
    if not people:
        print("No registered person found. Please add a person first.")
        return None
    print("\nPlease select the person whose report you want to see:")
    for i, person in enumerate(people):
        print(f"{i + 1}: {person['name']}")
    while True:
        try:
            selection_str = input("\nYour selection (number): ")
            selection = int(selection_str)
            if 1 <= selection <= len(people):
                return people[selection - 1]
            else:
                print(f"Please enter a number between 1 and {len(people)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_portfolio_risk(portfolio_distribution, asset_info):
    total_risk_score = 0
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            risk_score = asset_info[asset].get('risk_score', asset_info[asset].get('risk_puani', 0))
            total_risk_score += percent * risk_score
    return total_risk_score

def calculate_portfolio_return(portfolio_distribution, asset_info, scenario='base'):
    scenario_keys = {
        "base": "expected_percentage_return",
        "good": "good_scenario_return",
        "bad": "bad_scenario_return"
    }
    key = scenario_keys.get(scenario, "expected_percentage_return")
    total_return_percent = 0
    usd_return_expectation = asset_info.get("USD Based Interest", {}).get(key, 0)
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            asset_return = asset_info[asset].get(key, 0)
            usd_based = asset_info[asset].get('is_usd_based', False)
            if usd_based:
                combined_return = (1 + asset_return) * (1 + usd_return_expectation) - 1
                total_return_percent += percent * combined_return
            else:
                total_return_percent += percent * asset_return
    return total_return_percent

def show_scenario_analysis(principal, current_dist, target_dist, asset_info):
    print("\n" + "-"*110)
    print("SCENARIO ANALYSIS (Annual TL-Based Return and Portfolio Value)".center(110))
    print("-" * 110)
    print(f"{'SCENARIO':<20} | {'CURRENT PORTFOLIO':^42} | {'TARGET PORTFOLIO':^42}")
    print(f"{'':<20} | {'% Return':^20} | {'Final Value (TL)':>20} | {'% Return':^20} | {'Final Value (TL)':>20}")
    print("-" * 110)

    scenarios = [
        ("Bad Scenario", "bad"),
        ("Base Scenario", "base"),
        ("Good Scenario", "good")
    ]

    for scenario_name, scenario_code in scenarios:
        current_return = calculate_portfolio_return(current_dist, asset_info, scenario=scenario_code)
        current_final = principal * (1 + current_return)
        target_return = calculate_portfolio_return(target_dist, asset_info, scenario=scenario_code)
        target_final = principal * (1 + target_return)
        print(
            f"{scenario_name:<20} | "
            f"{current_return*100:^19.2f}% | {current_final:>20,.2f} | "
            f"{target_return*100:^19.2f}% | {target_final:>20,.2f}"
        )

def show_comparison_report(name, principal, current_dist, target_dist, asset_info):
    print("\n" + "="*110)
    print(f"Person: {name}".center(110))
    print(f"Principal: {principal:,.2f} TL".center(110))
    print("="*110)
    print("PORTFOLIO DISTRIBUTION COMPARISON".center(110))
    print("-" * 110)
    print(f"{'ASSET':<20} | {'CURRENT':^30} | {'TARGET':^30} | {'CHANGE (Buy/Sell)':^25}")
    print("-" * 110)

    all_assets = list(set(current_dist.keys()) | set(target_dist.keys()))
    # Prepare a list of (asset, abs(change), change, current, target) for sorting
    asset_changes = []
    for asset in all_assets:
        current_percent = current_dist.get(asset, 0)
        current_amount = current_percent * principal
        target_percent = target_dist.get(asset, 0)
        target_amount = target_percent * principal
        diff_amount = target_amount - current_amount
        asset_changes.append((asset, diff_amount, diff_amount, current_percent, target_percent, current_amount, target_amount))
    # Sort by absolute value of change, descending
    asset_changes.sort(key=lambda x: x[1], reverse=True)
    for asset, _, diff_amount, current_percent, target_percent, current_amount, target_amount in asset_changes:
        current_str = f"{current_amount:,.2f} TL (%{current_percent*100:.1f})"
        target_str = f"{target_amount:,.2f} TL (%{target_percent*100:.1f})"
        diff_str = f"{diff_amount:+,.2f} TL" if abs(diff_amount) > 0.01 else ""
        print(f"{asset:<20} | {current_str:>30} | {target_str:>30} | {diff_str:>25}")

    print("-" * 110)
    current_risk = calculate_portfolio_risk(current_dist, asset_info)
    target_risk = calculate_portfolio_risk(target_dist, asset_info)
    current_total_str = f"Total: {principal:,.2f} TL"
    target_total_str = f"Total: {principal:,.2f} TL"
    print(f"{'':<20} | {current_total_str:>30} | {target_total_str:>30} | {'':>25}")
    current_risk_str = f"Avg. Risk: {current_risk:.2f}/10"
    target_risk_str = f"Avg. Risk: {target_risk:.2f}/10"
    print(f"{'RISK SCORE':<20} | {current_risk_str:>30} | {target_risk_str:>30} | {'':>25}")
    show_scenario_analysis(principal, current_dist, target_dist, asset_info)
    print("=" * 110)

if __name__ == "__main__":
    people_list = load_file(PEOPLE_FILE)
    asset_info = load_file(ASSET_FILE)
    if people_list is None or asset_info is None:
        sys.exit("Program stopped due to file read error.")

    selected_person = select_person(people_list)
    if selected_person:
        name = selected_person['name']
        principal = selected_person['principal']
        current_dist = selected_person.get('current_portfolio_distribution')
        target_dist = selected_person.get('target_portfolio')
        if current_dist and target_dist:
            show_comparison_report(
                name,
                principal,
                current_dist,
                target_dist,
                asset_info
            )
        else:
            print("\nCurrent and/or target portfolio information is missing.")
            print("Comparison report could not be generated.")
            print("Please make sure you have run both 'current_portfolio.py' and 'target_portfolio.py'.")