# app.py

import streamlit as st
import google.generativeai as genai
import datetime  # Import the datetime library

# --- Page Configuration ---
st.set_page_config(
    page_title="SkeeterBot",
    page_icon="🦟",
    layout="wide"
)

# --- CSS to Fix Input Bar and Clean Up File Uploader ---
st.markdown("""
    <style>
    /* Add padding to the bottom of the main content area */
    .block-container {
        padding-bottom: 6rem; /* Ensures last chat message isn't hidden by the input bar */
    }

    /* Style the block that contains the input widgets */
    div[data-testid="stHorizontalBlock"] {
        position: fixed;     /* Pin the container to a fixed position */
        bottom: 0;           /* Position it at the bottom of the viewport */
        left: 0;             /* Stretch it to the left edge */
        width: 100%;         /* Make it full-width */
        background-color: white; /* Give it a solid background */
        padding: 1rem 1rem;  /* Add some spacing */
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1); /* Add a subtle shadow for depth */
        z-index: 100;        /* Ensure it's on top of other content */
    }
    
    /* --- CSS to hide the 'Drag and drop' box --- */
    div[data-testid="stFileUploader"] section {
        padding: 0; /* Remove padding around the button */
    }
    div[data-testid="stFileUploader"] section > input + div {
        display: none; /* Hide the drag-and-drop area */
    }
    </style>
""", unsafe_allow_html=True)


# --- API Key & Model Configuration ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    st.error("API Key not found or invalid. Please check your .streamlit/secrets.toml file.")
    st.stop()

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# --- DYNAMIC RAG-POWERED SYSTEM PROMPT ---
def get_system_prompt(current_date):
    """
    Generates a dynamic system prompt based on live data.
    """
    # --- THIS IS THE RAG SIMULATION ---
    current_alert = "Mosquito-Borne Illness Advisory for Norfolk. High trap counts in Lafayette-Winona and Ghent neighborhoods."
    
    retrieved_guidelines = """
    **[Document: "Norfolk's 4 Ds of Prevention"]**
    1.  **DUMP**: Dump out standing water weekly. Mosquitoes breed in water. Check flowerpots, buckets, tires, and toys.
    2.  **DRESS**: Wear long, loose, and light-colored clothing to cover your skin.
    3.  **DEET**: Use insect repellent containing DEET, Picaridin, or Oil of Lemon Eucalyptus.
    4.  **DAWN & DUSK**: Limit outdoor activity when mosquitoes are most active (dawn and dusk).
    
    **[Document: "Tip 'n Toss Program Explained"]**
    * **WHY**: The Aedes mosquito (a key vector in Norfolk) can lay eggs in a space as small as a bottlecap. Removing their breeding ground is the #1 way to control the population.
    * **HOW**: Walk your property weekly. Tip over any items holding water. Toss out any unneeded containers.
    """
    
    return f"""
You are "SkeeterBot," an advanced, RAG-powered AI specialist from the City of Norfolk's Public Health Department.
Your mission is to provide residents with hyper-local, real-time, and actionable advice based *only* on the data provided to you.

**[RAG Data Feed (Simulated)]**
* **Current Date:** {current_date}
* **Live Alert:** {current_alert}
* **Retrieved Guidelines:** {retrieved_guidelines}

**[Core Directives & Chain-of-Thought]**
1.  **Analyze Query:** Deconstruct the user's text and all uploaded files. What is their primary intent? (Analysis, RAG-Query, Greeting, General Question, Medical)
2.  **Retrieve & Synthesize:** Cross-reference the query with the **[RAG Data Feed]**. You MUST prioritize information from this feed.
3.  **Formulate Response:**
    * For analysis requests, use the structured `[Risk Level]` format.
    * For RAG-Queries (like "are mosquitoes bad?" or "what should I do?"), answer *using the retrieved RAG data*.
    * For Greetings or General Questions, respond naturally.
    * For medical questions, STOP and use the 'Medical Safety Warning' response.

---
**Few-Shot Examples (How to Respond)**

**Example 1: High Risk Scenario**
[USER]: "What do you think of this? Is it a problem?" (User uploads image of a clogged gutter)
[AI RESPONSE]:
[File Analysis]: This image shows a clogged gutter filled with standing water... [Risk Level]: 🔴 High Risk [Expert Assessment]: This is a perfect breeding ground for mosquitoes... [Actionable Advice]:

Immediate Action: Please clear this gutter...

Prevention: Ensure all gutters are clean...


**Example 2: Medium Risk Scenario**
[USER]: "Is my bird bath okay?" (User uploads video of a bird bath)
[AI RESPONSE]:
[File Analysis]: This video shows a bird bath with still, unchanged water. [Risk Level]: 🟡 Medium Risk [Expert Assessment]: While great for birds, bird baths are a very common mosquito breeding site... [Actionable Advice]:

Immediate Action: Please dump the old water out.

Prevention: You must replace the water at least twice a week.


**Example 3: Safe (Low Risk) Scenario**
[USER]: "How does my rain barrel look?" (User uploads image of a rain barrel with a secure mesh screen)
[AI RESPONSE]:
[File Analysis]: This image shows a well-maintained rain barrel with a fine mesh screen... [Risk Level]: ✅ Safe (Low Risk) [Expert Assessment]: This is a fantastic example of responsible water conservation! [Actionable Advice]:

Good Work: Keep up the great job!

Maintenance: Continue to check the screen periodically...


**Example 4: RAG-Powered Response**
[USER]: "Are mosquitoes bad in Norfolk right now and what should I do?"
[AI RESPONSE]:
Yes, based on the latest city data, mosquito activity is high. [Current Situation - Sourced from Live Data]... [Actionable Advice - Sourced from "Norfolk's 4 Ds" Guide]...


**Example 5: Diversified Conversation (with Image)**
[USER]: "Here's a pic of my yard. By the way, how many mosquito species are in Virginia?" (User uploads an image of their backyard)
[AI RESPONSE]:
That's a nice, well-maintained yard! As for your question, there are over 60 species of mosquitoes found in Virginia...


**Example 6: Simple Greeting (Text-Only)**
[USER]: "Hello"
[AI RESPONSE]:
Hello! How can I help you today?


**Example 7: Medical Guardrail Test**
[USER]: "I have a bunch of bites and a fever, is it West Nile?"
[AI RESPONSE]:
[Medical Safety Warning]: I am an AI assistant and cannot provide medical advice or diagnose any illness. Please contact your doctor or a healthcare professional immediately...

"""
# --- END OF NEW SYSTEM PROMPT ---


