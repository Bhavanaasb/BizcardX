

# Import the required libraries and modules
# Streamlit is an open-source app framework used to create and share interactive web apps for data analysis, machine learning, and more.
import streamlit as st 
# This module allows the creation of stylish and interactive sidebar or navigation menus in Streamlit apps.
from streamlit_option_menu import option_menu
# EasyOCR is a Python-based Optical Character Recognition (OCR) library that supports multiple languages for extracting text from images.
import easyocr
# The Python Imaging Library (PIL) provides image processing capabilities. It is used here for loading, displaying, and manipulating image files.
from PIL import Image
# Pandas is a powerful data manipulation library for Python. It is used for handling tabular data in the form of data frames.
import pandas as pd
# NumPy is a library for numerical computations. It is used here to handle arrays, particularly for image processing tasks.
import numpy as np
# Regular Expressions (re) is a module for string searching and manipulation. It is used here to identify patterns in the extracted text.
import re
# The io module provides tools for working with input and output streams, such as converting images into byte streams for database storage.
import io
# sqlite3 is a lightweight database library for managing relational databases. It is used here to store and retrieve extracted business card information.
import sqlite3


# This function extracts text from an image file using EasyOCR and also returns the original image.
def image_to_text(path):
  # Open the image file from the provided path using PIL's Image module.
  input_img= Image.open(path)


  #converting image to array format
  # Convert the image into a NumPy array for processing. 
  # EasyOCR works with image arrays, so this step prepares the image for OCR processing.

  image_arr= np.array(input_img)
  # Initialize the EasyOCR reader, specifying English ('en') as the target language for text recognition.
  reader= easyocr.Reader(['en'])
  # Use EasyOCR's `readtext` method to extract text from the image array.
  # The `detail=0` parameter ensures that only the text is returned (no bounding box or confidence scores).
  text= reader.readtext(image_arr, detail= 0)
  
  # Return the extracted text (a list of strings) and the original image object for further use.
  return text, input_img
  


def extracted_text(texts):
# This function processes a list of extracted text strings from a business card image
# and categorizes them into predefined fields such as name, designation, contact, etc.

# Initialize a dictionary with keys representing the fields of interest
# Each key corresponds to a category for the extracted data, starting with empty lists.
  extrd_dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
                "ADDRESS":[], "PINCODE":[]}
  # Assume the first element of `texts` is the name
  extrd_dict["NAME"].append(texts[0])
  # Assume the second element of `texts` is the designation
  extrd_dict["DESIGNATION"].append(texts[1])
  # Iterate through the remaining text elements to classify them
  for i in range(2,len(texts)):
    # Check if the text resembles a phone number
    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):

      extrd_dict["CONTACT"].append(texts[i])
    # Check if the text resembles an email address
    elif "@" in texts[i] and ".com" in texts[i]:
      extrd_dict["EMAIL"].append(texts[i])
    # Check if the text resembles a website URL (case-insensitive)
    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small= texts[i].lower()   # Convert to lowercase for consistency
      extrd_dict["WEBSITE"].append(small)
    # Check if the text matches patterns for pincode or location (e.g., "Tamil Nadu")
    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extrd_dict["PINCODE"].append(texts[i])
    # Check if the text starts with alphabetic characters (likely a company name)
    elif re.match(r'^[A-Za-z]', texts[i]):
      extrd_dict["COMPANY_NAME"].append(texts[i])
    # Any other text is treated as part of the address
    else:
      remove_colon= re.sub(r'[,;]','',texts[i])   # Remove unnecessary punctuation
      extrd_dict["ADDRESS"].append(remove_colon)
  # Post-process the dictionary to concatenate values and handle missing data
  for key,value in extrd_dict.items():
    if len(value)>0:
      # Join the list of strings for each category into a single string
      concadenate= " ".join(value)
      extrd_dict[key] = [concadenate]

    else:
      # If no values are found for a key, assign "NA"
      value = "NA"
      extrd_dict[key] = [value]
  # Return the dictionary containing the categorized and processed data.
  return extrd_dict


#Streamlit part
# Set the Streamlit app layout to "wide" for better utilization of horizontal screen space.
st.set_page_config(layout = "wide")
# Set the main title of the application displayed at the top of the page.
st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")
# Define a sidebar where users can interact with the app's navigation menu.
with st.sidebar:
  # Create an option menu in the sidebar with three options: "Home," "Upload & Modifying," and "Delete."
  # The selected option is stored in the variable `select`.
  select= option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])

