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

# Define the career advisor system role
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

# Define the onboarding system role
ONBOARDING_SYSTEM_ROLE = """
You are CareerCoach AI's onboarding assistant. Your role is to collect comprehensive user information through a friendly, conversational interview process.

You need to collect information in these categories:
1. Personal Information: Full name, date of birth, location, contact details (email, phone, LinkedIn), marital status
2. Current Job Information: Current role, company, salary, employment type (full-time/part-time/contract), work setting (remote/hybrid/onsite)
3. Technical Skills: Programming languages, tools, frameworks, certifications
4. Work Experience: Previous roles, companies, duration, key responsibilities
5. Career Aspirations: Desired role, preferred industry, work setting preferences, relocation willingness
6. Timeline & Milestones: Contract end dates, certification completion dates, job search timeline

IMPORTANT GUIDELINES:
- Ask questions in a natural, conversational manner
- Ask 2-3 related questions at a time to keep the conversation flowing
- Be encouraging and supportive throughout the process
- After each user response, acknowledge what you've learned before asking the next questions
- When you have collected sufficient information across all categories, say: "Perfect! I now have all the information I need to provide you with personalized career advice. You can now ask me any career-related questions!"

Start the conversation by explaining that you need to learn about them first, then begin with basic personal information.
"""

def format_name(name):
    """Format name to properly capitalize each word"""
    if not name:
        return ""
    words = name.split()
    formatted_words = [word.capitalize() for word in words]
    return " ".join(formatted_words)

def is_full_name(name):
    """Check if input appears to be a full name (at least two words)"""
    if not name:
        return False
    words = name.strip().split()
    return len(words) >= 2

def check_user_exists(user_id):
    """Check if user exists in mem0 by searching for any memories"""
    try:
        client = get_memory_client()
        if not client:
            return False
        
        # Try to search for any information about the user
        results = client.search("personal information", user_id=user_id)
        return len(results) > 0
    except Exception as e:
        st.error(f"Error checking user existence: {e}")
        return False

def add_memory_from_conversation(user_message, assistant_message, user_id):
    """Add memory from a conversation turn"""
    try:
        client = get_memory_client()
        if not client:
            return False
        
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        
        client.add(messages, user_id=user_id)
        return True
    except Exception as e:
        st.error(f"Error adding memory: {e}")
        return False

def search_memory(query, user_id):
    """Search memory and return results"""
    try:
        client = get_memory_client()
        results = client.search(query, user_id=user_id)
        return results
    except Exception as e:
        st.error(f"Error searching memory: {e}")
        return None

def get_chatgpt_response(memory_results, query, system_role=CAREER_ADVISOR_SYSTEM_ROLE):
    """Get response from ChatGPT based on memory results"""
    try:
        if memory_results:
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
        else:
            prompt = query
        
        openai_client = get_openai_client()
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting ChatGPT response: {e}")
        return f"I encountered an error while processing your request: {str(e)}"

def get_onboarding_response(conversation_history):
    """Get onboarding response from ChatGPT"""
    try:
        openai_client = get_openai_client()
        
        messages = [{"role": "system", "content": ONBOARDING_SYSTEM_ROLE}]
        messages.extend(conversation_history)
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting onboarding response: {e}")
        return f"I encountered an error: {str(e)}"

# Initialize session state variables
if 'name_entered' not in st.session_state:
    st.session_state.name_entered = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'user_exists' not in st.session_state:
    st.session_state.user_exists = False
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'onboarding_started' not in st.session_state:
    st.session_state.onboarding_started = False
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
if 'registered_users' not in st.session_state:
    st.session_state.registered_users = []

def get_all_users_from_mem0():
    """Fetch all user names from mem0 using the users() API"""
    try:
        client = get_memory_client()
        if not client:
            return []
        
        # Use the direct users() API method
        results = client.users()
        
        # Extract just the names from the results
        user_names = []
        if results and 'results' in results:
            for user in results['results']:
                if 'name' in user:
                    user_names.append(user['name'])
        
        return sorted(user_names)
    except Exception as e:
        st.error(f"Error fetching users from mem0: {e}")
        return []

