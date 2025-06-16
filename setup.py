
"""
Setup script for LLM Flashcard Generator
Run this script to set up your environment and test the application
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Error installing requirements. Please check your Python environment.")
        return False
    return True

def create_sample_directory():
    """Create sample content directory"""
    print("📁 Creating sample content directory...")
    os.makedirs("sample_content", exist_ok=True)
    
    # Create sample biology content
    sample_content = '''# Photosynthesis Overview

Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in chloroplasts and involves two main stages:

## Light-Dependent Reactions
- Occur in the thylakoids
- Chlorophyll absorbs light energy
- Water molecules are split, releasing oxygen
- ATP and NADPH are produced

## Calvin Cycle (Light-Independent Reactions)
- Occurs in the stroma
- Uses ATP and NADPH from light reactions
- Converts CO2 into glucose
- Does not directly require light

## Factors Affecting Photosynthesis
1. Light intensity
2. Carbon dioxide concentration
3. Temperature
4. Water availability

The overall equation: 6CO2 + 6H2O + light energy -> C6H12O6 + 6O2'''

    with open("sample_content/photosynthesis.txt", "w", encoding='utf-8') as f:
        f.write(sample_content)
    
    print("✅ Sample content created!")

def create_env_template():
    """Create environment template"""
    print("🔑 Creating environment template...")
    env_content = """# Copy this file to .env and add your actual API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set default number of flashcards
DEFAULT_CARD_COUNT=15

# Optional: Set default subject
DEFAULT_SUBJECT=General
"""
    
    with open(".env.example", "w", encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Environment template created!")

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting the application...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped!")

def main():
    """Main setup function"""
    print("=" * 50)
    print("🎓 LLM Flashcard Generator Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create sample directory
    create_sample_directory()
    
    # Create environment template
    create_env_template()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Enter your API key in the app sidebar when prompted")
    print("3. Upload content or use the sample file in sample_content/")
    print("4. Generate your flashcards!")
    
    # Ask if user wants to run the app
    response = input("\nWould you like to start the application now? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_application()
    else:
        print("\nTo start the application later, run: streamlit run app.py")

if __name__ == "__main__":
    main()