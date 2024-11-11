import streamlit as st
import json
import random

def run():
    st.set_page_config(
        page_title="GPM Quiz App",
        page_icon="❓",
    )

if __name__ == "__main__":
    run()

# Custom CSS for the buttons
st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
</style>
""", unsafe_allow_html=True)

# Initialize session variables if they do not exist
default_values = {
    'shuffled_indices': None,
    'current_index': 0,
    'score': 0,
    'selected_option': None,
    'answer_submitted': False,
    'incorrect_indices': [],  # Track indices of incorrectly answered questions
    'retry_incorrect': False,  # Flag to indicate if we're retrying incorrect questions
    'shuffled_options': None,  # Track shuffled options for the current question
    'quiz_completed': False     # Flag to indicate if quiz is completed
}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

# Load quiz data
with open('content/quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

# Shuffle questions at the start of the quiz if not already done
if st.session_state.shuffled_indices is None:
    st.session_state.shuffled_indices = random.sample(range(len(quiz_data)), len(quiz_data))

def restart_quiz():
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.incorrect_indices = []
    st.session_state.retry_incorrect = False
    st.session_state.shuffled_indices = random.sample(range(len(quiz_data)), len(quiz_data))
    st.session_state.shuffled_options = None
    st.session_state.quiz_completed = False

def restart_incorrect():
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.shuffled_indices = st.session_state.incorrect_indices.copy()
    st.session_state.incorrect_indices = []
    st.session_state.retry_incorrect = True
    st.session_state.shuffled_options = None
    st.session_state.quiz_completed = False

def submit_answer():
    if st.session_state.selected_option is not None:
        st.session_state.answer_submitted = True
        correct_answer = quiz_data[st.session_state.shuffled_indices[st.session_state.current_index]]['answer']
        if st.session_state.selected_option == correct_answer:
            st.session_state.score += 10
        else:
            st.session_state.incorrect_indices.append(st.session_state.shuffled_indices[st.session_state.current_index])
        
        # If this is the last question, set quiz as completed
        if st.session_state.current_index == len(st.session_state.shuffled_indices) - 1:
            st.session_state.quiz_completed = True
    else:
        st.warning("Please select an option before submitting.")

def next_question():
    st.session_state.current_index += 1
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.shuffled_options = None  # Reset for the next question

# Title and description
st.title("GPM Quiz App")

# Progress bar
progress_bar_value = (st.session_state.current_index + 1) / len(st.session_state.shuffled_indices)
st.metric(label="Score", value=f"{st.session_state.score} / {len(st.session_state.shuffled_indices) * 10}")
st.progress(progress_bar_value)

# Check if quiz is completed
if st.session_state.quiz_completed:
    st.write(f"Quiz completed! Your score is: {st.session_state.score} / {len(st.session_state.shuffled_indices) * 10}")
    # Restart options: full quiz or only incorrect answers
    if len(st.session_state.incorrect_indices) > 0:
        st.button('Restart Wrong Answered Questions', on_click=restart_incorrect)
    else:
        st.info("Congratulations! All questions were answered correctly.")
    st.button('Restart Full Quiz', on_click=restart_quiz)
else:
    st.markdown(""" ___ """)
    # Display the question without additional information or underline
    current_question_index = st.session_state.shuffled_indices[st.session_state.current_index]
    question_item = quiz_data[current_question_index]
    st.subheader(f"Question {st.session_state.current_index + 1}")
    st.write(question_item['question'])
    st.markdown(""" ___ """)

    # Shuffle the options if they haven't been shuffled for this question
    if st.session_state.shuffled_options is None:
        options = question_item['options']
        st.session_state.shuffled_options = random.sample(options, len(options))

    # Answer selection and feedback
    options = st.session_state.shuffled_options
    correct_answer = question_item['answer']

    if st.session_state.answer_submitted:
        for option in options:
            if option == correct_answer:
                st.success(f"{option} (Correct answer)")
            elif option == st.session_state.selected_option:
                st.error(f"{option} (Incorrect answer)")
            else:
                st.write(option)
    else:
        st.session_state.selected_option = st.radio("Choose an answer:", options)

    # Submission button and response logic
    if st.session_state.answer_submitted:
        if st.session_state.current_index < len(st.session_state.shuffled_indices) - 1:
            st.button('Next', on_click=next_question)
        else:
            st.session_state.quiz_completed = True  # Mark quiz as completed on last question
    else:
        st.button('Submit', on_click=submit_answer)
