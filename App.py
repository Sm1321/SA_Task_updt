import streamlit as st
import mysql.connector
import pandas as pd
from PIL import Image



#-----------------------------------------------------------------------------------------------------------
# Add this at the beginning of your script, right after importing libraries
def set_blue_background():
    st.markdown("""
    <style>
    .stApp {
        color: #010E0A;  /* Text color */
    }
    .center-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;  /* Centering vertically */
    }
    </style>
    """, unsafe_allow_html=True)

# Call this function before creating your Streamlit UI elements
set_blue_background()



#-----------------------------------------------------------------------------------------------------------
#For Diplay the Logo
def display_logo(image_path=None):
    """Display logo in the center. Accepts an image path or file uploader, adjusts width to 100px."""
    if image_path:
        try:
            img = Image.open(image_path)
            img = img.resize((200, int(200 * img.height / img.width)))
            st.image(img, use_column_width=False)
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        uploaded_file = st.file_uploader("Choose a logo image", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            img = img.resize((200, int(200 * img.height / img.width)))
            st.image(img, caption="Uploaded Logo", use_column_width=False)

# Example of using the function
display_logo(image_path="SA_Logo.jpg")  #image logo path



#-----------------------------------------------------------------------------------------------------------
# Step 1: Database Connection
@st.cache_resource
def get_database_connection():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="Temporary_Employee_Tracker"
        
    )
    return connection

# Step 2: Fetch Data with Column Names
def fetch_employee_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee_list")
    rows = cursor.fetchall()
    columns = ["Name", "Position", "Skills", "CurrentStatus"]
    df = pd.DataFrame(rows, columns = columns)
    cursor.close()
    return df

def fetch_main_table_data():
    # Establish database connection
    connection = get_database_connection()
    cursor = connection.cursor()

    # Execute the query to fetch the required data from the main_table
    cursor.execute("SELECT WeekEnd_Date, Employee, Project, Time_in_hours FROM main_table")
    rows = cursor.fetchall()
    columns = ["WeekEnd_Date", "Employee", "Project", "Time_in_hours"]

    # Create a DataFrame from the fetched rows and columns
    df = pd.DataFrame(rows, columns=columns)

    # Convert 'WeekEnd_Date' to datetime format
    df['WeekEnd_Date'] = pd.to_datetime(df['WeekEnd_Date'])

    # Extract the year from 'WeekEnd_Date' and ensure it's an integer
    df['Year'] = df['WeekEnd_Date'].dt.year

    #st.write(df.dtypes)
    # If the extracted year has any unwanted formatting like commas, clean it
    df['Year'] = df['Year'].astype(str).str.replace(",", "") #convert the Year into Str only
  
    df['WeekNumber(In that Year)'] = df['WeekEnd_Date'].dt.isocalendar().week

    # Retain only the date (not time) part of 'WeekEnd_Date'
    df['WeekEnd_Date'] = df['WeekEnd_Date'].dt.date

    # Close the cursor to free up resources
    cursor.close()

    # Return the DataFrame with extracted features
    return df




def fetch_project_list_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Project_List")
    rows = cursor.fetchall()
    columns = ["Project", "Description", "StartDate", "Expected_to_Complete", "Internal_or_External", "Status"]
    df = pd.DataFrame(rows, columns = columns)
    cursor.close()
    return df


#-----------------------------------------------------------------------------------------------------------
# Step 3: Insert New Employee
def add_new_employee(name, position, skills, current_status):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO employee_list (Name, Position, Skills, CurrentStatus) 
    VALUES (%s, %s, %s, %s)
    """, (name, position, skills, current_status))
    connection.commit()
    cursor.close()

# Step 4: Insert New Project
def add_new_project(project, description, start_date, expected_completion, internal_or_external, status):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO Project_List (Project, Description, StartDate, Expected_to_Complete, Internal_or_External, Status) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (project, description, start_date, expected_completion, internal_or_external, status))
    connection.commit()
    cursor.close()

# Step 5: Insert Employee Work Details
def add_employee_work_details(StartDate, employee, project, time_in_hours):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO main_table (StartDate, Employee, Project, Time_in_hours) 
    VALUES (%s, %s, %s, %s)
    """, (StartDate, employee, project, time_in_hours))
    connection.commit()
    cursor.close()



#-----------------------------------------------------------------------------------------------------------
# Step 6: Streamlit App Layout with Sidebar
st.sidebar.title("Choose your Task here")
option = st.sidebar.selectbox("Choose a section", ["Dashboard", "Add New Employee", "Add New Project", "Employee Weekly Tracker", "Utilization Analysis"])

