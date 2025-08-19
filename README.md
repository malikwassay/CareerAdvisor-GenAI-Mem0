# CareerCoach AI

A sophisticated AI-powered career coaching application that provides personalized career guidance using advanced memory storage and natural language processing. Built with Streamlit, mem0 for persistent user profiles, and OpenAI for intelligent career advice.

## Features

### Core Functionality
- **Personalized Career Coaching**: AI-driven advice based on comprehensive user profiles
- **Persistent Memory Storage**: User profiles and conversation history stored using mem0
- **Intelligent Onboarding**: Adaptive interview process that adjusts to user's profession
- **User Profile Management**: Browse and select from existing user profiles
- **Natural Language Interaction**: Conversational interface for career questions
- **Context-Aware Responses**: Differentiated handling of factual queries vs. advice requests

### Advanced Capabilities
- **Field-Adaptive Onboarding**: Customized questions based on user's profession
- **Comprehensive Profile Building**: Collects personal, professional, and career aspiration data
- **Memory-Enhanced Responses**: Leverages stored profile information for personalized advice
- **Session State Management**: Seamless user experience across interactions
- **Dynamic User Discovery**: Real-time loading of existing users from mem0 database

## Prerequisites

### Required Services
- **mem0 API**: User profile and memory storage
- **OpenAI API**: Natural language processing and career advice generation
- **Python 3.8+**: Runtime environment

### API Keys Required
- mem0 API key
- OpenAI API key

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/malikwassay/CareerAdvisor-GenAI-Mem0
cd careercoach-ai
```

### 2. Install Dependencies
```bash
pip install streamlit mem0ai openai python-dotenv
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the project root:
```env
MEM0_API_KEY=your-mem0-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

For Streamlit Cloud deployment, use `.streamlit/secrets.toml`:
```toml
MEM0_API_KEY = "your-mem0-api-key-here"
OPENAI_API_KEY = "your-openai-api-key-here"
```

## Dependencies

```txt
streamlit>=1.28.0
mem0ai>=0.1.0
openai>=1.0.0
python-dotenv>=1.0.0
```

## Usage

### Starting the Application
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### User Flow

**New Users:**
1. Enter full name on welcome screen
2. Complete adaptive onboarding interview
3. Receive personalized career advice

**Returning Users:**
1. Select name from existing user list
2. Ask career questions immediately
3. Get responses based on stored profile

### Interface Components

**Welcome Screen:**
- Full name input with validation
- Dynamic user list in sidebar
- Profile selection buttons

**Onboarding Process:**
- Conversational interview
- Field-specific question adaptation
- Progressive profile building

**Career Advice Interface:**
- Natural language question input
- Profile information display
- Personalized response generation

## Technical Architecture

### System Components

**Memory Management:**
- mem0 client for profile storage
- Conversation history persistence
- User discovery and retrieval

**AI Integration:**
- OpenAI GPT-4-mini for responses
- Dual system roles (onboarding vs. advice)
- Context-aware prompt engineering

**Session Management:**
- Streamlit session state
- User flow orchestration
- Error handling and validation

### Data Models

**User Profile Information:**
- **Personal Data**: Name, birth date, location, contact details
- **Professional Background**: Current role, company, salary, employment type
- **Technical Skills**: Field-specific tools, certifications, competencies
- **Work Experience**: Previous roles, responsibilities, duration
- **Career Aspirations**: Target roles, industries, preferences
- **Timeline Constraints**: Contract dates, certification goals

### System Roles

**Career Advisor Role:**
```python
CAREER_ADVISOR_SYSTEM_ROLE = """
Expert career advisor providing personalized guidance based on:
- User's professional background and skills
- Career aspirations and timeline constraints
- Industry-specific insights and recommendations
- Actionable career development advice
"""
```

**Onboarding Assistant Role:**
```python
ONBOARDING_SYSTEM_ROLE = """
Adaptive interview assistant that:
- Collects comprehensive user information
- Adapts questions to user's specific field
- Maintains conversational flow
- Signals completion when sufficient data collected
"""
```

## Key Functions

### User Management
- `check_user_exists()`: Verify user presence in mem0
- `get_all_users_from_mem0()`: Retrieve existing user list
- `format_name()`: Standardize name formatting
- `is_full_name()`: Validate full name input

### Memory Operations
- `add_memory_from_conversation()`: Store conversation turns
- `search_memory()`: Retrieve relevant profile information
- `get_memory_client()`: Initialize mem0 connection

### AI Integration
- `get_chatgpt_response()`: Generate career advice responses
- `get_onboarding_response()`: Handle onboarding conversations
- `get_openai_client()`: Initialize OpenAI connection

### Session Management
- Multiple session state variables for flow control
- Callback functions for button interactions
- Dynamic UI state management

## Configuration

### API Configuration

**mem0 Integration:**
```python
client = MemoryClient(api_key=mem0_api_key)
```

**OpenAI Configuration:**
```python
client = openai.OpenAI(api_key=openai_api_key)
model = "gpt-4o-mini"
```

### Field-Specific Adaptations

The onboarding process adapts to user professions:

**Engineering Fields:**
- CAD software proficiency
- Project management tools
- Professional certifications
- Construction/design experience

**Healthcare Professions:**
- Medical specializations
- Clinical equipment familiarity
- Professional licenses
- Hospital system experience

**Education Sector:**
- Subject area expertise
- Grade level preferences
- Classroom management tools
- Teaching certifications

**Business & Finance:**
- Industry-specific software
- Analytical tools
- Professional certifications
- Market experience

## User Interface Features

### Sidebar Components
- **User List Display**: Dynamic loading from mem0
- **Profile Selection**: One-click user switching
- **Refresh Functionality**: Real-time user list updates
- **Registered Users**: Session-specific user tracking

### Main Interface Elements
- **Welcome Screen**: Name validation and entry
- **Onboarding Chat**: Conversational profile building
- **Career Advice**: Question input and response display
- **Profile Information**: Expandable data view

### Styling and UX
- Centered layout design
- Clear visual hierarchy
- Responsive button interactions
- Error message handling
- Progress indication

## Error Handling

### API Error Management
- Connection validation for mem0 and OpenAI
- Graceful degradation for API failures
- User-friendly error messages
- Retry mechanisms for temporary failures

### Input Validation
- Full name requirement enforcement
- Empty query prevention
- Session state consistency checks
- Profile existence verification

### Memory Operations
- Error handling for memory storage/retrieval
- Fallback responses for missing data
- Connection failure recovery
- Data consistency validation

## Security Considerations

### API Key Management
- Environment variable storage
- Secrets file configuration for deployment
- No hardcoded credentials
- Secure client initialization

### Data Privacy
- User-specific memory isolation
- Secure profile storage with mem0
- No client-side data persistence
- Privacy-compliant conversation handling

### Session Security
- Session state isolation
- User authentication through name verification
- Secure memory access patterns

## Deployment

### Local Development
```bash
# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Streamlit Cloud Deployment
1. **Repository Setup**: Connect GitHub repository
2. **Secrets Configuration**: Add API keys in Streamlit dashboard
3. **Dependencies**: Ensure requirements.txt is complete
4. **Deploy**: Automatic deployment from main branch

