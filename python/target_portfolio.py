
import json
import sys

# For target portfolio calculations, ratios are taken directly from people.json for each person.
# It is easier to edit the ratios in the JSON file than to enter them one by one here.

# File paths
ASSET_FILE = "data/asset_info.json"
PEOPLE_FILE = "data/people.json"


def load_file(file_path):
    """
    Loads the specified JSON file and returns its content.
    Returns None if file is missing or invalid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please create the file first.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        return None

def validate_portfolio_percentages(portfolio_dict):
    """
    Checks if the sum of percentages in the given portfolio dict is 1.0 (100%).
    Returns True if valid, False otherwise.
    """
    total_percent = sum(portfolio_dict.values())
    if not (0.999 < total_percent < 1.001):
        print("\nWARNING: Portfolio percentages do not sum to 100%!")
        print(f"Calculated Total Percentage: %{total_percent * 100:.2f}")
        return False
    return True

def calculate_portfolio_risk(target_portfolio, asset_info):
    """
    Calculates the total risk of the portfolio based on asset risk scores.
    Returns the weighted average risk score.
    """
    total_risk_score = 0
    for asset, percent in target_portfolio.items():
        if asset in asset_info:
            risk_score = asset_info[asset].get('risk_score', asset_info[asset].get('risk_puani', 0))
            total_risk_score += percent * risk_score
        else:
            print(f"WARNING: Asset '{asset}' not found in '{ASSET_FILE}'. Not included in risk calculation.")
    return total_risk_score

def calculate_portfolio_return(portfolio_distribution, asset_info, scenario='base'):
    """
    Varlık getirileri ve kur artışına göre portföyün toplam beklenen getirisini hesaplar.
    Kur artışı beklentisini "USD TRY Based" varlığından alır.
    """
    if not portfolio_distribution: return 0
    
    scenario_keys = {
        "base": "expected_percentage_return",
        "good": "good_scenario_return",
        "bad": "bad_scenario_return"
    }
    key = scenario_keys.get(scenario, "expected_percentage_return")
    
    total_return_percent = 0
    
    # --- DEĞİŞİKLİK BURADA ---
    # Kur artışı beklentisi artık "USD TRY Based" varlığından alınıyor.
    usd_try_return_expectation = asset_info.get("USD TRY Based", {}).get(key, 0)
    
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            # "USD TRY Based" varlığının kendisi, zaten kur artışını temsil ettiği için
            # ayrıca bir birleştirme işlemine tabi tutulmaz.
            if asset == "USD TRY Based":
                total_return_percent += percent * usd_try_return_expectation
                continue

            asset_return = asset_info[asset].get(key, 0)
            is_usd_based = asset_info[asset].get('is_usd_based', False)
            
            if is_usd_based:
                # Dolar bazlı diğer varlıkların getirisi, kur artışıyla birleştirilir.
                combined_return = (1 + asset_return) * (1 + usd_try_return_expectation) - 1
                total_return_percent += percent * combined_return
            else:
                # TL bazlı varlıkların getirisi doğrudan eklenir.
                total_return_percent += percent * asset_return
                
    return total_return_percent

def show_distribution_and_report(name, principal, target_portfolio, asset_info):
    """
    Calculates and prints the investment distribution, risk, and return based on the given info.
    """
    print("\n" + "="*50)
    print(f"Person: {name}")
    print(f"Principal: {principal:,.2f} TL")
    print("--- Target Investment Distribution ---")

    for asset, percent in target_portfolio.items():
        required_amount = principal * percent
        risk_score = asset_info.get(asset, {}).get('risk_score', 'Unknown')
        expected_return = asset_info.get(asset, {}).get('expected_return_description', 'Unknown')
        print(f"{asset:<20}: {required_amount:>15,.2f} TL (%{percent*100:.0f})")
        print(f"{' ':<20} Risk: {risk_score:<2} / 10 | Return: {expected_return}")

    total_portfolio_risk = calculate_portfolio_risk(target_portfolio, asset_info)
    total_portfolio_return = calculate_portfolio_return(target_portfolio, asset_info)
    print("-" * 50)
    print(f"Weighted Average Portfolio Risk: {total_portfolio_risk:.2f} / 10")
    print(f"Annual (TL Based) Portfolio Return Expectation: %{total_portfolio_return * 100:.2f}")
    print("="*50)

# --- Main Program ---
if __name__ == "__main__":
    people = load_file(PEOPLE_FILE)
    asset_info = load_file(ASSET_FILE)
    if people is None or asset_info is None:
        sys.exit()

    print("Please select the person whose portfolio you want to view:")
    for i, person in enumerate(people):
        print(f"{i + 1}: {person['name']}")

    while True:
        try:
            selection_str = input("\nYour selection (number): ")
            selection = int(selection_str)
            if 1 <= selection <= len(people):
                selected_person = people[selection - 1]
                break
            else:
                print("Please enter a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    person_name = selected_person['name']
    person_principal = selected_person['principal']
    person_target_portfolio = selected_person['target_portfolio']

    if validate_portfolio_percentages(person_target_portfolio):
        show_distribution_and_report(person_name, person_principal, person_target_portfolio, asset_info)
    else:
        print(f"\nPortfolio configuration for {person_name} is invalid. No operation performed.")