
# English version, updated for new JSON structure
import json

PEOPLE_FILE = "../data/people.json"
SURVEY_FILE = "risk_survey.json"

def load_portfolios(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        return []

def save_portfolios(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"\nData successfully saved to '{file_path}'.")
    except Exception as e:
        print(f"Error saving file: {e}")

def load_questions():
    try:
        with open(SURVEY_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('risk_questions', [])
    except FileNotFoundError:
        print(f"Error: '{SURVEY_FILE}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{SURVEY_FILE}' is not a valid JSON file.")
        return None

def select_person(people):
    if not people:
        print("No registered person found.")
        return None
    print("\nPlease select the person whose risk score you want to calculate:")
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

def calculate_risk_profile():
    questions = load_questions()
    if not questions:
        return None
    total_score = 0
    num_questions = len(questions)
    print("\n--- Investor Risk Profile Survey ---")
    print("Please enter the letter (A, B, C, ...) for your answer to each question.")
    print("-" * 35)
    for i, question_data in enumerate(questions, 1):
        question_text = question_data['question_text']
        options = question_data['options']
        print(f"\nQuestion {i}/{num_questions}: {question_text}")
        option_map = {}
        for option in options:
            print(f"  {option['option_id']}) {option['option_text']}")
            option_map[option['option_id'].upper()] = option['score']
        while True:
            user_input = input("Your answer: ").upper()
            if user_input in option_map:
                total_score += option_map[user_input]
                break
            else:
                print(f"Invalid input. Please enter one of: {', '.join(option_map.keys())}")
    risk_score = 0
    if num_questions > 0:
        risk_score = total_score / num_questions
    print("\n" + "-" * 35)
    print(f"Survey Completed. Your Risk Score: {risk_score:.1f}")
    print("-" * 35)
    if risk_score <= 13.3:
        risk_level = "Low Risk"
        description = "You are an investor who prioritizes financial security and avoids risk."
    elif risk_score <= 23.3:
        risk_level = "Medium Risk (Balanced)"
        description = "You aim to protect your capital while also seeking moderate returns."
    else:
        risk_level = "High Risk"
        description = "You are willing to take high risks for high return potential."
    print(f"Your Risk Profile: {risk_level}")
    print(f"Description: {description}")
    return risk_score

def main():
    people_list = load_portfolios(PEOPLE_FILE)
    if not people_list:
        print("Operation could not be completed. Please check the people list.")
        return
    selected_person = select_person(people_list)
    if selected_person:
        risk_score = calculate_risk_profile()
        if risk_score is not None:
            selected_person['risk_score'] = round(risk_score, 2)
            print(f"\n{selected_person['name']}'s new risk score is '{selected_person['risk_score']}'.")
            save_portfolios(PEOPLE_FILE, people_list)

if __name__ == "__main__":
    main()