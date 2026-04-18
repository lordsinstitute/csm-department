# myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

def extract_entities(text):
    emails = re.findall(r'\S+@\S+', text)
    names = re.findall(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)', text)
    if names:
        names = [" ".join(names[0])]
    return emails, names

def index(request):
    results = []

    if request.method == 'POST':
        job_description = request.POST.get('job_description')
        resume_files = request.FILES.getlist('resume_files')

        # Create a directory for uploads if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Process uploaded resumes
        processed_resumes = []
        for resume_file in resume_files:
            # Save the uploaded file
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(resume_file.name, resume_file)
            resume_path = os.path.join(upload_dir, filename)

            # Process the saved file
            resume_text = extract_text_from_pdf(resume_path)
            emails, names = extract_entities(resume_text)
            processed_resumes.append((names, emails, resume_text))

        # TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer()
        job_desc_vector = tfidf_vectorizer.fit_transform([job_description])

        # Rank resumes based on similarity
        ranked_resumes = []
        for (names, emails, resume_text) in processed_resumes:
            resume_vector = tfidf_vectorizer.transform([resume_text])
            similarity = cosine_similarity(job_desc_vector, resume_vector)[0][0] * 100 
            ranked_resumes.append((names, emails, similarity))

        # Sort resumes by similarity score
        ranked_resumes.sort(key=lambda x: x[2], reverse=True)

        results = ranked_resumes

    return results

def download_csv(request):
    # Generate the CSV content
    results = request.session.get('results', [])
    csv_content = "Rank,Name,Email,Similarity\n"
    for rank, (names, emails, similarity) in enumerate(results, start=1):
        name = names[0] if names else "N/A"
        email = emails[0] if emails else "N/A"
        csv_content += f"{rank},{name},{email},{similarity}\n"

    # Create a temporary file to store the CSV content
    csv_filename = "ranked_resumes.csv"
    csv_full_path = os.path.join(settings.MEDIA_ROOT, csv_filename)
    with open(csv_full_path, "w") as csv_file:
        csv_file.write(csv_content)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'

    with open(csv_full_path, 'rb') as csv_file:
        response.write(csv_file.read())

    return response
