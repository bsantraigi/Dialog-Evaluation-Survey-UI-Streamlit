import streamlit as st
import pandas as pd
import numpy as np
import os
import uuid

st.title('Dialog Evaluation Survey')

# Check if session contains prolific id, 
# If not ask the user for a prolific id,
# Else say Logged in and show the prolific id

st.sidebar.title('Login')
if 'prolific_id' not in st.session_state:
    st.session_state.prolific_id = st.sidebar.text_input('Please enter your Prolific ID')
    st.sidebar.write('Logged in with Prolific ID: ', st.session_state.prolific_id)
else:
    st.sidebar.write('Logged in with Prolific ID: ', st.session_state.prolific_id)

# Load survey_input.csv to dataframe
df_data = pd.read_csv('survey_input.csv')
# df_data

# exit()
# Create a directory to store the responses for each prolific id
os.makedirs('responses', exist_ok=True)
os.makedirs('responses/' + st.session_state.prolific_id, exist_ok=True)

# We will store the response from each streamlit session in a separate csv file
# Create a csv file with unique hash of length 8
# Make sure it doesn't already exists
def generate_hash():
    UNIQ_ID = str(uuid.uuid4())[:8].upper()
    return UNIQ_ID

if 'hash' not in st.session_state:
    hash = generate_hash()
    filename = 'responses/' + st.session_state.prolific_id + '/' + hash + '.csv'
    while os.path.exists(filename):
        hash = generate_hash()
        filename = 'responses/' + st.session_state.prolific_id + '/' + hash + '.csv'
    st.session_state.hash = hash
    st.session_state.filename = filename

# get the hash from session
hash = st.session_state.hash
filename = st.session_state.filename

# Create a dataframe to store the responses
df_response = pd.DataFrame(columns=['prolific_id', 'hash', 'con', 'response'])

# Read in all questions from users previous sessions, if any
import glob
for file in glob.glob('responses/' + st.session_state.prolific_id + '/*.csv'):
    df_response = df_response.append(pd.read_csv(file))

# Randomly pick total of 10 questions for each user
# If the user has already answered a question, don't pick it again
df_data = df_data[~df_data['con'].isin(df_response['con'])]
# If the user has already answered 10 questions, don't pick any more
if len(df_response) < 10:
    df_data = df_data.sample(n=10-len(df_response), random_state=1)

# On streamlit right side, show a progress bar
st.markdown('**Progress**')
st.write("You have answered", len(df_response), "out of 10 questions")
progress = len(df_response) / 10
st.progress(progress)

# If the user has already answered 10 questions, show a message and exit
if len(df_response) == 10:
    st.write('You have already answered 10 questions. Thank you for your time!')
    st.stop()

# For each question, ask the user to rate it on a scale of 1 to 5
# We will show one question at a time, 
# and once the user has rated it, we will show the next question
# update the df_response dataframe

# Select the next unanswered question
row = df_data.iloc[0]
st.markdown('**Read the following context:**')
st.markdown(row['con'])
st.markdown('**Rate the response:**')
st.markdown(row['response_A_raw'])
# Ask the user to rate the response
rating = st.slider('Rating', 1, 5, 3)
# Add the response to the df_response dataframe
df_response = df_response.append({'prolific_id': st.session_state.prolific_id, 'hash': hash, 'con': row['con'], 'response_A_raw': row['response_A_raw'], 'rating': rating}, ignore_index=True)
# Save the response to a csv file
df_response.to_csv(filename, index=False)

