import streamlit as st
import json
import csv
import io
from typing import List, Dict
import PyPDF2
import re
import requests
import time

class FlashcardGenerator:
    def __init__(self, api_key: str = None, model_type: str = "huggingface"):
        """Initialize with API key and model type"""
        self.model_type = model_type
        if model_type == "huggingface" and api_key:
            # Using a better model for text generation - Flan-T5 is good for instruction following
            self.hf_api_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            self.hf_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            self.hf_headers = {}
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def generate_flashcards(self, content: str, subject: str = "General", num_cards: int = 15) -> List[Dict]:
        """Generate flashcards using selected AI model"""
        
        if self.model_type == "huggingface":
            return self._generate_huggingface_flashcards(content, subject, num_cards)
        else:
            return self._generate_offline_flashcards(content, subject, num_cards)
    
    def _wait_for_model(self, max_wait_time: int = 60) -> bool:
        """Wait for Hugging Face model to load if it's sleeping"""
        for attempt in range(max_wait_time // 10):
            try:
                test_payload = {"inputs": "Test if model is ready"}
                response = requests.post(self.hf_api_url, headers=self.hf_headers, json=test_payload, timeout=10)
                
                if response.status_code == 200:
                    return True
                elif response.status_code == 503:
                    st.info(f"Model is loading... Please wait (attempt {attempt + 1})")
                    time.sleep(10)
                else:
                    return False
            except requests.exceptions.Timeout:
                st.info("Model is still loading, please wait...")
                time.sleep(10)
        return False
    
    def _generate_huggingface_flashcards(self, content: str, subject: str, num_cards: int) -> List[Dict]:
        """Generate flashcards using Hugging Face API"""
        
        # Wait for model to be ready
        if not self._wait_for_model():
            st.error("")
            return self._generate_offline_flashcards(content, subject, num_cards)
        
        flashcards = []
        
        # Split content into smaller chunks to avoid token limits
        content_chunks = self._split_content(content, max_length=800)
        cards_per_chunk = max(1, num_cards // len(content_chunks))
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, chunk in enumerate(content_chunks):
            if len(flashcards) >= num_cards:
                break
                
            status_text.text(f"Generating flashcards from chunk {i+1}/{len(content_chunks)}...")
            progress_bar.progress((i + 1) / len(content_chunks))
            
            # Create prompts for different types of questions
            question_types = [
                f"Create a definition question about the key concepts in this {subject} text: {chunk}. Format: Question: [question] Answer: [answer]",
                f"Create a 'how' or 'why' question about the processes described in this {subject} text: {chunk}. Format: Question: [question] Answer: [answer]",
                f"Create a factual question about important details in this {subject} text: {chunk}. Format: Question: [question] Answer: [answer]"
            ]
            
            chunk_cards = []
            for question_prompt in question_types[:cards_per_chunk]:
                try:
                    payload = {
                        "inputs": question_prompt,
                        "parameters": {
                            "max_length": 200,
                            "temperature": 0.7,
                            "do_sample": True
                        }
                    }
                    
                    response = requests.post(
                        self.hf_api_url, 
                        headers=self.hf_headers, 
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            card = self._parse_generated_card(generated_text, chunk)
                            if card:
                                chunk_cards.append(card)
                    else:
                        st.warning(f"API request failed with status {response.status_code}")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    st.warning(f"Error generating card: {str(e)}")
                    continue
            
            # If HF generation didn't work well, fall back to rule-based for this chunk
            if len(chunk_cards) == 0:
                chunk_cards = self._generate_offline_flashcards(chunk, subject, cards_per_chunk)
            
            flashcards.extend(chunk_cards)
        
        progress_bar.empty()
        status_text.empty()
        
        # If we don't have enough cards, fill with rule-based generation
        if len(flashcards) < num_cards:
            remaining_cards = num_cards - len(flashcards)
            additional_cards = self._generate_offline_flashcards(content, subject, remaining_cards)
            flashcards.extend(additional_cards)
        
        return flashcards[:num_cards]
    
    def _split_content(self, content: str, max_length: int = 800) -> List[str]:
        """Split content into smaller chunks"""
        sentences = content.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content[:max_length]]
    
    def _parse_generated_card(self, generated_text: str, original_content: str) -> Dict:
        """Parse the generated text to extract question and answer"""
        try:
            # Try to find Question: and Answer: patterns
            if "Question:" in generated_text and "Answer:" in generated_text:
                parts = generated_text.split("Question:")[-1].split("Answer:")
                if len(parts) >= 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    
                    return {
                        "question": question if question else "What is the main concept discussed?",
                        "answer": answer if answer else original_content[:200] + "...",
                        "difficulty": "Medium"
                    }
            
            # Fallback: treat entire response as answer and create generic question
            return {
                "question": "What information is provided about this topic?",
                "answer": generated_text.strip() if generated_text.strip() else original_content[:200] + "...",
                "difficulty": "Medium"
            }
            
        except Exception:
            return None
    
    def _generate_offline_flashcards(self, content: str, subject: str, num_cards: int) -> List[Dict]:
        """Generate flashcards using rule-based approach (no API required)"""
        flashcards = []
        
        # Simple rule-based flashcard generation
        sentences = content.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Pattern-based question generation
        for i, sentence in enumerate(sentences[:num_cards]):
            if ':' in sentence:
                # Definition pattern
                parts = sentence.split(':', 1)
                if len(parts) == 2:
                    term = parts[0].strip()
                    definition = parts[1].strip()
                    flashcards.append({
                        "question": f"What is {term}?",
                        "answer": definition,
                        "difficulty": "Medium"
                    })
            elif sentence.strip().endswith(')'):
                # Parenthetical information
                base = sentence.split('(')[0].strip()
                info = sentence.split('(')[1].replace(')', '').strip()
                flashcards.append({
                    "question": f"What additional information is provided about {base}?",
                    "answer": info,
                    "difficulty": "Easy"
                })
            else:
                # General question based on sentence structure
                if sentence.lower().startswith(('the', 'a', 'an')):
                    # Extract the main noun
                    words = sentence.split()
                    if len(words) > 2:
                        main_concept = ' '.join(words[1:4])
                        flashcards.append({
                            "question": f"What is mentioned about {main_concept.lower()}?",
                            "answer": sentence.strip(),
                            "difficulty": "Medium"
                        })
                else:
                    flashcards.append({
                        "question": f"What key point is made about {subject.lower()}?",
                        "answer": sentence.strip(),
                        "difficulty": "Medium"
                    })
        
        # Add some subject-specific questions if we need more cards
        if len(flashcards) < num_cards:
            subject_questions = {
                "biology": [
                    {"question": "What biological process is described in the content?", "answer": "Refer to the main processes mentioned in the material.", "difficulty": "Hard"},
                    {"question": "What are the key biological components discussed?", "answer": "Based on the content provided.", "difficulty": "Medium"}
                ],
                "history": [
                    {"question": "What historical period or event is discussed?", "answer": "As described in the content.", "difficulty": "Medium"},
                    {"question": "What were the key causes or effects mentioned?", "answer": "According to the material provided.", "difficulty": "Hard"}
                ],
                "general": [
                    {"question": "What is the main topic discussed?", "answer": "Based on the overall content.", "difficulty": "Easy"},
                    {"question": "What are the key points mentioned?", "answer": "As outlined in the material.", "difficulty": "Medium"}
                ]
            }
            
            additional_questions = subject_questions.get(subject.lower(), subject_questions["general"])
            flashcards.extend(additional_questions[:num_cards - len(flashcards)])
        
        return flashcards[:num_cards]
    
    def export_to_csv(self, flashcards: List[Dict]) -> str:
        """Export flashcards to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Question', 'Answer', 'Difficulty'])
        
        for card in flashcards:
            writer.writerow([card['question'], card['answer'], card.get('difficulty', 'Medium')])
        
        return output.getvalue()
    
    def export_to_json(self, flashcards: List[Dict]) -> str:
        """Export flashcards to JSON format"""
        return json.dumps(flashcards, indent=2)
    
    def export_to_anki(self, flashcards: List[Dict]) -> str:
        """Export flashcards to Anki-compatible format"""
        output = []
        for card in flashcards:
            # Anki format: Front; Back; Tags
            output.append(f"{card['question']};{card['answer']};{card.get('difficulty', 'Medium')}")
        return "\n".join(output)

def main():
    st.set_page_config(
        page_title="HuggingFace Flashcard Generator",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 HuggingFace-Powered Flashcard Generator")
    st.markdown("Convert your educational content into effective flashcards using HuggingFace AI models!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        model_type = st.selectbox(
            "Choose AI Model",
            ["HuggingFace API (Requires API Key)", "Offline Mode (No API Required)"],
            help="Select your preferred method for generating flashcards"
        )
        
        api_key = None
        if "HuggingFace API" in model_type:
            # API Key input
            api_key = st.text_input(
                "HuggingFace API Key", 
                type="password",
                help="Enter your HuggingFace API token to generate AI-powered flashcards"
            )
            
            if not api_key:
                st.warning("Please enter your HuggingFace API token to use AI models")
                st.markdown("🔗 [Get your free API token here](https://huggingface.co/settings/tokens)")
            else:
                st.success("✅ API key provided! Using google/flan-t5-large model")
        else:
            st.info("📝 Offline mode uses rule-based generation - no API key needed!")
        
        # Subject selection
        subject = st.selectbox(
            "Subject Area",
            ["General", "Biology", "History", "Computer Science", "Mathematics", 
             "Physics", "Chemistry", "Literature", "Psychology", "Economics"]
        )
        
        # Number of flashcards
        num_cards = st.slider("Number of Flashcards", 5, 20, 10)
        
        # Model information
        if "HuggingFace API" in model_type:
            st.info("🤖 **Model:** Google Flan-T5 Large\n📊 **Quality:** High\n⚡ **Speed:** Medium")
    
    # Initialize generator
    selected_model = "huggingface" if "HuggingFace API" in model_type else "offline"
    generator = FlashcardGenerator(api_key, selected_model)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Input Content")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "File Upload"]
        )
        
        content = ""
        
        if input_method == "Text Input":
            content = st.text_area(
                "Paste your educational content here:",
                height=300,
                placeholder="Enter lecture notes, textbook excerpts, or any educational material..."
            )
        
        else:  # File Upload
            uploaded_file = st.file_uploader(
                "Upload your file",
                type=['txt', 'pdf'],
                help="Upload a .txt or .pdf file containing educational content"
            )
            
            if uploaded_file is not None:
                if uploaded_file.type == "text/plain":
                    content = str(uploaded_file.read(), "utf-8")
                elif uploaded_file.type == "application/pdf":
                    content = generator.extract_text_from_pdf(uploaded_file)
                
                if content:
                    st.success(f"File uploaded successfully! Content length: {len(content)} characters")
                    with st.expander("Preview content"):
                        st.text(content[:1000] + "..." if len(content) > 1000 else content)
    
    with col2:
        st.header("Quick Stats")
        if content:
            st.metric("Content Length", f"{len(content)} chars")
            st.metric("Estimated Words", f"{len(content.split())} words")
            st.metric("Target Flashcards", num_cards)
            
            # Show estimated time for HF API
            if "HuggingFace API" in model_type and api_key:
                estimated_time = num_cards * 2  # rough estimate
                st.metric("Est. Generation Time", f"{estimated_time}s")
        else:
            st.info("Upload content to see stats")
    
    # Generate flashcards
    if st.button("🚀 Generate Flashcards", type="primary", use_container_width=True):
        if not content:
            st.error("Please provide some educational content first!")
            return
        
        if len(content.strip()) < 50:
            st.warning("Content seems too short. Please provide more detailed educational material.")
            return
        
        # Check if API key is needed but not provided
        if "HuggingFace API" in model_type and not api_key:
            st.error("Please provide a HuggingFace API token or switch to Offline Mode.")
            return
        
        generation_method = "AI-powered HuggingFace analysis" if "HuggingFace API" in model_type else "rule-based extraction"
        with st.spinner(f"Generating flashcards using {generation_method}..."):
            flashcards = generator.generate_flashcards(content, subject, num_cards)
        
        if flashcards:
            st.success(f"Successfully generated {len(flashcards)} flashcards!")
            
            # Store in session state
            st.session_state.flashcards = flashcards
            
            # Display flashcards
            st.header("📚 Generated Flashcards")
            
            # Display options
            display_mode = st.radio("Display Mode:", ["Card View", "List View"], horizontal=True)
            
            if display_mode == "Card View":
                # Card view with tabs
                if len(flashcards) > 0:
                    # Create tabs for each flashcard (limit to 10 for UI performance)
                    display_count = min(len(flashcards), 10)
                    tab_labels = [f"Card {i+1}" for i in range(display_count)]
                    tabs = st.tabs(tab_labels)
                    
                    for i, tab in enumerate(tabs):
                        with tab:
                            card = flashcards[i]
                            st.markdown(f"**Question:** {card['question']}")
                            with st.expander("Show Answer"):
                                st.markdown(f"**Answer:** {card['answer']}")
                                if 'difficulty' in card:
                                    difficulty_color = {
                                        'Easy': 'green',
                                        'Medium': 'orange', 
                                        'Hard': 'red'
                                    }.get(card['difficulty'], 'blue')
                                    st.markdown(f"**Difficulty:** :{difficulty_color}[{card['difficulty']}]")
                    
                    if len(flashcards) > 10:
                        st.info(f"Showing first 10 cards. Total generated: {len(flashcards)}. Use List View or export to see all cards.")
            else:
                # List view
                for i, card in enumerate(flashcards, 1):
                    with st.container():
                        st.markdown(f"### Card {i}")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Q:** {card['question']}")
                            st.markdown(f"**A:** {card['answer']}")
                        with col2:
                            if 'difficulty' in card:
                                st.markdown(f"**Difficulty:** {card['difficulty']}")
                        st.divider()
            
            # Export options
            st.header("📥 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = generator.export_to_csv(flashcards)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"flashcards_{subject.lower()}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = generator.export_to_json(flashcards)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"flashcards_{subject.lower()}.json",
                    mime="application/json"
                )
            
            with col3:
                anki_data = generator.export_to_anki(flashcards)
                st.download_button(
                    label="🎯 Download Anki Format",
                    data=anki_data,
                    file_name=f"flashcards_{subject.lower()}.txt",
                    mime="text/plain"
                )
        else:
            st.error("Failed to generate flashcards. Please try again or switch to Offline Mode.")

if __name__ == "__main__":
    main()