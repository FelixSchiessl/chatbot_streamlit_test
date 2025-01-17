import streamlit as st
from openai import OpenAI
import json

# Assessment areas and questions
ASSESSMENT_AREAS = {
    "data_readiness": {
        "title": "Data Infrastructure & Quality",
        "questions": [
            "How would you rate the quality and organization of your company's data?",
            "Do you have established data governance policies?",
            "How is sensitive data currently handled in your organization?"
        ]
    },
    "technical_capability": {
        "title": "Technical Infrastructure",
        "questions": [
            "What computing resources do you currently have available?",
            "Does your team have experience with AI/ML technologies?",
            "How integrated are your current technical systems?"
        ]
    },
    "business_alignment": {
        "title": "Business Strategy & Use Cases",
        "questions": [
            "What are your primary objectives for implementing GenAI?",
            "Have you identified specific use cases for GenAI?",
            "How does GenAI align with your current business strategy?"
        ]
    },
    "change_readiness": {
        "title": "Organizational Change Readiness",
        "questions": [
            "How would you describe your organization's culture towards technological change?",
            "What training programs do you have in place?",
            "How do you plan to manage the transition to AI-enhanced workflows?"
        ]
    }
}

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_area" not in st.session_state:
        st.session_state.current_area = "introduction"
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "assessment_complete" not in st.session_state:
        st.session_state.assessment_complete = False

def get_system_prompt():
    """Return the system prompt for the AI."""
    return """You are an AI Readiness Assessment expert. Guide the user through evaluating their organization's readiness 
    for implementing Generative AI. Ask questions one at a time, listen carefully to responses, and provide thoughtful 
    insights. Be professional but conversational. Focus on understanding their current state and providing actionable 
    recommendations. If you detect potential risks or gaps, address them constructively."""

def generate_report(responses):
    """Generate a summary report based on assessment responses."""
    report_prompt = f"""Based on the following assessment responses, provide a comprehensive readiness report with specific 
    recommendations. Include strengths, areas for improvement, and next steps. Responses: {json.dumps(responses, indent=2)}"""
    
    return report_prompt

def main():
    st.title("🤖 GenAI Readiness Assessment")
    st.write(
        "Welcome to the Generative AI Readiness Assessment tool. This interactive assessment will help evaluate "
        "your organization's preparedness for implementing GenAI solutions and provide tailored recommendations."
    )

    initialize_session_state()

    # API key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return

    client = OpenAI(api_key=openai_api_key)

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle initial message
    if not st.session_state.messages:
        # Add system prompt
        st.session_state.messages.append({
            "role": "system",
            "content": get_system_prompt()
        })
        # Add welcome message
        initial_prompt = "Hello! I'll be guiding you through assessing your organization's GenAI readiness. Let's start with understanding your current data infrastructure. How would you rate the quality and organization of your company's data?"
        st.session_state.messages.append({
            "role": "assistant",
            "content": initial_prompt
        })
        with st.chat_message("assistant"):
            st.markdown(initial_prompt)

    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and stream response
        stream = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better assessment capabilities
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Store response in assessment data
        if st.session_state.current_area in ASSESSMENT_AREAS:
            if st.session_state.current_area not in st.session_state.responses:
                st.session_state.responses[st.session_state.current_area] = []
            st.session_state.responses[st.session_state.current_area].append({
                "question": st.session_state.messages[-2]["content"],
                "response": prompt
            })

    # Generate final report when assessment is complete
    if st.session_state.assessment_complete:
        st.write("---")
        st.subheader("Assessment Report")
        report_prompt = generate_report(st.session_state.responses)
        
        report_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": report_prompt}],
            stream=False,
        )
        
        st.markdown(report_response.choices[0].message.content)

if __name__ == "__main__":
    main()