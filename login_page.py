import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Define a function to filter out columns with PHI data
def filter_phi_columns(columns):
    # Replace this logic with your own criteria for identifying PHI columns.
    # For example, you can check for column names that suggest PHI data.

    safe_harbor_list = ['Names', 'Geography','location','street address', 'city', 'county', 'zip code', 'Dates', 'birthdate', 'admission date',
                        'discharge date', 'date of death', 'Telephone ', 'Fax numbers', 'Email addresses',
                        'Social Security ','SSN', 'Medical record ', 'Health plan beneficiary',
                        'Account', 'Certificate license ', 'Vehicle identifiers',
                        'serial' 'license plate ', 'Device identifiers', 'Web URLs', 'IP addresses',
                        'Biometric identifiers', 'fingerprints and voice', 'Full face photos',
                        'unique identifying ', 'codes']
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    phi_list = set()
    for col in columns:
        for pii_col in safe_harbor_list:
            embedding_1 = model.encode(col, convert_to_tensor=True)
            embedding_2 = model.encode(pii_col, convert_to_tensor=True)
            compare_value = util.pytorch_cos_sim(embedding_1, embedding_2).numpy()[0][0]
            if compare_value > 0.45:
                phi_list.add(col)
                print(col, pii_col,compare_value)
    phi_list = list(phi_list)
    if len(phi_list)>0:
        return phi_list,True
    else:
        return [],False

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
            

            filter_condition=filter_phi_columns(list(df.columns))
            if filter_condition[1]:
                list_data=",".join(filter_condition[0])
                st.error("Datset uploaded contain PHI columns - "+list_data)
            else:
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
