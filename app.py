import json
import streamlit as st
from mem0 import MemoryClient
import openai  # For ChatGPT integration
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CareerCoach AI",
    page_icon="👔",
    layout="centered"
)

# Initialize the Memory client
@st.cache_resource
def get_memory_client():
    mem0_api_key = os.getenv("MEM0_API_KEY")
    if not mem0_api_key:
        st.error("MEM0_API_KEY not found in environment variables. Please check your .env file.")
        return None
    return MemoryClient(api_key=mem0_api_key)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        return None
    return openai.OpenAI(api_key=openai_api_key)

# Define the career advisor system role with updated instructions for concise responses
CAREER_ADVISOR_SYSTEM_ROLE = """
You are CareerCoach AI, an expert career and job advisor leveraging detailed user profile information. 
Your role is to provide personalized career guidance based on:

1. The user's personal information (name, contact details, birth date)
2. Professional background (current job, company, salary, employment type, work setting)
3. Technical skills and expertise
4. Previous work experience
5. Career aspirations (desired role, industry, work setting preferences)
6. Timeline constraints (current contract end date, certification completion)
7. Relocation preferences

IMPORTANT: Always analyze the user's question first and provide a direct, concise answer only to what they're asking:
- For simple factual questions (e.g., "What is my birthdate?", "What is my current salary?"), provide only the specific information requested with minimal context.
- For more complex questions seeking advice (e.g., "How can I transition to a new role?"), provide more detailed guidance.
- Always address the user by their first name.
- Keep responses as concise as possible while still being helpful.
- Only include information directly relevant to their specific question.

When advising users on career development:
- Be specific and personalized, directly referencing their skills, experience, and stated preferences
- Provide actionable recommendations for career advancement or transition
- Suggest realistic timelines based on their current contract end date
- Recommend skill development opportunities relevant to their career goals
- Offer industry-specific insights for their target sector
- Consider their work setting preferences (remote, hybrid, onsite)
- Account for their relocation preferences when suggesting opportunities

Always maintain a supportive, encouraging tone while being honest about the skills gap or additional qualifications they might need to achieve their goals.
"""

def format_name(name):
    """
    Format name to properly capitalize each word
    Examples:
    - wassay haider -> Wassay Haider
    - WASSAY HAIDER -> Wassay Haider
    - wAsSaY hAiDeR -> Wassay Haider
    """
    if not name:
        return ""
        
    # Split by spaces and format each word
    words = name.split()
    formatted_words = [word.capitalize() for word in words]
    return " ".join(formatted_words)

def is_full_name(name):
    """Check if input appears to be a full name (at least two words)"""
    if not name:
        return False
    words = name.strip().split()
    return len(words) >= 2

def search_memory(query, user_id):
    """Search memory and return results"""
    try:
        client = get_memory_client()
        results = client.search(query, user_id=user_id)
        return results
    except Exception as e:
        st.error(f"Error searching memory: {e}")
        return None

