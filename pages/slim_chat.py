from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


import streamlit as st
import pandas as pd
import os
from streamlit_extras.bottom_container import bottom
import streamlit_shadcn_ui as ui
import streamlit_antd_components as sac
from streamlit_javascript import st_javascript
from user_agents import parse
import time
import toml

import streamlit_shadcn_ui as ui

user_prompt = False

# if "user_description" not in st.session_state:
#     st.switch_page('pages/submit_feedback.py')
try:
    # check user agent to suppress non-mandatory parts when running on mobile
    ua_string = st_javascript("""window.navigator.userAgent;""")
    user_agent = parse(ua_string)
    st.session_state.is_session_pc = user_agent.is_pc
except:
    st.session_state.is_session_pc = True

config = toml.load("config.toml")




# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
msgs_len = len(msgs.messages)
disable_feedback = True if msgs_len < config['minimal_number_of_messages'] else False

wizard_step1 = sac.steps(
    items=[
        sac.StepsItem(title='Profiling'),
        sac.StepsItem(title='Chat'),
        sac.StepsItem(title='Feedback', disabled=disable_feedback),
    ], index=1
)

# Initialize session state for the button
if "reset_coversation" not in st.session_state:
    st.session_state.reset_coversation = False
elif st.session_state['reset_coversation']:
    st.session_state['reset_coversation'] = False
    msgs.clear()
    msgs_len = 0

openai_api_key = st.secrets["openai_api_key"]

 # Set up the LangChain, passing in Message History
system_message = """I want you to act as a person, not a chatbot.  Your need to engage with the user in a friendly conversation.
You have a specific persona that you need to stick to it. For this persona, you must use details I will provide here below. 
Any detail that is not specific enough, you choose something specific and stick to it. You have to be really convincing as an actual person.
Be concise with your messages. Don't exceed 100 words.
Share details about you in the conversation and show genuine interest in the user.
Proactively introduce new and engaging topics to keep the conversation flowing naturally.
Throughout the conversation maintain a fun, lighthearted tone.
Prioritize connection, creativity, and a sense of enjoyment in the interaction."""


if 'user_description' in st.session_state:
    system_message += f"Details to consider: {st.session_state['user_description']}."

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{sentence}"),
    ]
)

chain = prompt | ChatOpenAI(api_key=openai_api_key,
                            model="gpt-4o-mini",
                            temperature=1,
                            )
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="sentence",
    history_messages_key="history",
)

last_user_prompt = ""

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

with bottom():
    bottom_columns = st.columns([3, 1],vertical_alignment='bottom')
#    user_prompt = bottom_columns[0].chat_input()


    predefined_messages = [ "Hi! How are you doing?", "Hi! Who are you?", "What are you up to?",
                       "What are your plans for today?", "Tell me more about yourself", "What are your hobbies?",
                     "How do you like to spend your evenings?","What's your favorite way to relax?", "What are some goals you're working towards?"]


    # Free text input option
    user_text = st.chat_input(placeholder="Type a message or choose a suggested message from the list:")

    # Display the select box for predefined messages
    selected_message = bottom_columns[0].selectbox("Or choose from this list:", predefined_messages, index=0)

    # Button to send the message
    if bottom_columns[1].button("Send Suggested") or user_text:
        # If the user provided custom input, use that, otherwise use the selected predefined message
        user_prompt = user_text if user_text else selected_message
        user_text = None

    wizard_step2 = sac.steps(
        items=[
            sac.StepsItem(title='Profiling'),
            sac.StepsItem(title='Chat'),
            sac.StepsItem(title='Feedback', disabled=disable_feedback),
        ], index=1, key="wiz2"
    )

    next_columns = st.columns([4,1])
    if disable_feedback:
        next_columns[0].caption(
            f"You will be able to move to the feedback page after at least {config['minimal_number_of_messages']} message.")
    else:
        next_columns[0].caption(
            f"Can continue to chat or move to the feedback screen")
        next_button = next_columns[1].button("Feedback")

with st.container():
    if user_prompt:
        st.chat_message("human").write(user_prompt)
        # Note: new messages are saved to history automatically by Langchain during run
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"sentence": user_prompt}, config)

        with st.chat_message("ai"):
            message_placeholder = st.empty()  # Create a placeholder for the assistant's response
            length_of_wait = int(len(response.content)/40)
            for i in range(length_of_wait):  # Adjust the range for how long you want to show the "thinking" animation
                if i % 4 == 0:
                    message_placeholder.write("Typing")
                elif i % 4 == 1:
                    message_placeholder.write("Typing.")
                elif i % 4 == 2:
                    message_placeholder.write("Typing..")
                else:
                    message_placeholder.write("Typing...")
                time.sleep(0.5)  # Adjust the speed of the animation

            # After the delay, update the placeholder with the actual response
            message_placeholder.write(response.content)


        #chat_area[0].chat_message("ai", avatar='human').write(response.content)
        last_user_prompt = user_prompt
        st.session_state['submitted'] = False


if not disable_feedback and (next_button or wizard_step2 == "Feedback" or wizard_step1 == "Feedback"):
    st.session_state['reset_coversation'] = True
    st.session_state['chat_messages'] = msgs.messages
    st.switch_page('pages/submit_feedback.py')
elif wizard_step2 == "Profiling" or wizard_step1 == "Profiling":
    st.session_state['reset_coversation'] = True
    st.switch_page('pages/set_profile.py')