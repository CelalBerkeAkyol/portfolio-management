import json
import sys

# File paths
PEOPLE_FILE = "data/people.json"
ASSET_FILE = "data/asset_info.json"

def load_file(file_path):
    """
    Loads the specified JSON file and returns its content.
    Returns an empty list/dict if file is missing or empty.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return [] if 'people.json' in file_path else {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Info: '{file_path}' not found. A new file will be created.")
        return [] if 'people.json' in file_path else {}
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        return None

def save_file(data, file_path):
    """
    Saves the given data to the specified JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data successfully saved to '{file_path}'.")

def select_person(people):
    """
    Lets the user select a person from the list and returns the selected person's dictionary.
    """
    if not people:
        print("No registered person found in the system.")
        return None

    print("\nPlease select the person whose portfolio you want to update:")
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

def get_number(message):
    """
    Repeatedly asks the user for a valid float number.
    """
    while True:
        try:
            value = float(input(message))
            return value
        except ValueError:
            print("Error: Please enter a numeric value only.")

def get_current_portfolio_info():
    """
    Gets the current portfolio info (amounts) from the user.
    """
    print("\nPlease enter your current asset amounts (in TL):")
    print("***Enter all values as numbers***\n")
    
    current_portfolio_amount = {}
    current_portfolio_amount["TRY Based Interest"] = get_number("TRY Based Interest / Money Market Fund amount: ")
    current_portfolio_amount["USD Based Interest"] = get_number("USD Based Interest / Foreign Money Market Fund amount: ")
    current_portfolio_amount["Gold"] = get_number("Gold amount: ")
    current_portfolio_amount["Silver"] = get_number("Silver amount: ")
    current_portfolio_amount["Turkish Fund"] = get_number("Turkish Fund amount: ")
    current_portfolio_amount["Turkish Stocks"] = get_number("Turkish Stocks amount: ")
    current_portfolio_amount["Real Estate"] = get_number("Real Estate / Real Estate Fund amount: ")
    current_portfolio_amount["Foreign Stocks"] = get_number("Foreign Stocks amount: ")
    current_portfolio_amount["Cryptocurrency"] = get_number("Cryptocurrency amount: ")

    return current_portfolio_amount

def calculate_portfolio_risk(portfolio_distribution, asset_info):
    """
    Calculates the total risk of the portfolio based on asset risk scores.
    """
    total_risk_score = 0
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            risk_score = asset_info[asset]['risk_score'] if 'risk_score' in asset_info[asset] else asset_info[asset].get('risk_puani', 0)
            total_risk_score += percent * risk_score
        else:
            print(f"WARNING: Asset '{asset}' not found in '{ASSET_FILE}'. Not included in risk calculation.")
    return total_risk_score

def calculate_portfolio_return(portfolio_distribution, asset_info):
    """
    Calculates the total expected return of the portfolio based on asset returns and currency appreciation.
    """
    total_return_percent = 0
    usd_return_expectation = asset_info.get("USD Based Interest", {}).get('expected_percentage_return', 0)
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            asset_return = asset_info[asset].get('expected_percentage_return', 0)
            usd_based = asset_info[asset].get('is_usd_based', False)
            if usd_based:
                combined_return = (1 + asset_return) * (1 + usd_return_expectation) - 1
                total_return_percent += percent * combined_return
            else:
                total_return_percent += percent * asset_return
        else:
            print(f"WARNING: Asset '{asset}' not found in '{ASSET_FILE}'. Not included in return calculation.")
    return total_return_percent

def show_portfolio_report(name, title, amount_distribution, percent_distribution, principal, asset_info):
    """
    Calculates and prints the investment distribution, risk, and return based on the given info.
    """
    print("\n" + "="*50)
    print(f"Person: {name}")
    print(f"Portfolio Type: {title}")
    print(f"Principal: {principal:,.2f} TL")
    print("--- Investment Distribution ---")

    for asset, amount in amount_distribution.items():
        percent = percent_distribution.get(asset, 0)
        risk_score = asset_info.get(asset, {}).get('risk_score', 'Unknown')
        expected_return = asset_info.get(asset, {}).get('expected_percentage_return', None)
        expected_return_desc = asset_info.get(asset, {}).get('expected_return_description', 'Unknown')
        if expected_return is not None:
            expected_return_str = f"{expected_return_desc} ({expected_return:.2%})"
        else:
            expected_return_str = expected_return_desc
        print(f"{asset:<20}: {amount:>15,.2f} TL (%{percent*100:.1f})")
        print(f"{' ':<20} Risk: {risk_score:<2} / 10 | Return: {expected_return_str}")

    total_portfolio_risk = calculate_portfolio_risk(percent_distribution, asset_info)
    total_portfolio_return = calculate_portfolio_return(percent_distribution, asset_info)
    print("-" * 50)
    print(f"Weighted Average Portfolio Risk: {total_portfolio_risk:.2f} / 10")
    print(f"Annual (TL Based) Portfolio Return Expectation: %{total_portfolio_return * 100:.2f}")
    print("="*50)

# --- Main Program ---
if __name__ == "__main__":
    people_list = load_file(PEOPLE_FILE)
    asset_info = load_file(ASSET_FILE)
    if people_list is None or asset_info is None:
        sys.exit("Program stopped due to file read error.")

    selected_person = select_person(people_list)
    if selected_person:
        new_amount_distribution = get_current_portfolio_info()
        new_principal = sum(new_amount_distribution.values())
        new_percent_distribution = {asset: round(amount / new_principal, 4) for asset, amount in new_amount_distribution.items()}
        selected_person['principal'] = new_principal
        selected_person['amount_distribution'] = new_amount_distribution
        selected_person['current_portfolio_distribution'] = new_percent_distribution
        # Overwrite current_values and current_portfolio for full update
        selected_person['current_values'] = new_amount_distribution.copy()
        selected_person['current_portfolio'] = new_percent_distribution.copy()
        save_file(people_list, PEOPLE_FILE)
        person_name = selected_person['name']
        show_portfolio_report(
            person_name,
            "Current Portfolio",
            new_amount_distribution,
            new_percent_distribution,
            new_principal,
            asset_info
        )


        
