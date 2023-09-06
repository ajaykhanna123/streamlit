import streamlit as st
import pandas as pd

# Define a function to simulate user authentication
def authenticate(username, password):
    # You can implement your own authentication logic here.
    # For simplicity, we'll use hardcoded credentials.
    valid_username = "user"
    valid_password = "password"
    
    if username == valid_username and password == valid_password:
        return True
    else:
        return False

# Streamlit app
def main():
    st.set_page_config(layout="wide")
    st.title("Login Page")

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Display login section
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.write("Welcome, " + username + "!")
        else:
            
            st.error("Login failed. Please try again.")

    # Check if the user is logged in before displaying upload and text boxes
    if st.session_state.logged_in:
        # Display file upload section below login
        st.subheader("Upload CSV or Excel File")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file is not None:
            # Read and display the uploaded file
            file_extension = uploaded_file.name.split(".")[-1]
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            st.write("Uploaded Data:")
            st.write(df)

            # Add text boxes for question and output
            question = st.text_input("Question", placeholder="Enter your question here")
            if st.button("Submit"):
                # Here, you can process the question and provide an output based on the data in the CSV
                # For demonstration purposes, we'll simply display the question.
                st.write("Question:", question)

    # Display information about what the tool can and cannot do on the right side
    st.sidebar.title("Tool Information")
    st.sidebar.markdown("### What This Tool Can Do:")
    st.sidebar.write("- Upload CSV or Excel files.")
    st.sidebar.write("- Enter questions and get answers based on the data.")

    st.sidebar.markdown("### What This Tool Cannot Do:")
    st.sidebar.write("- Handle complex data processing.")
    st.sidebar.write("- Advanced natural language processing.")
    st.sidebar.write("- Real-time updates or database connections.")

if __name__ == "__main__":
    main()