# Dashboard - Display DataFrames
if option == "Dashboard":
    st.title("🏢Employee Tracker Dashboard")
    st.header("👨Employee List")
    employee_data = fetch_employee_data()
    #####print(employee_data)
    st.dataframe(employee_data, use_container_width=True)

    st.header("🕵️Main Table")
    main_table_data = fetch_main_table_data()
    st.dataframe(main_table_data, use_container_width=True)

    st.header("💻Project List")
    project_list_data = fetch_project_list_data()
    st.dataframe(project_list_data, use_container_width=True)

# Add New Employee Details
elif option == "Add New Employee":
    st.title("👨Add New Employee")
    with st.form(key='add_employee_form'):
        name = st.text_input("Name")
        position = st.text_input("Position")
        skills = st.text_input("Skills")
        current_status = st.selectbox("Current Status", ['Active', 'Inactive'])

        submit_employee = st.form_submit_button("Add Employee")
        if submit_employee:
            if name and position and skills and current_status:
                add_new_employee(name, position, skills, current_status)
                st.success("Employee added successfully!")
            else:
                st.error("Please fill all fields.")

# Add New Project Details
elif option == "Add New Project":
    st.title("💻Add New Project")
    with st.form(key='add_project_form'):
        project_name = st.text_input("Project Name")
        description = st.text_input("Description")
        start_date = st.date_input("Start Date")
        expected_completion = st.number_input("Expected Completion (Weeks)", min_value=1)
        internal_or_external = st.selectbox("Internal or External", ['Internal', 'External'])
        status = st.selectbox("Status", ['Active', 'Completed', 'On Hold'])

        submit_project = st.form_submit_button("Add Project")
        if submit_project:
            if project_name and description and start_date and expected_completion and internal_or_external and status:
                add_new_project(project_name, description, start_date, expected_completion, internal_or_external, status)
                st.success("Project added successfully!")
            else:
                st.error("Please fill all fields.")

# Add Employee Work Details
elif option == "Employee Weekly Tracker":
    st.title("🙎‍♂️Employee Weekly Tracker")
    with st.form(key='add_work_form'):
        StartDate =  st.date_input("Start Date")
        employee_name = st.text_input("Employee Name")
        project_name = st.text_input("Project Name")
        time_in_hours = st.number_input("Time Spent (in hours)", min_value=1)

        submit_work = st.form_submit_button("Add Work Details")
        if submit_work:
            if StartDate and employee_name and project_name and time_in_hours:
                add_employee_work_details(StartDate, employee_name, project_name, time_in_hours)
                st.success("Work details added successfully!")
            else:
                st.error("Please fill all fields.")

# Utilization Analysis (O/P)
elif option == "Utilization Analysis":
    st.title("🏢Utilization Analysis")
    main_table_output = fetch_main_table_data() ##Call the main_table Fech function, to do the select box tasks
    final_option = st.sidebar.selectbox("Choose a section", ["Employee_Work", "BY Employee", "BY Date", "BY Year", "BY Project", "BY WeekNumber"])

    if final_option == 'Employee_Work':
        output = main_table_output.pivot_table(
            index='Employee',
            columns='Project',
            values='Time_in_hours',
        ).fillna(0)
        st.dataframe(output)

    elif final_option == 'BY Employee':
        employee_filter = st.selectbox("Select Employee", options = main_table_output['Employee'].unique())
        filtered_data = main_table_output[main_table_output['Employee'] == employee_filter]
        if filtered_data.empty:
            st.warning(f"No work details found for employee '{employee_filter}'")
        else:
            st.dataframe(filtered_data)

    elif final_option == 'BY Date':
        date_filter = st.date_input("Select a date", value=main_table_output['WeekEnd_Date'].max())
        filtered_data = main_table_output[main_table_output['WeekEnd_Date'] == date_filter]
        if filtered_data.empty:
            st.warning(f"No work details found for the selected date {date_filter}")
        else:
            st.dataframe(filtered_data)

    elif final_option == 'BY Year':
        year_filter = st.selectbox("Select Year", options=main_table_output['Year'].unique())
        filtered_data = main_table_output[main_table_output['Year'] == year_filter]
        if filtered_data.empty:
            st.warning(f"No work details found for the selected year {year_filter}")
        else: 
            st.dataframe(filtered_data)

    elif final_option == 'BY Project':
        project_filter = st.selectbox("Select Project", options=main_table_output['Project'].unique())
        filtered_data = main_table_output[main_table_output['Project'] == project_filter]
        if filtered_data.empty:
            st.warning(f"No work details found for project '{project_filter}'")
        else:
            st.dataframe(filtered_data)

    elif final_option == 'BY WeekNumber':
        week_filter = st.selectbox("Select Week Number", options=main_table_output['WeekNumber(In that Year)'].unique())
        filtered_data = main_table_output[main_table_output['WeekNumber(In that Year)'] == week_filter]
        if filtered_data.empty:
            st.warning(f"No work details found for the selected week number {week_filter}")
        else:
            st.dataframe(filtered_data)


