#SMART CLASSROOM ASSIST

📌 Project Description

Smart Classroom Assist is an AI-powered system designed to automate and enhance traditional classroom activities using advanced technologies such as Computer Vision, Optical Character Recognition (OCR), and Natural Language Processing (NLP).

The system reduces manual workload for teachers while improving the learning experience for students through intelligent automation and real-time assistance.

The system performs automated attendance using object detection models (YOLO) by analyzing live CCTV feeds, eliminating the need for manual roll calls. It captures and digitizes classroom board content using OCR techniques like Tesseract and PaddleOCR, and further refines the extracted text using Large Language Models (LLMs) to generate structured and concise notes.

Additionally, it provides AI-based doubt solving and real-time lecture summaries, enabling students to better understand and revise concepts.

The platform is developed as a cross-platform application using Flutter, ensuring accessibility across Android, iOS, and Web. A cloud-based backend using Supabase enables real-time data synchronization, secure storage, and scalability.

Team

<img width="831" height="530" alt="image" src="https://github.com/user-attachments/assets/b8b0822a-7d98-49f0-bfec-8cf0b27c6789" />

Project Guide: Mr. Khaja Pasha, Assistant Professor  
Co-Guide / HoD: Dr. Altaf C, Associate Professor & Associate HoD, Department of CSE-AIML  
Institution: Lords Institute of Engineering and Technology, Hyderabad  

🏗️ Project Structure

1. Input Layer
- CCTV video feed (attendance)
- Classroom board images
- Student queries (text input)

2. Processing Layer

a. Computer Vision Module
- YOLO model
- Student detection and attendance marking

b. OCR Module
- Tesseract / PaddleOCR
- Converts board content into digital text

c. NLP / LLM Module
- HuggingFace models
- Text summarization
- Question answering
- Note refinement


3. Backend Layer
- Supabase
- Database storage
- Authentication
- API communication
- Real-time updates


4. Application Layer
- Flutter (Android, iOS, Web)

Features:
- Student Dashboard
- Teacher Dashboard
- Notes access
- Attendance monitoring
- AI interaction

5. Output Layer
- Attendance reports
- AI-generated notes
- Lecture summaries
- Answers to student queries
