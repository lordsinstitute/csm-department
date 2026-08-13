# Intelligent Document Summarizer

A modern web app that uses AI to generate clear, accurate summaries of legal and financial documents. Powered by Google Gemini 2.5 Flash and built with React and Tailwind CSS.

## Features

- Summarize uploaded documents (PDF, TXT, JPG, PNG) or pasted text
- Specialized modes for Legal, Financial, or Dual analysis
- Chatbot assistant for follow-up questions
- Extractive and Abstractive summaries, plus key points
- Clean, responsive dark theme design
- Secure file processing and data safety notice

## Demo

![Screenshot of the Intelligent Document Summarizer app](./demo.png)
*(Note: Replace `demo.png` with an actual screenshot of your application.)*

## Local Development Setup

Follow these instructions to get the project running on your local machine for development and testing purposes.

### Prerequisites

- [Node.js](https://nodejs.org/) (version 18 or later is recommended)
- [npm](https://www.npmjs.com/) (usually comes with Node.js)
- A Google Gemini API Key

### Instructions

1.  **Clone the Repository**
    
    Open your terminal and run the following command to clone the project:
    ```bash
    git clone https://github.com/your-username/intelligent-document-summarizer.git
    cd intelligent-document-summarizer
    ```
    *(Replace `your-username` with your actual GitHub username.)*

2.  **Install Dependencies**
    
    Install all the required packages using npm:
    ```bash
    npm install
    ```

3.  **Set Up Your API Key**
    
    This application requires a Google Gemini API key to function.
    
    a. Get your key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    
    b. In the root directory of the project, create a new file named `.env`.
    
    c. Open the `.env` file and add your API key in the following format:
    ```
    API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual key. This file is included in `.gitignore` to ensure your key is not accidentally committed to source control.

4.  **Start the Development Server**
    
    Run the following command to start the app locally:
    ```bash
    npm start
    ```
    This will launch the application in your default browser, typically at `http://localhost:3000`.

## Technologies Used

-   **React** - A JavaScript library for building user interfaces.
-   **TypeScript** - A typed superset of JavaScript that compiles to plain JavaScript.
-   **Tailwind CSS** - A utility-first CSS framework for rapid UI development.
-   **Google Gemini 2.5 Flash** (via `@google/genai`) - The AI model powering text extraction, summarization, and chat.
-   **jsPDF** - For client-side PDF generation.

## Security & Privacy

Your documents are processed securely. Files are sent directly to Google's Generative AI API and are **not** used for model training or stored on any intermediary servers. All communications are encrypted.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This application is for educational and research purposes only and should not be considered a substitute for professional advice.*