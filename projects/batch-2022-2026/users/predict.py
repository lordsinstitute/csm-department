# predict.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import random
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def perform_prediction(mri, pet):
    # Save temporary images (for simulation, replace with actual fusion logic)
    mri_path = f'media/uploads/temp_mri_{datetime.now().timestamp()}.png'
    pet_path = f'media/uploads/temp_pet_{datetime.now().timestamp()}.png'
    fused_image_path = f'media/uploads/fused/fused_{datetime.now().timestamp()}.png'

    with open(mri_path, 'wb+') as f:
        for chunk in mri.chunks():
            f.write(chunk)

    with open(pet_path, 'wb+') as f:
        for chunk in pet.chunks():
            f.write(chunk)

    os.system(f'cp {mri_path} {fused_image_path}')  # Simulated fusion logic

    # Simulated tumor prediction result
    result = random.choice(['Tumor Detected', 'No Tumor'])
    confidence = round(random.uniform(97.0, 99.9), 2)

    # Use Gemini to generate a caption or explanation
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"This fused brain scan MRI-PET image suggests a diagnosis of: {result}. Confidence: {confidence}%. Please provide a short medical explanation."

    try:
        response = model.generate_content(prompt)
        explanation = response.text
    except Exception as e:
        explanation = "Gemini response failed. " + str(e)

    return fused_image_path, result, confidence, explanation
