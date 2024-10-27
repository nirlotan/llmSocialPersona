import streamlit as st
import streamlit_antd_components as sac
from faker import Faker
import random

from streamlit_javascript import st_javascript
from user_agents import parse
import toml

# get icons from https://icons.getbootstrap.com/

@st.cache_data
def get_interest_list():
    interests = ['Yoga', 'Music', 'Art', 'Sports', 'History', 'Science', 'Cooking',
             'Politics', 'Reading', 'Travelling', 'Hiking', 'Writing', 'Coding', 'Dance', 'Nature', 'Fitness',
             'Health', 'Drawing', 'Gardening', 'Photography', 'Meditation', 'Animals', 'Fashion', 'Beauty', 'Teaching',
             'Movies', 'Languages', 'Fishing', 'Crafts', 'Math', 'Cars', 'Hiking']

    random.shuffle(interests)
    return interests



config = toml.load("config.toml")
max_interests = config['max_interests_pc']

try:
    # check user agent to suppress non-mandatory parts when running on mobile
    ua_string = st_javascript("""window.navigator.userAgent;""")
    user_agent = parse(ua_string)
    st.session_state.is_session_pc = user_agent.is_pc
    if user_agent.is_pc:
        max_interests = config['max_interests_pc']
    else:
        max_interests = config['max_interests_mobile']

except:
    max_interests = config['max_interests_mobile']
    st.session_state.is_session_pc = True


wizard_step1 = sac.steps(
    items=[
        sac.StepsItem(title='Profiling'),
        sac.StepsItem(title='Chat'),
        sac.StepsItem(title='Feedback', disabled=True),
    ],
)

st.markdown("#### Define your user profile:")

sac.divider(label='Personal Attributes', icon='file-earmark-person', align='center', color='gray')
gender = sac.buttons([
sac.ButtonsItem(label='Gender:', disabled=True, color='#25C3B0'),
    sac.ButtonsItem(label='Male', icon='gender-male', color='#25C3B0'),
    sac.ButtonsItem(label='Female',  icon='gender-female',color='#25C3B0'),
    sac.ButtonsItem(label='Other', icon='gender-neuter', color='#25C3B0'),
    sac.ButtonsItem(label='Prefer not to disclose', icon='gender-ambiguous',color='#25C3B0'),
], label="", description='', align='center', index=-1)

age = sac.buttons([
    sac.ButtonsItem(label='Age group:', disabled=True, color='#25C3B0'),
    sac.ButtonsItem(label='18-24',  color='#25C3B0'),
    sac.ButtonsItem(label='25-32',color='#25C3B0'),
    sac.ButtonsItem(label='33-44', color='#25C3B0'),
    sac.ButtonsItem(label='45-55',color='#25C3B0'),
    sac.ButtonsItem(label='55-120', color='#25C3B0'),
], label="", align='center', index=-1)

sac.divider(label='Areas of interests', icon='controller', align='center', color='gray')

interests = get_interest_list()

def split_list_into_sublists(input_list, max_size):
    return [input_list[i:i + max_size] for i in range(0, len(input_list), max_size)]

list_of_lists = split_list_into_sublists(interests, max_interests)
user_interests = []
for list in list_of_lists:
    user_interests += sac.chip(
        items=list, index=[], align='center', radius='md', multiple=True
    )

if 'Sports' in user_interests:
    user_interests += sac.chip(items=['Football','Basketball','Soccer','Cricket'],
         index=[], align='center', radius='md', multiple=True
    )

if 'Music' in user_interests:
    user_interests += sac.chip(items=['R&B','Hip-Hop','Jazz','Rock',
                                      'Pop','Alternative music','Classical Music'],
         index=[], align='center', radius='md', multiple=True
    )

sac.divider(label='More Info', icon='people-fill', align='center', color='gray')

marital_status = sac.buttons([
    sac.ButtonsItem(label='Marital status:', disabled=True, color='#D4BEE4'),
    sac.ButtonsItem(label='single',  color='#D4BEE4'),
    sac.ButtonsItem(label='married',color='#D4BEE4'),
    sac.ButtonsItem(label='divorced/seperated', color='#D4BEE4'),
    sac.ButtonsItem(label='widowed',color='#D4BEE4'),
    sac.ButtonsItem(label='other', color='#D4BEE4'),
], label="", description='', align='center', index=-1)


children = sac.buttons([
    sac.ButtonsItem(label='I have children:', disabled=True, color='#D4BEE4'),
    sac.ButtonsItem(label='Yes',  color='#D4BEE4'),
    sac.ButtonsItem(label='No',color='#D4BEE4'),
    sac.ButtonsItem(label='I have grand children', color='#D4BEE4'),
    sac.ButtonsItem(label='I don\'t want children',color='#D4BEE4'),
    sac.ButtonsItem(label='other', color='#D4BEE4'),
], label="", description='', align='center', index=-1)

politics = sac.buttons([
    sac.ButtonsItem(label='I consider myself:', disabled=True, color='#D4BEE4'),
    sac.ButtonsItem(label='Republican',  color='#D4BEE4'),
    sac.ButtonsItem(label='Democrat',color='#D4BEE4'),
    sac.ButtonsItem(label='unaffiliated', color='#D4BEE4'),
], label="", description='', align='center', index=-1)


fake = Faker()


if gender == "Male":
    name = fake.first_name_male()
elif gender == "Female":
    name = fake.first_name_female()
else:
    name = fake.first_name()
lname = fake.last_name()

user_description = f"Your name is: {name} {lname}. "
age_description = ""


if age != None:
    age_description = f"{age} years old"
if gender != None and gender != "Prefer not to disclose" and gender != "Other":
    user_description += f"You are a {age_description} {gender}"
elif age != None:
    user_description += f"You are {age_description}"

if age != None or gender != None:
    user_description += ". "

if marital_status not in [None, 'other']:
    user_description += f"You are {marital_status}. "

def check_children(children):
    if children == 'Yes':
        return "You have children."
    elif children == 'No':
        return "You don't have children. "
    elif children == 'I have grand children':
        return "You have grand children."
    elif children == "I don\'t want children":
        return "You don\'t have and don\'t want to have children."
    else:
        return ""

user_description += check_children(children)

if politics != None:
    user_description += f"You identify as {politics}. "

if len(user_interests) > 0:
   user_description += f"Your interests includes: {', '.join(user_interests)}. "

st.session_state['user_description'] = user_description

next_button = st.button("Go to chat")

wizard_step2 = sac.steps(
    items=[
        sac.StepsItem(title='Profiling'),
        sac.StepsItem(title='Chat'),
        sac.StepsItem(title='Feedback', disabled=True),
    ], key="wiz2"
)


if next_button or wizard_step2 == "Chat" or wizard_step1 == "Chat":
    st.session_state['reset_coversation'] = True
    st.switch_page('app_pages/slim_chat.py')

