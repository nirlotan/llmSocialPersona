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

st.set_page_config(page_title="≋SøcialPersonaCore★", page_icon="🗣️", layout="wide")


if "selected_user" not in st.session_state:
    switch_page('main')
if "previous_user" not in st.session_state:
    st.session_state['previous_user'] = st.session_state['selected_user']


# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")

def reset_conversation():
    msgs.clear()
    st.session_state.suggested_selection = ''
    st.toast("Reset Conversation", icon="🚩")

@st.cache_data
def read_data():
    return pd.read_excel("https://www.dropbox.com/scl/fi/ilya513nxe3r7uoyfpwtc/persona_details.xlsx?rlkey=dtw5zb3g0u9qzde4e7gtwbay2&st=lg5v5uyc&dl=1")

df = read_data()

if st.session_state['selected_user'] != st.session_state['previous_user']:
    st.toast("Switched User", icon="🚩")
    msgs.clear()
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
    if inner_cols[3].button("No Persona", use_container_width=True):
        st.session_state['selected_user'] = "DefaultChatBot"
        reset_conversation()

    use_self_description = ui.switch(default_checked=True, label="Use user's self description")

with title_cols[1].container(border=True):
    container_cols = st.columns([1, 4], vertical_alignment='center')
    st.write(selected_user_data['description'])
    container_cols[0].markdown(f'<img src="{image}" alt="My Image" width="50" height="50" style="border-radius: 50%;">',
                               unsafe_allow_html=True)
    container_cols[1].markdown(f"#### {selected_user_data['screen_name']}")

    with st.expander("SocialVec profile insights", expanded=False):
        st.markdown(body=selected_user_data['persona_description'])


openai_api_key = st.secrets["openai_api_key"]

 # Set up the LangChain, passing in Message History
system_message = """I want you to act as a person, not a chatbot.  Your need to engage with the user in a friendly conversation.
You have a specific persona that you need to stick to it. For this persona, you must use details I will provide here below.
Be concise with your messages. Don't exceed 100 words.
Share details about you in the conversation and show genuine interest in the user.
Proactively introduce new and engaging topics to keep the conversation flowing naturally.
Throughout the conversation maintain a fun, lighthearted tone.
Prioritize connection, creativity, and a sense of enjoyment in the interaction."""

system_message += f"Details to consider: Your name is {selected_user}."

if use_self_description:
    system_message += f"You describe yourself as: {df[df['screen_name']==selected_user]['description'].iloc[0]}"

system_message += f"Additional important personal information: {df[df['screen_name']==selected_user]['persona_description'].iloc[0]}"


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


# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    title_cols[0].chat_message(msg.type).write(msg.content)

with bottom():
    bottom_columns = st.columns([3, 1],vertical_alignment='bottom')

    user_prompt = bottom_columns[0].chat_input()

    with bottom_columns[1]:
        btn = sac.buttons(
            items=["Hi! How are you doing?", "Hi! Who are you?", "What are you up to?",
                                        "What are your plans for today?", "Tell me more about yourself", "What are your hobbies?"],
            label = 'Suggested Messages', index=0, align = 'center', size = 'xs', key="asvv1")

        st.write(btn)

with st.container():
    if user_prompt:
        title_cols[0].chat_message("human").write(user_prompt)
        # Note: new messages are saved to history automatically by Langchain during run
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"sentence": user_prompt}, config)
        title_cols[0].chat_message("ai", avatar='human').write(response.content)
        last_user_prompt = user_prompt

    # Draw the messages at the end, so newly generated ones show up immediately