def get_chatgpt_response(memory_results, query):
    """Get response from ChatGPT based on memory results with improved query understanding"""
    try:
        # Create a prompt that includes the memory search results and emphasizes concise responses
        prompt = f"""
        The user asked: "{query}"
        
        Information retrieved from memory about the user:
        {json.dumps(memory_results, indent=2)}
        
        Remember to:
        1. Understand the specific intent of the question - is it a simple factual query or a request for advice?
        2. For factual questions (like "What is my birthdate?"), provide ONLY the specific fact with minimal context.
        3. For advice questions, provide personalized guidance considering their profile information.
        4. Always be concise and directly address their question.
        
        Now, provide a personalized response that directly answers their specific question.
        """
        
        # Call the OpenAI API with the career advisor system role
        openai_client = get_openai_client()
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",  # Using a more capable model for better career advice
            messages=[
                {"role": "system", "content": CAREER_ADVISOR_SYSTEM_ROLE},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting ChatGPT response: {e}")
        return f"I encountered an error while processing your request: {str(e)}"

# Initialize session state variables
if 'name_entered' not in st.session_state:
    st.session_state.name_entered = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'name_error' not in st.session_state:
    st.session_state.name_error = ""
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'submit_clicked' not in st.session_state:
    st.session_state.submit_clicked = False
if 'reset_name_clicked' not in st.session_state:
    st.session_state.reset_name_clicked = False
if 'show_names' not in st.session_state:
    st.session_state.show_names = True

# List of all available names
available_names = [
    "Jennifer Petty", "Emily Lopez", "Amy Hancock", "Jennifer Morris", "James Santos",
    "Lisa French", "Ann Mendez", "Victor Edwards", "Sandra Smith", "Timothy Stuart",
    "Linda Ramirez", "Melanie Cook", "Jennifer Marshall", "Tanya Miller DVM", "Jeffery Jackson",
    "Christopher Proctor", "Kristi Hart", "Tim Cruz", "Steven Garcia DDS", "Rachel Montgomery",
    "Caitlin Marshall", "Jesse Jenkins", "Timothy Singh", "Monique Freeman", "Michael Murray",
    "Heather Davis", "Jennifer Moody", "Roberta Dougherty", "Karen Lewis", "Thomas Burgess",
    "Carla Ball", "Douglas Webster", "Jill Nunez", "Joseph Young", "Molly Davis",
    "Glen Gonzalez", "Richard Martin", "Jesse Hayes", "Lauren Fischer", "Sheila King",
    "Jacob Smith", "Vickie Garcia", "Micheal Robinson", "Dr. Brandy Gallagher", "James Hunt",
    "Timothy Chan", "Kevin Patterson", "Alyssa Bennett", "Whitney Jordan", "Kyle Neal"
]

# Callback functions for buttons that update session state
def on_name_submit():
    """Set flag when name is submitted"""
    st.session_state.submit_clicked = True
    # Hide the names once a name is submitted
    st.session_state.show_names = False

def on_reset_name():
    """Set flag when name reset is requested"""
    st.session_state.reset_name_clicked = True
    # Show the names again when resetting
    st.session_state.show_names = True

# App header
st.title("CareerCoach AI")
st.markdown("### Your Personalized Career Advisor")
st.markdown("---")

# Handle reset name request (must be processed before the main interface logic)
if st.session_state.reset_name_clicked:
    st.session_state.name_entered = False
    st.session_state.reset_name_clicked = False

# Sidebar with available names
if not st.session_state.name_entered and st.session_state.show_names:
    with st.sidebar:
        st.header("Available Profiles")
        st.markdown("##### Click on a name to begin!")
        
        # Calculate midpoint to split the names into two columns if needed
        midpoint = len(available_names) // 2
        
        # Create two columns in the sidebar
        col1, col2 = st.columns(2)
        
        # Display first half of names in first column
        with col1:
            for name in available_names[:midpoint]:
                if st.button(name, key=f"btn_{name}", use_container_width=True):
                    st.session_state.user_id = name
                    st.session_state.name_entered = True
                    st.session_state.show_names = False
                    st.rerun()
        
        # Display second half of names in second column
        with col2:
            for name in available_names[midpoint:]:
                if st.button(name, key=f"btn_{name}", use_container_width=True):
                    st.session_state.user_id = name
                    st.session_state.name_entered = True
                    st.session_state.show_names = False
                    st.rerun()
        
        st.markdown("---")
        st.caption("These are sample profiles for demonstration purposes.")

# Name entry popup if name hasn't been entered yet
if not st.session_state.name_entered:
    # Create a centered card for name entry
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Welcome to CareerCoach AI")
        st.markdown("Please enter your full name to get started.")
        
        name_input = st.text_input("Your full name:", key="name_input")
        
        if st.session_state.name_error:
            st.error(st.session_state.name_error)
            
        st.button("Continue", on_click=on_name_submit)
        
        # Process the submission after button is clicked
        if st.session_state.submit_clicked:
            if not name_input:
                st.session_state.name_error = "Please enter your name to continue."
                st.session_state.submit_clicked = False  # Reset the flag
            elif not is_full_name(name_input):
                st.session_state.name_error = "Please enter your full name (first and last name)."
                st.session_state.submit_clicked = False  # Reset the flag
            else:
                st.session_state.name_error = ""
                st.session_state.user_id = format_name(name_input)
                st.session_state.name_entered = True
                st.session_state.submit_clicked = False  # Reset the flag
else:
    # Main application after name has been entered
    st.write(f"Hello, **{st.session_state.user_id}**! How can I help with your career today?")
    
    # Provide example queries to guide users
    with st.expander("Example questions you can ask"):
        st.markdown("""
        - What is my current salary?
        - When does my current contract end?
        - What are my technical skills?
        - What career path should I pursue with my background?
        - How can I transition to a data science role?
        - What skills should I develop for my desired role?
        - What's a realistic timeline for my career transition?
        """)
    
    # Input area for user's career question
    query = st.text_area("Your career question:", 
                         value=st.session_state.query,
                         height=80, 
                         placeholder="Ask me anything about your career, skills, or profile...")
    
    # Clear the stored query once it's displayed
    if st.session_state.query:
        st.session_state.query = ""
    
    if st.button("Get Response"):
        if query:
            with st.spinner("Searching for your profile information..."):
                memory_results = search_memory(query, st.session_state.user_id)
            
            if memory_results:
                st.success("Profile information found!")
                
                # Option to view raw profile data (collapsible)
                with st.expander("View your profile information", expanded=False):
                    st.json(memory_results)
                
                with st.spinner("Analyzing your career situation..."):
                    response = get_chatgpt_response(memory_results, query)
                
                # Display the response in a clean, highlighted box
                st.markdown("## Your Answer")
                # st.markdown("---")
                st.markdown(f"<div style='background-color:#393E46 ; padding:2px; border-radius:10px;'>{response}</div>", 
                            unsafe_allow_html=True)
            else:
                st.error("I couldn't find your profile information. Please check that you've entered your name correctly or contact support.")
        else:
            st.warning("Please enter a career question to get personalized advice.")
    
    # Add option to change name (small, at the bottom)
    st.markdown("---")
    st.button("Change your name", 
              type="secondary", 
              help="Click to re-enter your name", 
              on_click=on_reset_name)

# Footer
st.markdown("---")
st.caption("CareerCoach AI uses mem0 for secure profile storage and OpenAI for personalized career insights.")