# Get all users from mem0 dynamically
@st.cache_data(ttl=300)  # Cache for 5 minutes to avoid repeated API calls
def get_cached_users():
    return get_all_users_from_mem0()

existing_users = get_cached_users()

# Callback functions for buttons
def on_name_submit():
    st.session_state.submit_clicked = True
    st.session_state.show_names = False

def on_reset_name():
    st.session_state.reset_name_clicked = True
    st.session_state.show_names = True
    st.session_state.onboarding_complete = False
    st.session_state.onboarding_started = False
    st.session_state.conversation_history = []

# App header
st.title("CareerCoach AI")
st.markdown("### Your Personalized Career Advisor")
st.markdown("---")

# Handle reset name request
if st.session_state.reset_name_clicked:
    st.session_state.name_entered = False
    st.session_state.user_exists = False
    st.session_state.reset_name_clicked = False

# Sidebar with available names
if not st.session_state.name_entered and st.session_state.show_names:
    with st.sidebar:
        st.header("Available Profiles")
        
        # Refresh button to reload users from mem0
        if st.button("🔄 Refresh User List", help="Reload users from database"):
            st.cache_data.clear()  # Clear cache to force refresh
            st.rerun()
        
        if st.session_state.registered_users:
            st.subheader("📝 Your Registered Profiles")
            for name in st.session_state.registered_users:
                if st.button(f"✅ {name}", key=f"reg_btn_{name}", use_container_width=True):
                    st.session_state.user_id = name
                    st.session_state.name_entered = True
                    st.session_state.user_exists = True
                    st.session_state.onboarding_complete = True
                    st.session_state.show_names = False
                    st.rerun()
            
            st.markdown("---")
        
        if existing_users:
            st.subheader("👥 Existing Users")
            st.caption(f"Found {len(existing_users)} users in database")
            
            # Calculate midpoint for two columns
            midpoint = len(existing_users) // 2 if len(existing_users) > 1 else 1
            
            if len(existing_users) > 10:  # If many users, show in two columns
                col1, col2 = st.columns(2)
                
                with col1:
                    for name in existing_users[:midpoint]:
                        if st.button(name, key=f"btn_{name}", use_container_width=True):
                            st.session_state.user_id = name
                            st.session_state.name_entered = True
                            st.session_state.user_exists = True
                            st.session_state.onboarding_complete = True
                            st.session_state.show_names = False
                            st.rerun()
                
                with col2:
                    for name in existing_users[midpoint:]:
                        if st.button(name, key=f"btn_{name}", use_container_width=True):
                            st.session_state.user_id = name
                            st.session_state.name_entered = True
                            st.session_state.user_exists = True
                            st.session_state.onboarding_complete = True
                            st.session_state.show_names = False
                            st.rerun()
            else:  # If few users, show in single column
                for name in existing_users:
                    if st.button(name, key=f"btn_{name}", use_container_width=True):
                        st.session_state.user_id = name
                        st.session_state.name_entered = True
                        st.session_state.user_exists = True
                        st.session_state.onboarding_complete = True
                        st.session_state.show_names = False
                        st.rerun()
        else:
            st.info("No existing users found in database.")
            st.caption("Enter your name to create a new profile!")
        
        st.markdown("---")
        st.caption("Users are dynamically loaded from mem0 database.")

# Name entry interface
if not st.session_state.name_entered:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Welcome to CareerCoach AI")
        st.markdown("Please enter your full name to get started.")
        
        name_input = st.text_input("Your full name:", key="name_input")
        
        if st.session_state.name_error:
            st.error(st.session_state.name_error)
            
        st.button("Continue", on_click=on_name_submit)
        
        if st.session_state.submit_clicked:
            if not name_input:
                st.session_state.name_error = "Please enter your name to continue."
                st.session_state.submit_clicked = False
            elif not is_full_name(name_input):
                st.session_state.name_error = "Please enter your full name (first and last name)."
                st.session_state.submit_clicked = False
            else:
                st.session_state.name_error = ""
                formatted_name = format_name(name_input)
                st.session_state.user_id = formatted_name
                st.session_state.name_entered = True
                st.session_state.submit_clicked = False
                
                # Check if user exists in mem0
                st.session_state.user_exists = check_user_exists(formatted_name)
                
                if st.session_state.user_exists:
                    st.session_state.onboarding_complete = True
                else:
                    st.session_state.onboarding_complete = False
                    st.session_state.onboarding_started = False
                
                st.rerun()