### Production Considerations
- **Environment Variables**: Secure API key management
- **Error Monitoring**: Log aggregation and alerting
- **Performance**: Session state optimization
- **Scaling**: User load management with mem0

## Customization

### Onboarding Questions
Modify field-specific questions in the system role:
```python
ONBOARDING_SYSTEM_ROLE = """
# Add new profession adaptations
# Update question categories
# Modify completion criteria
"""
```

### Career Advice Logic
Customize advice generation:
```python
CAREER_ADVISOR_SYSTEM_ROLE = """
# Update advice categories
# Modify response templates
# Add industry-specific insights
"""
```

### UI Customization
- Modify Streamlit page configuration
- Update styling and layout
- Customize component behavior
- Add new interface elements

## Troubleshooting

### Common Issues

**API Connection Problems:**
- Verify API keys in environment variables
- Check network connectivity
- Validate API key permissions
- Monitor rate limits

**Memory Storage Issues:**
- Confirm mem0 API access
- Check user ID formatting
- Verify memory search queries
- Monitor storage limits

**Onboarding Flow Problems:**
- Review conversation history structure
- Validate completion detection logic
- Check field-specific adaptations
- Monitor response generation

### Debugging Steps

1. **Check Environment Setup:**
   ```bash
   # Verify API keys
   echo $MEM0_API_KEY
   echo $OPENAI_API_KEY
   ```

2. **Test API Connections:**
   - Validate mem0 client initialization
   - Test OpenAI API access
   - Verify service availability

3. **Monitor Session State:**
   - Check Streamlit session variables
   - Validate user flow logic
   - Review error handling

## Performance Optimization

### Caching Strategies
- `@st.cache_resource` for API clients
- `@st.cache_data` for user lists
- Session state for conversation history
- Efficient memory queries

### Memory Management
- Optimize conversation storage
- Efficient profile retrieval
- Strategic session state usage
- Regular cache clearing

### API Usage Optimization
- Batch memory operations where possible
- Optimize prompt lengths
- Use appropriate OpenAI models
- Implement request rate limiting

## Future Enhancements

### Planned Features
- **Multi-language Support**: Internationalization capabilities
- **Advanced Analytics**: Career progression tracking
- **Integration Expansions**: LinkedIn, job boards, salary data
- **Enhanced Personalization**: Learning from user interactions

### Technical Improvements
- **Database Migration**: From mem0 to dedicated database
- **Advanced Caching**: Redis integration for performance
- **API Optimization**: GraphQL for efficient data fetching
- **Real-time Features**: WebSocket integration for live updates


**Note**: This application requires active mem0 and OpenAI API connections. Ensure all credentials are properly configured and services are accessible before deployment.