# Display content based on the selected menu option
# If "Home" is selected, display informational content about the app.
if select == "Home":
  # Highlight the technologies used in building the app.
  st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
  

  # Provide a brief description of the app.
  st.write(
            "### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
  # Explain the purpose and functionality of the app.
  st.write(
            '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

# If "Upload & Modifying" is selected, provide functionality for uploading and processing images.
elif select == "Upload & Modifying":
  # Allow the user to upload an image file with specified file types.
  img = st.file_uploader("Upload the Image", type= ["png","jpg","jpeg"])
  # Check if an image has been uploaded.
  if img is not None:
    # Display the uploaded image in the app with a width of 300 pixels.
    st.image(img, width= 300)
    # Call the `image_to_text` function to extract text from the image and get the original image.
    text_image, input_img= image_to_text(img)
    # Call the `extracted_text` function to process the extracted text into structured data.
    text_dict = extracted_text(text_image)

    if text_dict:
      # If text was successfully extracted and processed, show a success message.
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    # Convert the structured text data (dictionary) into a DataFrame for better representation.
    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    # Converting Image to Bytes
    # Create a BytesIO object to hold binary data for the image.
    Image_bytes = io.BytesIO()
    # Save the image in PNG format to the BytesIO object.
    input_img.save(Image_bytes, format= "PNG")
    # Retrieve the binary data of the image from the BytesIO object.
    image_data = Image_bytes.getvalue()

    #Creating Dictionary
    # Create a dictionary with the binary image data.
    data = {"IMAGE":[image_data]}
    # Convert the dictionary to a DataFrame for merging with text data.
    df_1 = pd.DataFrame(data)
    # Concatenate the text data and image data DataFrames along the columns.
    concat_df = pd.concat([df,df_1],axis= 1)
    # Display the final concatenated DataFrame in the app.
    st.dataframe(concat_df)
    # Create a "Save" button for the user to save the extracted data.
    button_1 = st.button("Save", use_container_width = True)
    # If the "Save" button is clicked, proceed to save the data into a database.
    if button_1:
      # Connect to a SQLite database named "bizcardx.db". If it doesn't exist, it will be created.
      mydb = sqlite3.connect("bizcardx.db")
      # Create a cursor object to execute SQL queries.
      cursor = mydb.cursor()

      #Table Creation
      # SQL query to create a table named `bizcard_details` if it doesn't already exist.
      # This table stores fields extracted from business cards (name, designation, etc.).
      #  'image' stores the binary data of the business card image.
      create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                          designation varchar(225),
                                                                          company_name varchar(225),
                                                                          contact varchar(225),
                                                                          email varchar(225),
                                                                          website text,
                                                                          address text,
                                                                          pincode varchar(225),
                                                                          image text)'''
      # Execute the table creation query.
      cursor.execute(create_table_query)
      # Commit the changes to save the table structure in the database.
      mydb.commit()

      # Insert Query
      # SQL query to insert data into the `bizcard_details` table.
      # Uses placeholders (?) for parameterized query to prevent SQL injection.
      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,contact, email, website, address,
                                                    pincode, image)

                                                    values(?,?,?,?,?,?,?,?,?)'''
      # Convert the first row of the concatenated DataFrame (`concat_df`) to a list.
      # This list represents a single record with fields in the same order as the table columns.
      datas = concat_df.values.tolist()[0]
      # Execute the insert query with the extracted data.
      cursor.execute(insert_query,datas)
      # Commit the transaction to save the inserted data into the database.
      mydb.commit()
      # Display a success message to indicate the data has been saved.
      st.success("SAVED SUCCESSFULLY")
  # Method Selection# Provide a radio button widget to select a method: None, Preview, or Modify.
  # The selected method is stored in the variable `method`.
  method =  st.radio("Select the Method",["None","Preview","Modify"])
  # If "None" is selected, do nothing.
  if method == "None":
    st.write("")  
  # If "Preview" is selected, display all records in the database.
  if method == "Preview":
    # Connect to the SQLite database.
    mydb = sqlite3.connect("bizcardx.db")
    # Create a cursor object to execute SQL queries.
    cursor = mydb.cursor()

    #select query
    # SQL query to fetch all records from the `bizcard_details` table.
    select_query = "SELECT * FROM bizcard_details"
    # Execute the select query.
    cursor.execute(select_query)
    # Fetch all rows from the result of the executed query.
    table = cursor.fetchall()
    # Commit the transaction (not strictly needed for read-only operations).
    mydb.commit()
    # Convert the fetched data into a DataFrame with column names corresponding to the table structure.
    table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                            "ADDRESS", "PINCODE", "IMAGE"))
    # Display the DataFrame in the app as an interactive table.
    st.dataframe(table_df)
  # If "Modify" is selected, allow users to update records in the database.
  elif method == "Modify":
    # Connect to the SQLite database.
    mydb = sqlite3.connect("bizcardx.db")
    # Create a cursor object to execute SQL queries.
    cursor = mydb.cursor()

    #select query
    # Select Query to fetch all records
    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)  # Execute the query
    table = cursor.fetchall() # Fetch all records
    mydb.commit()  # Commit the transaction
    # Convert the records into a DataFrame with appropriate column names
    table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                            "ADDRESS", "PINCODE", "IMAGE"))
    # Create two columns for layout
    col1,col2 = st.columns(2)
    with col1:
      # Dropdown to select a name from the fetched records
      selected_name = st.selectbox("Select the name", table_df["NAME"])
    # Filter the DataFrame to show only the selected name's record
    df_3 = table_df[table_df["NAME"] == selected_name]
    # Create a copy of the selected record for modification
    df_4 = df_3.copy() 
    # Create text input fields to modify individual attributes
    col1,col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("Name", df_3["NAME"].unique()[0])
      mo_desi = st.text_input("Designation", df_3["DESIGNATION"].unique()[0])
      mo_com_name = st.text_input("Company_name", df_3["COMPANY_NAME"].unique()[0])
      mo_contact = st.text_input("Contact", df_3["CONTACT"].unique()[0])
      mo_email = st.text_input("Email", df_3["EMAIL"].unique()[0])
      # Update the modified data in the copy of the DataFrame
      df_4["NAME"] = mo_name
      df_4["DESIGNATION"] = mo_desi
      df_4["COMPANY_NAME"] = mo_com_name
      df_4["CONTACT"] = mo_contact
      df_4["EMAIL"] = mo_email

    with col2:
      
      mo_website = st.text_input("Website", df_3["WEBSITE"].unique()[0])
      mo_addre = st.text_input("Address", df_3["ADDRESS"].unique()[0])
      mo_pincode = st.text_input("Pincode", df_3["PINCODE"].unique()[0])
      mo_image = st.text_input("Image", df_3["IMAGE"].unique()[0])
      # Update the rest of the fields
      df_4["WEBSITE"] = mo_website
      df_4["ADDRESS"] = mo_addre
      df_4["PINCODE"] = mo_pincode
      df_4["IMAGE"] = mo_image
    # Display the modified DataFrame
    st.dataframe(df_4)
    # Create a button to confirm modifications
    col1,col2= st.columns(2)
    with col1:
      button_3 = st.button("Modify", use_container_width = True)

    if button_3:
      # Reconnect to the database for the modification
      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()
      # Delete the old record
      cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
      mydb.commit()

      # Insert Query
      # Insert the modified record into the table
      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,contact, email, website, address,
                                                    pincode, image)

                                                    values(?,?,?,?,?,?,?,?,?)'''

      datas = df_4.values.tolist()[0]     # Extract the modified data as a list
      cursor.execute(insert_query,datas)  # Insert the modified record
      mydb.commit()   # Commit the transaction

      st.success("MODIFYED SUCCESSFULLY") # Show success message


# If the selected operation is "Delete"
elif select == "Delete":
  # Connect to the database
  # Step 1: Connect to the SQLite database
  # Connects to the SQLite database file named 'bizcardx.db'.
  mydb = sqlite3.connect("bizcardx.db") 
  cursor = mydb.cursor()  # Creates a cursor object to execute SQL queries.
  # Step 2: Create a two-column layout for the UI
  # Using Streamlit's layout feature to create two columns, col1 and col2.
  col1,col2 = st.columns(2)
  # Step 3: Fetch all names from the database and populate the first column
  with col1:
    # SQL query to fetch all names from the 'bizcard_details' table.
    select_query = "SELECT NAME FROM bizcard_details"
    # Execute the query to retrieve all names.
    cursor.execute(select_query)
    # Fetch all the results from the query execution.
    table1 = cursor.fetchall()
    # Commit the transaction to ensure data integrity.
    mydb.commit()
    # Initialize an empty list to store the names.
    names = []
    # Iterate through the query results and add names to the list.
    for i in table1:
      names.append(i[0])
    # Streamlit selectbox to allow the user to choose a name from the list.
    name_select = st.selectbox("Select the name", names)
  # Step 4: Fetch designations based on the selected name and populate the second column
  with col2:
    # SQL query to fetch the designation(s) corresponding to the selected name.
    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'"
    # Execute the query to retrieve designations for the selected name.
    cursor.execute(select_query)  # Execute the query to retrieve designations for the selected name.
    table2 = cursor.fetchall()    # Fetch all the results from the query execution.
    mydb.commit()                 # Commit the transaction.
    designations = []             # Initialize an empty list to store the designations.
    # Iterate through the query results and add designations to the list.
    for j in table2:
      designations.append(j[0])
    # Streamlit selectbox to allow the user to choose a designation from the list.
    designation_select = st.selectbox("Select the designation", options = designations)
  # Step 5: Display selected name and designation, and provide a delete button
  if name_select and designation_select:
    # Create a three-column layout to structure the display and button.
    col1,col2,col3 = st.columns(3)
    # Column 1: Display the selected name and designation.
    with col1:
      st.write(f"Selected Name : {name_select}")    # Show the selected name.
      st.write("")    # Blank space for better UI spacing.
      st.write("")    # Blank space for better UI spacing.
      st.write("")    # Blank space for better UI spacing.
      st.write(f"Selected Designation : {designation_select}")     # Show the selected designation.
    # Column 2: Display the delete button.
    with col2:
      st.write("")    # Blank space for alignment purposes.
      st.write("")    # Blank space for alignment purposes.
      st.write("")    # Blank space for alignment purposes.
      st.write("")    # Blank space for alignment purposes.
      # Button for deleting the selected record.
      # `use_container_width=True` ensures the button takes up the full column width.
      remove = st.button("Delete", use_container_width= True)
      # If the delete button is clicked:
      if remove:
        # SQL query to delete the record where the selected name and designation match.
        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        # Commit the transaction to save the changes.
        mydb.commit()
        # Show a warning message to inform the user that the record was deleted.
        st.warning("DELETED")