# Main application interface
elif st.session_state.name_entered:

    
    # Onboarding process for new users
    if not st.session_state.onboarding_complete:
        st.markdown(f"## Hello, {st.session_state.user_id.split()[0]}!")
        
        if not st.session_state.onboarding_started:
            st.markdown("I don't have any information about you yet, but I'd love to learn more so I can provide personalized career advice!")
            st.markdown("I'll ask you some questions to understand your background, skills, and career goals.")
            
            if st.button("Let's get started! 🚀"):
                st.session_state.onboarding_started = True
                # Initialize conversation with first onboarding message
                first_response = get_onboarding_response([{"role": "user", "content": "I'm ready to get started with the onboarding process."}])
                st.session_state.conversation_history.append({"role": "assistant", "content": first_response})
                st.rerun()
        
        else:
            # Show onboarding conversation
            st.markdown("### Profile Setup")
            
            # Display conversation history
            for i, message in enumerate(st.session_state.conversation_history):
                if message["role"] == "assistant":
                    st.markdown(f"**CareerCoach AI:** {message['content']}")
                else:
                    st.markdown(f"**You:** {message['content']}")
                st.markdown("---")
            
            # Input for user response
            user_input = st.text_area("Your response:", key=f"onboarding_input_{len(st.session_state.conversation_history)}", height=100)
            
            if st.button("Send Response"):
                if user_input:
                    # Add user message to conversation
                    st.session_state.conversation_history.append({"role": "user", "content": user_input})
                    
                    # Get AI response
                    ai_response = get_onboarding_response(st.session_state.conversation_history)
                    
                    # Add AI response to conversation
                    st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Store the conversation turn in mem0
                    add_memory_from_conversation(user_input, ai_response, st.session_state.user_id)
                    
                    # Check if onboarding is complete
                    if "now have all the information I need" in ai_response.lower() or "you can now ask me" in ai_response.lower():
                        st.session_state.onboarding_complete = True
                        # Add user to registered users list
                        if st.session_state.user_id not in st.session_state.registered_users:
                            st.session_state.registered_users.append(st.session_state.user_id)
                    
                    st.rerun()
    
    # Regular career advice interface for existing/completed users
    else:
        st.write(f"Hello, **{st.session_state.user_id}**! How can I help with your career today?")
        
        # Provide example queries
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
        
        # Input area for career questions
        query = st.text_area("Your career question:", 
                             value=st.session_state.query,
                             height=80, 
                             placeholder="Ask me anything about your career, skills, or profile...")
        
        if st.session_state.query:
            st.session_state.query = ""
        
        if st.button("Get Response"):
            if query:
                with st.spinner("Searching for your profile information..."):
                    memory_results = search_memory(query, st.session_state.user_id)
                
                if memory_results:
                    st.success("Profile information found!")
                    
                    with st.expander("View your profile information", expanded=False):
                        st.json(memory_results)
                    
                    with st.spinner("Analyzing your career situation..."):
                        response = get_chatgpt_response(memory_results, query)
                    
                    st.markdown("## Your Answer")
                    st.markdown(f"<div style='background-color:#393E46; padding:20px; border-radius:10px; color:white;'>{response}</div>", 
                                unsafe_allow_html=True)
                else:
                    st.error("I couldn't find your profile information. This might be a technical issue - please try again.")
            else:
                st.warning("Please enter a career question to get personalized advice.")
        
        # Option to change name
        st.markdown("---")
        st.button("Change your name", 
                  type="secondary", 
                  help="Click to re-enter your name", 
                  on_click=on_reset_name)

# Footer
st.markdown("---")
st.caption("CareerCoach AI uses mem0 for secure profile storage and OpenAI for personalized career insights.")