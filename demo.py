import streamlit as st
import json

# Sample flashcards for demonstration
SAMPLE_FLASHCARDS = {
    "Biology": [
        {"question": "What is photosynthesis?", "answer": "The process by which plants convert light energy into chemical energy, producing glucose and oxygen from carbon dioxide and water.", "difficulty": "Medium"},
        {"question": "Where does photosynthesis occur in plant cells?", "answer": "In the chloroplasts, specifically in the thylakoids where chlorophyll captures light energy.", "difficulty": "Easy"},
        {"question": "What are the two main stages of photosynthesis?", "answer": "The light-dependent reactions (occur in thylakoids) and the Calvin cycle (occurs in stroma).", "difficulty": "Medium"},
        {"question": "What is the chemical equation for photosynthesis?", "answer": "6CO2 + 6H2O + light energy → C6H12O6 + 6O2", "difficulty": "Hard"},
        {"question": "What factors affect the rate of photosynthesis?", "answer": "Light intensity, carbon dioxide concentration, temperature, and water availability.", "difficulty": "Medium"},
    ],
    "History": [
        {"question": "When did World War II begin?", "answer": "September 1, 1939, when Germany invaded Poland.", "difficulty": "Easy"},
        {"question": "What was D-Day?", "answer": "The Allied invasion of Normandy, France on June 6, 1944, opening a second front in Western Europe.", "difficulty": "Medium"},
        {"question": "What were the main causes of World War II?", "answer": "The Treaty of Versailles, rise of totalitarian regimes, economic instability from the Great Depression, and failure of the League of Nations.", "difficulty": "Hard"},
        {"question": "When did the United States enter World War II?", "answer": "December 8, 1941, the day after the Pearl Harbor attack by Japan.", "difficulty": "Medium"},
        {"question": "What were the two main theaters of World War II?", "answer": "The European Theater (Germany vs. Allies in Europe) and the Pacific Theater (Japan vs. Allies in the Pacific).", "difficulty": "Medium"},
    ],
    "Computer Science": [
        {"question": "What is the time complexity of accessing an element in an array?", "answer": "O(1) - constant time, as elements can be accessed directly using their index.", "difficulty": "Easy"},
        {"question": "What is a linked list?", "answer": "A linear data structure where elements are stored in nodes, each containing data and a pointer to the next node.", "difficulty": "Medium"},
        {"question": "What are the advantages of arrays over linked lists?", "answer": "Fast random access, memory efficiency, cache-friendly layout, and simplicity of implementation.", "difficulty": "Medium"},
        {"question": "What is the time complexity of insertion in a linked list?", "answer": "O(1) if the position is known, O(n) if the position must be found by traversing the list.", "difficulty": "Hard"},
        {"question": "When should you use a linked list instead of an array?", "answer": "When you need frequent insertions/deletions, when size varies significantly, or when the order of elements changes often.", "difficulty": "Hard"},
    ]
}

def main():
    st.set_page_config(
        page_title="Flashcard Demo",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Flashcard Generator Demo")
    st.markdown("**Experience sample flashcards instantly - no API key required!**")
    
    st.info("💡 This demo shows you exactly what the flashcard generator produces. Try the full version with your own content using the main app!")
    
    # Subject selection
    subject = st.selectbox(
        "Choose a subject to see sample flashcards:",
        list(SAMPLE_FLASHCARDS.keys())
    )
    
    flashcards = SAMPLE_FLASHCARDS[subject]
    
    # Display flashcards
    st.header(f"📚 Sample {subject} Flashcards")
    
    # Display mode selection
    display_mode = st.radio("Display Mode:", ["Card View", "List View"], horizontal=True)
    
    if display_mode == "Card View":
        # Create tabs for each flashcard
        tab_labels = [f"Card {i+1}" for i in range(len(flashcards))]
        tabs = st.tabs(tab_labels)
        
        for i, tab in enumerate(tabs):
            with tab:
                card = flashcards[i]
                st.markdown(f"**Question:** {card['question']}")
                with st.expander("Show Answer"):
                    st.markdown(f"**Answer:** {card['answer']}")
                    difficulty_color = {
                        'Easy': 'green',
                        'Medium': 'orange', 
                        'Hard': 'red'
                    }.get(card['difficulty'], 'blue')
                    st.markdown(f"**Difficulty:** :{difficulty_color}[{card['difficulty']}]")
    
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
                    st.markdown(f"**Difficulty:** {card['difficulty']}")
                st.divider()
    
    # Export demo
    st.header("📥 Export Preview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Preview CSV Format"):
            csv_preview = "Question,Answer,Difficulty\n"
            for card in flashcards:
                csv_preview += f'"{card["question"]}","{card["answer"]}","{card["difficulty"]}"\n'
            st.code(csv_preview, language="csv")
    
    with col2:
        if st.button("📋 Preview JSON Format"):
            json_preview = json.dumps(flashcards, indent=2)
            st.code(json_preview, language="json")
    
    with col3:
        if st.button("🎯 Preview Anki Format"):
            anki_preview = ""
            for card in flashcards:
                anki_preview += f"{card['question']};{card['answer']};{card['difficulty']}\n"
            st.code(anki_preview, language="text")
    
    # Call to action
    st.markdown("---")
    st.markdown("### 🚀 Ready to try with your own content?")
    st.markdown("Run the main application with `streamlit run app.py` to:")
    st.markdown("- Upload your own educational content")
    st.markdown("- Generate custom flashcards using AI")
    st.markdown("- Export in multiple formats")
    st.markdown("- Choose from different subjects and difficulty levels")

if __name__ == "__main__":
    main()