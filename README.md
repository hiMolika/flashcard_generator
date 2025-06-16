# 🎓 LLM-Powered Flashcard Generator
An intelligent flashcard generation tool that converts educational content into effective question-answer flashcards using Large Language Models (LLMs).
🚀 Features

Multi-format Input: Support for text input and file uploads (.txt, .pdf)
AI-Powered Generation: Uses OpenAI GPT models to create high-quality flashcards
Subject-Specific: Tailored flashcard generation for different academic subjects
Difficulty Levels: Automatic assignment of Easy/Medium/Hard difficulty levels
Multiple Export Formats: CSV, JSON, and Anki-compatible formats
Interactive UI: Clean, user-friendly Streamlit interface
Customizable: Adjustable number of flashcards (10-25 per session)

🛠️ Installation & Setup
Prerequisites

Python 3.8 or higher
OpenAI API key (Get one here)

Step 1: Clone the Repository
bashgit clone (https://github.com/hiMolika/flashcard_generator)
cd flashcard_generator
Step 2: Install Dependencies
bashpip install -r requirements.txt
Step 3: Run the Application
bashstreamlit run app.py
The application will open in your browser at http://localhost:8501
📝 Usage Guide
1. API Key Setup

Enter your OpenAI API key in the sidebar
The key is required for flashcard generation

2. Configure Settings

Select your subject area (Biology, History, Maths, etc.)
Choose the number of flashcards to generate (10-25)

3. Input Content
Choose one of two input methods:
Text Input:

Paste your educational content directly into the text area
Supports lecture notes, textbook excerpts, study materials

File Upload:

Upload .txt or .pdf files
Automatic text extraction from PDFs
Content preview available

4. Generate Flashcards

Click "Generate Flashcards" to start the AI processing
Wait for the AI to analyze your content and create flashcards

5. Review & Export

Card View: Browse flashcards individually with expandable answers
List View: See all flashcards in a scrollable list
Export Options: Download in CSV, JSON

📊 Sample Output
Question: What is photosynthesis?
Answer: Photosynthesis is the process by which plants convert light energy into chemical energy, producing glucose and oxygen from carbon dioxide and water.
Difficulty: Medium
Question: Where does photosynthesis occur in plant cells?
Answer: Photosynthesis occurs in the chloroplasts, specifically in the thylakoids where chlorophyll captures light energy.
Difficulty: Easy

## 🚀 Installation & Setup
### 1️⃣ Clone the repository
```bash
git clone https://github.com/hiMolika/flashcard_generator
cd flashcard_generator
