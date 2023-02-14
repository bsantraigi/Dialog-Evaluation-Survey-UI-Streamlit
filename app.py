import streamlit as st
import pandas as pd
import numpy as np

st.title('Dialog Evaluation Survey')

# Check if session contains prolific id, 
# If not ask the user for a prolific id,
# Else say Logged in and show the prolific id

if 'prolific_id' not in st.session_state:
    st.session_state.prolific_id = st.text_input('Please enter your Prolific ID')
    st.write('Logged in with Prolific ID: ', st.session_state.prolific_id)
else:
    st.write('Logged in with Prolific ID: ', st.session_state.prolific_id)

# Load survey_input.csv to dataframe
df_data = pd.read_csv('survey_input.csv')

# Create a directory to store the responses for each prolific id
os.makedirs('responses', exist_ok=True)
os.makedirs('responses/' + st.session_state.prolific_id, exist_ok=True)

# We will store the response from each streamlit session in a separate csv file
# Create a csv file with unique hash of length 8
hash = secrets.token_hex(4)
filename = 'responses/' + st.session_state.prolific_id + '/' + hash + '.csv'

# Make sure it doesn't already exists
while os.path.exists(filename):
    hash = secrets.token_hex(4)
    filename = 'responses/' + st.session_state.prolific_id + '/' + hash + '.csv'

# Create a dataframe to store the responses
df_response = pd.DataFrame(columns=['prolific_id', 'hash', 'question', 'response'])

# Read in all questions from users previous sessions, if any
import glob
for file in glob.glob('responses/' + st.session_state.prolific_id + '/*.csv'):
    df_response = df_response.append(pd.read_csv(file))

# Randomly pick total of 10 questions for each user
# If the user has already answered a question, don't pick it again
df_data = df_data[~df_data['question'].isin(df_response['question'])]
# If the user has already answered 10 questions, don't pick any more
if len(df_response) < 10:
    df_data = df_data.sample(n=10-len(df_response), random_state=1)

# On streamlit right side, show a progress bar
st.sidebar.markdown('**Progress**')
progress = len(df_response) / 10
st.sidebar.progress(progress)

# For each question, ask the user to rate it on a scale of 1 to 5
# We will show one question at a time, 
# and once the user has rated it, we will show the next question
# update the df_response dataframe
for index, row in df_data.iterrows():
    st.write(row['question'])
    response = st.slider('Rate this question', 1, 5, 3)
    df_response = df_response.append({'prolific_id': st.session_state.prolific_id, 'hash': hash, 'question': row['question'], 'response': response}, ignore_index=True)

