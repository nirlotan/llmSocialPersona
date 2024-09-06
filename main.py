import streamlit_shadcn_ui as ui
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="≋SøcialPersonaCore★", page_icon="🗣️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("https://www.dropbox.com/scl/fi/ilya513nxe3r7uoyfpwtc/persona_details.xlsx?rlkey=dtw5zb3g0u9qzde4e7gtwbay2&st=lg5v5uyc&dl=1").sample(frac=1)
    return df[df['image'].notna()].reset_index(drop=True)


def user_card(image, name, text, index):
    with st.container(border=True):
        container_cols = st.columns([1,4],vertical_alignment='center')
        st.write(text)
        container_cols[0].markdown(f'<img src="{image}" alt="photo" width="50" height="50" style="border-radius: 50%;">',
                    unsafe_allow_html=True)
        container_cols[1].markdown(f"#### {name}")
        if ui.button("Choose me!", key=f"button{index}", variant="outline", className="m-1"):
            return True
        else:
            return False



df = load_data()

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i%3]:
        if user_card( row['image'],
                      row['screen_name'], row['description'], i):

            st.session_state['selected_user'] = row['screen_name']
            st.session_state['selected_user_data'] = df[df['screen_name']==row['screen_name']].iloc[0]
            switch_page("chat")
#