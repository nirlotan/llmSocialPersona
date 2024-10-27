from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

import streamlit as st
import pandas as pd
import os
from streamlit_extras.bottom_container import bottom
import streamlit_shadcn_ui as ui
from streamlit_extras.switch_page_button import switch_page
import streamlit_antd_components as sac
from streamlit_javascript import st_javascript
from user_agents import parse

st.set_page_config(page_title="≋SøcialPersonaCore★", page_icon="🗣️", layout="wide")


if "selected_user" not in st.session_state:
    switch_page('main')
if "previous_user" not in st.session_state:
    st.session_state['previous_user'] = st.session_state['selected_user']

try:
    # check user agent to suppress non-mandatory parts when running on mobile
    ua_string = st_javascript("""window.navigator.userAgent;""")
    user_agent = parse(ua_string)
    st.session_state.is_session_pc = user_agent.is_pc
except:
    st.session_state.is_session_pc = True

# Set up memory
msgs_1 = StreamlitChatMessageHistory(key="langchain_messages")
msgs_2 = StreamlitChatMessageHistory(key="langchain_messages")

def reset_conversation():
    msgs_1.clear()
    msgs_2.clear()
    st.session_state.suggested_selection = ''
    st.toast("Reset Conversation", icon="🚩")

@st.cache_data
def read_data():
    return pd.read_excel("https://www.dropbox.com/scl/fi/ilya513nxe3r7uoyfpwtc/persona_details.xlsx?rlkey=dtw5zb3g0u9qzde4e7gtwbay2&st=lg5v5uyc&dl=1")

df = read_data()

if st.session_state['selected_user'] != st.session_state['previous_user']:
    st.toast("Switched User", icon="🚩")
    msgs_1.clear()
    msgs_2.clear()
    st.session_state['previous_user'] = st.session_state['selected_user']

selected_user = st.session_state['selected_user']
selected_user_data = st.session_state['selected_user_data']
image = selected_user_data["image"]

title_cols = st.columns([5,2])
with title_cols[0]:
    inner_cols = st.columns([4,1,1,1],vertical_alignment='bottom')
    inner_cols[0].title("🗣️ ≋SøcialPersonaCore★ chat")
    if inner_cols[1].button("Switch User", use_container_width=True):
        switch_page('main')
    if inner_cols[2].button("Reset Chat", use_container_width=True):
        reset_conversation()

    use_self_description = ui.switch(default_checked=True, label="Use user's self description")

openai_api_key = st.secrets["openai_api_key"]

 # Set up the LangChain, passing in Message History
system_message_1 = """I want you to act as a person, not a chatbot.  Your need to engage with the user in a friendly conversation.
You have a specific persona that you need to stick to it. For this persona, you must use details I will provide here below.
Be concise with your messages. Don't exceed 100 words.
Share details about you in the conversation and show genuine interest in the user.
Proactively introduce new and engaging topics to keep the conversation flowing naturally.
Throughout the conversation maintain a fun, lighthearted tone.
Prioritize connection, creativity, and a sense of enjoyment in the interaction."""

system_message_2 = system_message_1


system_message_1 += f"Details to consider: Your name is {selected_user}."

if use_self_description:
    system_message_1 += f"You describe yourself as: {df[df['screen_name']==selected_user]['description'].iloc[0]}"

system_message_1 += f"Additional important personal information: {df[df['screen_name']==selected_user]['persona_description'].iloc[0]}"

prompt_1 = ChatPromptTemplate.from_messages(
    [
        ("system", system_message_1),
        MessagesPlaceholder(variable_name="history1"),
        ("human", "{sentence}"),
    ]
)

prompt_2 = ChatPromptTemplate.from_messages(
    [
        ("system", system_message_2),
        MessagesPlaceholder(variable_name="history2"),
        ("human", "{sentence}"),
    ]
)

chain_1 = prompt_1 | ChatOpenAI(api_key=openai_api_key,
                            model="gpt-4o-mini",
                            temperature=1,
                            )

chain_2 = prompt_2 | ChatOpenAI(api_key=openai_api_key,
                            model="gpt-4o-mini",
                            temperature=1,
                            )

chain_with_history_1 = RunnableWithMessageHistory(
    chain_1,
    lambda session_id: msgs_1,
    input_messages_key="sentence1",
    history_messages_key="history1",
)
chain_with_history_2 = RunnableWithMessageHistory(
    chain_2,
    lambda session_id: msgs_2,
    input_messages_key="sentence2",
    history_messages_key="history2",
)

chat_columns = st.columns(2)

chat_columns[0].markdown(f"#### User: {st.session_state['selected_user']}")
chat_columns[1].markdown(f"#### Default chatbot")

# Render current messages from StreamlitChatMessageHistory
for msg_1 in msgs_1.messages:
    chat_columns[0].chat_message(msg_1.type).write(msg_1.content)

for msg_2 in msgs_2.messages:
    chat_columns[1].chat_message(msg_2.type).write(msg_2.content)


with bottom():
    user_prompt = st.chat_input()

with chat_columns[0].container():
    if user_prompt:
        chat_columns[0].chat_message("human").write(user_prompt)
        # Note: new messages are saved to history automatically by Langchain during run
        config = {"configurable": {"session_id": "any"}}
        response1 = chain_with_history_1.invoke({"sentence": user_prompt}, config)
        chat_columns[0].chat_message("ai", avatar='human').write(response1.content)
        last_user_prompt = user_prompt

with chat_columns[1].container():
    if user_prompt:
        chat_columns[1].chat_message("human").write(user_prompt)
        # Note: new messages are saved to history automatically by Langchain during run
        config = {"configurable": {"session_id": "any"}}
        response2 = chain_with_history_2.invoke({"sentence": user_prompt}, config)
        chat_columns[1].chat_message("ai", avatar='human').write(response2.content)
        last_user_prompt = user_prompt

    # Draw the messages at the end, so newly generated ones show up immediately

