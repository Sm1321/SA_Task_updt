import streamlit as st
import mysql.connector
import pandas as pd

# Step 1: Database Connection
@st.cache_resource
def get_database_connection():
    connection = mysql.connector.connect(
        host="127.0.0.1",  #  host
        user="root",       #  username
        password="1234",   # password
        database="Temporary_Employee_Tracker"  # database name
    )
    return connection

# Step 2: Fetch Data with Column Names
def fetch_employee_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee_list")
    rows = cursor.fetchall()
    columns = ["Name", "Position", "Skills", "CurrentStatus"]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    return df

def fetch_main_table_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM main_table")
    rows = cursor.fetchall()
    columns = ["WeekDay", "Employee", "Project", "Time_in_hours"]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    return df

def fetch_project_list_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Project_List")
    rows = cursor.fetchall()
    columns = ["Project", "Description", "StartDate", "Expected_to_Complete", "Internal_or_External", "Status"]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    return df

# Step 3: Insert New Employee
def add_new_employee(name, position, skills, current_status):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
    """
    INSERT INTO employee_list (Name, Position, Skills, CurrentStatus) 
    VALUES (%s, %s, %s, %s)
    """, (name, position, skills, current_status)
        )
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
def add_employee_work_details(weekday, employee, project, time_in_hours):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO main_table (WeekDay, Employee, Project, Time_in_hours) 
    VALUES (%s, %s, %s, %s)
    """, (weekday, employee, project, time_in_hours))
    connection.commit()
    cursor.close()

# Step 6: Streamlit App Layout with Sidebar
st.sidebar.title("Choose your Task here")
option = st.sidebar.selectbox(
    "Choose a section",
    ["Dashboard", "Add New Employee", "Add New Project", "Add Employee Work Details", "Utilization Analysis (O/P)"]
)


####################################### SELECT BOX For ADDIND DATA and RESULT #####################################################3
# Dashboard - Display DataFrames
if option == "Dashboard":
    st.title("🏢Employee Tracker Dashboard")

    # Display DataFrames
    st.header("👨Employee List")
    employee_data = fetch_employee_data()
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
elif option == "Add Employee Work Details":
    st.title("🙎‍♂️Add Employee Work Details")
    with st.form(key='add_work_form'):
        weekday = st.number_input("Week Day", min_value=1, max_value=7)
        employee_name = st.text_input("Employee Name")
        project_name = st.text_input("Project Name")
        time_in_hours = st.number_input("Time Spent (in hours)", min_value=1)

        submit_work = st.form_submit_button("Add Work Details")
        if submit_work:
            if weekday and employee_name and project_name and time_in_hours:
                add_employee_work_details(weekday, employee_name, project_name, time_in_hours)
                st.success("Work details added successfully!")
            else:
                st.error("Please fill all fields.")

# Utilization Analysis (O/P)
elif option == "Utilization Analysis (O/P)":
    st.title("🏢Utilization Analysis (O/P)")

    # Fetch the main table data and create a pivot table
    main_table_output = fetch_main_table_data()

    # Generate Output Table using Pivot Table
    ## Piviot Table :- The Piviot Opertor is Used to transform Rows into columns ,summarize data for better readability and Analysis.
    output = main_table_output.pivot_table(
        index='Employee',  # Rows will be employees
        columns='Project',  # Columns will be projects
        values='Time_in_hours',  # Values will be the time spent (in hours)
        #aggfunc='sum'  # Aggregating the time spent in case there are multiple records for the same employee and project
    ).fillna(0)  # Replace NaN with 0 

    # Display the pivot table
    st.dataframe(output)
