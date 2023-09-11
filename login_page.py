import streamlit as st
from sentence_transformers import SentenceTransformer, util
import openai
import re
import pandas as pd


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
                    answer=ask_csv(df, 'Show me the comparison of total claims for each ICD10code using graph', True)
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


class generate_code():

  api_key=''
  #api_key=''
  openai.api_key=api_key

  def __init__(self,df):
    self.df=df
    self.num_rows=len(df)
    self.num_columns=len(df.columns)
    self.data_types=df.dtypes

  def query(self,payload):
    response=openai.Completion.create(
      engine="text-davinci-002",
      prompt=payload["inputs"],
      temperature=payload["temperature"],
      max_tokens=payload["max_new_tokens"])

    return response['choices'][0]['text'].strip()


  def prompt_generation(self,question):
    columns=self.df.columns
    col_list=','.join(columns)
    prompt=f'''Write a python code on pandas dataframe df with columns:{col_list}.
    The pandas dataframe already exists with the following schema:
    {self.df.dtypes}
    The code assumes the dataframe df while the below code.
    The code should be able to display results for the following user query:
    {question}
    The code should also print the final results using the print statement
    'Do not add comments in the code'
    The code must be executed when passed to exec function
    'Always assume that dataframe df already exists'
    'The code should import the necessary modules'
    'Try to avoid using loops while writing the code if possible'
'''
    return prompt

  @staticmethod
  def clean_code(code):
    read_patt=re.compile(r'pd\.read\_csv\([A-Za-z0-9]*\.csv\)')
    code=re.sub(read_patt,'',code)
    matplotlib_patt=re.compile(r"\%matplotlib inline")
    code=re.sub(matplotlib_patt,'',code)
    return code


  def generate(self,
            original_prompt, temperature=0.9, max_new_tokens=256, top_p=0.95, repetition_penalty=1.0
        ):

            prompt=original_prompt
            generate_kwargs = {
                "temperature":temperature,
                "max_new_tokens":max_new_tokens,
                "top_p":top_p,
                "repetition_penalty":repetition_penalty,
                "do_sample":True,
                "seed":42
            }

            suffix=''

            prompt_dict={"inputs":prompt,**generate_kwargs}
            code_response=self.query(prompt_dict)
            #for i in range(5):
            prompt_dict={"inputs":prompt,**generate_kwargs}
            code_response=self.query(prompt_dict)
            prompt=code_response

            match = re.search(
              "(```python)(.*)(```)",
               prompt.replace(prompt+suffix, ""),
                re.DOTALL | re.MULTILINE,
                            )
            # if match:
            #   break


            final_code=prompt.replace(original_prompt+suffix, "")
            #final_code=final_code.split("\'''")
            #final_code=final_code.split("You can use the below code to get the answer:")

            return final_code

def ask_csv(df,questions,show_code=False):
  code_generator=generate_code(df)
  prompt=code_generator.prompt_generation(question=questions)
  code=code_generator.generate(prompt)
  code=code_generator.clean_code(code)
  if show_code:
      print(code)
  else:
      pass
  for statements in code.split('\n'):
    exec(statements)


if __name__ == "__main__":
    main()
