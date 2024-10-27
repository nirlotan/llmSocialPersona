import streamlit as st
import streamlit_antd_components as sac
import streamlit_shadcn_ui as ui
import firebase_admin
from firebase_admin import credentials, db
import json


# Initialize session state for the button
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

# Function to handle button click
def on_button_click():
    st.session_state.button_clicked = True  # Set the button as clicked


wizard_step1 = sac.steps(
    items=[
        sac.StepsItem(title='Profiling'),
        sac.StepsItem(title='Chat'),
        sac.StepsItem(title='Feedback'),
    ], index=2
)

if wizard_step1 == "Chat":
    st.session_state['reset_coversation'] = True
    st.switch_page('app_pages/slim_chat.py')
elif wizard_step1 == "Profiling":
    st.session_state['reset_coversation'] = True
    st.switch_page('app_pages/set_profile.py')


rate1 = sac.rate(label='Engaging3', description="How engaging was the converation?", value=0.0, align='start',key="asd1")
rate2 = sac.rate(label='Personal4', description="Did you feel that the conversation was personal?" ,value=0.0, align='start',key="asd2")
rate3 = sac.rate(label='label22', value=0.0, align='start',key="asd3")

if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(st.secrets['freebase_certificate']))
    # Initialize the Firebase app
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://socialai-00007-default-rtdb.firebaseio.com/'  # Use your own database URL here
    })

# Reference to the Firebase Realtime Database
ref = db.reference("/survey_results")  # This is where survey results will be stored

# Display the button with streamlit_shadcn_ui
if not st.session_state.button_clicked:
    if ui.button("Submit Survey", key='but'):

        if 'user_description' not in st.session_state:
            st.session_state['user_description'] = None

        # Each survey response will be stored under a unique key (such as a timestamp or unique user ID)
        survey_data = {
            "profile":st.session_state['user_description'],
            "chat": [msg.content for msg in st.session_state['chat_messages']],
            "q1": rate1,
            "q2": rate2,
            "q3": rate3,
        }

        # Save survey results to Firebase (generating a new key under 'survey_results')
        ref.push(survey_data)
        on_button_click()
        st.success("Thank you for submitting the survey!")

else:
    st.write("Survey can only be sumbitted once.")
# Button to submit the survey

