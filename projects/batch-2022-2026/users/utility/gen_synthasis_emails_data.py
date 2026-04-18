import google.generativeai as genai
import os

# --- IMPORTANT: Replace with your actual Gemini API Key ---
# It's recommended to store your API key securely, e.g., in an environment variable.
# For this example, we'll assume it's set as an environment variable.
# You can get your API key from Google AI Studio: https://aistudio.google.com/app/apikey
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set your Gemini API key before running this script.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

# --- Define the Generative AI model ---
# Using 'gemini-1.5-flash' as requested
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_phishing_email_content(target_company, attacker_goal, urgency_level="high"):
    """
    Generates synthetic phishing email content based on provided parameters.
    This is a conceptual example for training detection systems.
    """
    prompt = f"""
    You are an AI assistant tasked with generating synthetic phishing email content
    for cybersecurity training and detection system development.
    The goal is to create realistic-looking phishing emails.

    Generate an email targeting a user of "{target_company}".
    The attacker's goal is to "{attacker_goal}".
    The email should convey a {urgency_level} level of urgency.

    Include common phishing tactics like:
    - A deceptive sender name/email address.
    - A compelling subject line.
    - A sense of urgency or threat.
    - A call to action (e.g., click a link, verify information).
    - Grammatical errors or subtle inconsistencies are optional but can be included for realism.

    Start with a subject line and then the email body.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during content generation: {e}"

def generate_malware_description_for_threat_intel(malware_type, desired_impact, target_system):
    """
    Generates a synthetic description of a new, hypothetical malware variant
    for threat intelligence purposes. This helps in understanding potential new threats.
    """
    prompt = f"""
    As a cybersecurity threat intelligence analyst, you need to describe a
    hypothetical new malware variant.

    Generate a detailed description for a "{malware_type}" malware.
    Its primary desired impact is "{desired_impact}".
    It specifically targets "{target_system}".

    Include the following details:
    - Hypothetical name for the malware.
    - How it might propagate (e.g., phishing, exploit kit).
    - Its key functionalities/modules (e.g., data exfiltration, ransomware encryption).
    - Evasion techniques it might employ.
    - Potential indicators of compromise (IOCs) - e.g., unusual network traffic, specific file names.
    - A brief analysis of its potential threat level.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during content generation: {e}"

def start_generations(company, goal):
    print("--- Generative AI for Phishing Email Simulation (POC) ---")
    # company = "Acme Corp"
    # goal = "steal login credentials for their internal HR system"
    phishing_email = generate_phishing_email_content(company, goal, "critical")
    print(phishing_email)
    print("\n" + "="*80 + "\n")

    print("--- Generative AI for Synthetic Malware Description (POC) ---")
    malware = "fileless backdoor"
    impact = "persistent access and data exfiltration"
    system = "Windows Server environments with unpatched RDP"
    malware_description = generate_malware_description_for_threat_intel(malware, impact, system)
    print(malware_description)

    return phishing_email, malware_description