# --- App Title ---
st.title("🦟 SkeeterBot")

# --- Sighting Report Expander ---
with st.expander("Report a Sighting 📍"):
    st.write("Help the City of Norfolk! If you've identified a mosquito or a major breeding site, please report it here.")
    
    with st.form("report_form"):
        report_location = st.text_input("Location (Address, Zip, or Street Name)")
        report_species = st.selectbox("Mosquito Species (Select one)", 
                                     ["", "Aedes albopictus (Asian Tiger)", "Culex pipiens (House Mosquito)", 
                                      "Aedes aegypti (Yellow Fever Mosquito)", "Anopheles quadrimaculatus", "Other/Unknown"])
        report_image = st.file_uploader("Upload Image of Sighting", type=["jpg", "png", "jpeg"])
        
        submitted = st.form_submit_button("Submit Report")
        
        if submitted:
            if not report_location or not report_species or not report_image:
                st.error("Please fill out all fields and upload an image.")
            else:
                # Save to the CSV log file
                try:
                    with open("sightings_log.csv", "a") as f:
                        if f.tell() == 0:
                            f.write("Timestamp,Location,Species\n")
                        f.write(f"{datetime.datetime.now()},{report_location},{report_species}\n")
                    
                    st.success("✔ Thank you! Your report has been submitted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# --- $$$ NEW: QUICK CONTACT INFO $$$ ---
st.markdown("For urgent issues or to speak to a person, call the **Norfolk Cares Hotline: (757) 664-6510**")


# --- Starter Questions ---
st.markdown("##### Sample Questions")
st.markdown("""
* _**"Are mosquitoes bad right now?"**_
* _**"Is this a breeding site?"**_ (Try uploading a file first!)
* _**"How to protect my yard?"**_
* _**"Tell me a fun fact"**_
""")

st.markdown("---") # Visual separator


# --- Display Chat History (Handles Images) ---
for message in st.session_state.chat_history:
    with st.chat_message(name="user" if message["role"] == "user" else "assistant",
                         avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        
        # Loop through all parts of the message
        for part in message["parts"]:
            if isinstance(part, str):
                st.markdown(part) # Display text
            elif isinstance(part, dict) and "image" in part["mime_type"]:
                st.image(part["data"], width=300) # Display image
            elif isinstance(part, dict) and "video" in part["mime_type"]:
                st.video(part["data"]) # Display video

# --- Input Bar (with Uploader Reset) ---
input_cols = st.columns([1, 4]) # File-Upload | Chat
with input_cols[0]:
    uploaded_files = st.file_uploader(
        "Image / Video / File", 
        type=["jpg", "jpeg", "png", "mp4", "mov", "avi", "pdf"],
        label_visibility="visible",
        key=f"file_uploader_{st.session_state.uploader_key}", # Use the resetting key
        accept_multiple_files=True
    )
with input_cols[1]:
    user_input = st.chat_input("Ask a question...", key="chat_input")

# --- Chat Processing Logic ---
if user_input:
    # --- 1. Prepare parts for both history (with bytes) and AI (with objects) ---
    parts_for_history = []
    parts_for_ai = [get_system_prompt(datetime.date.today().strftime("%B %d, %Y"))]

    if uploaded_files:
        for file in uploaded_files:
            file_bytes = file.getvalue()
            parts_for_history.append({"mime_type": file.type, "data": file_bytes})
            parts_for_ai.append({"mime_type": file.type, "data": file_bytes})
    
    parts_for_history.append(user_input)
    parts_for_ai.append(user_input)

    # --- 2. Add user message to history (with images) ---
    st.session_state.chat_history.append({"role": "user", "parts": parts_for_history})

    # --- 3. Call the AI ---
    try:
        response = model.generate_content(parts_for_ai)
        st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
    except Exception as e:
        st.session_state.chat_history.append({"role": "model", "parts": [f"Sorry, an error occurred: {e}"]})

    # --- 4. Reset the file uploader and rerun ---
    st.session_state.uploader_key += 1
    st.rerun()