import streamlit as st
import pandas as pd
import os        # To check file existence and manage paths
import subprocess # To run the external script
import sys        # To get the current Python executable path
import time       # For potential brief pauses if needed

# --- Configuration ---
CSV_FILE_PATH = "course_data.csv"
SCRAPER_SCRIPT_PATH = "tutorial_cloud_old.py" # Path to your scraper script
LOCAL_SCRAPER_SCRIPT_PATH = "local_version.py"

st.set_page_config(page_title="Credentials Saver", layout="centered")

# --- App Title ---
st.title("Edit Username and Password")
options = ["FA 2025-26", "SU 1 2024-25", "SP 2024-25", "FA 2024-25","SU 2 2023-24","SU 1 2023-24","SP 2023-24","FA 2023-24","SU 2 2022-23"] 

Selected_Term = st.selectbox("Term:", options)
st.write("You selected:", Selected_Term)

# Using unique keys helps Streamlit manage state if the app reruns
username = st.text_input("Enter your Username:", key="username_input")
# Use type="password" to mask the input
password = st.text_input("Enter your Password:", type="password", key="password_input")

submitted = st.button("Save to .env file")

# --- Processing Logic ---
if submitted:
    # Basic check: ensure both fields have some input
    if username and password:
        # Define the content to write
        env_content = f"PORTAL_USERNAME={username}\nPORTAL_PASSWORD={password}\nSELECTED_TERM={Selected_Term}\n"
        file_path = ".env" # Standard name for environment variable files

        try:
            # Open the file in write mode ('w')
            # This creates the file if it doesn't exist, or overwrites it if it does.
            with open(file_path, "w") as f:
                f.write(env_content)

            # Provide feedback to the user
            st.success(f"Successfully wrote credentials to `{file_path}`!")
            st.info(f"The file `{file_path}` has been created/updated in the same directory as the script.")
            

        except IOError as e:
            st.error(f"Error writing to file: {e}")
            st.error(f"Could not write to `{file_path}`. Please check file permissions in the directory: {os.getcwd()}")
        except Exception as e:
             st.error(f"An unexpected error occurred: {e}")

    else:
        # If fields are empty
        st.warning("Please enter both username and password.")

# --- Caching Function for Loading Data ---
@st.cache_data
def load_data(file_path):
    """Loads data from the CSV file."""
    if not os.path.exists(file_path):
        # Don't show error initially, only if reload is attempted / data expected
        return pd.DataFrame() # Return empty DataFrame if file missing
    try:
        df = pd.read_csv(file_path)
        # Basic data cleaning
        for col in ['credits', 'max_enrollment', 'total_enrollment']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        for col in ['course', 'course_name', 'instructor', 'room', 'days', 'start_time', 'end_time']:
            if col in df.columns:
                df[col] = df[col].fillna('N/A')
        return df
    except pd.errors.EmptyDataError:
        st.warning(f"Warning: '{file_path}' is empty.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading or processing CSV file: {e}")
        return pd.DataFrame()

# --- Function to run the scraper ---
def local_run_scraper_script():
    """Runs the tutorial_cloud.py script as a subprocess."""
    try:
        python_executable = sys.executable # Get path to current python interpreter
        st.info(f"Starting course data update script (`{LOCAL_SCRAPER_SCRIPT_PATH}`)... Please wait, this may take a few minutes.")
        st.spinner("Executing scraper...")
        # Use Popen for non-blocking execution initially, but wait here for simplicity
        # For a truly non-blocking UI, you'd need more complex state management
        # Using check_output to wait and capture output/errors
        process = subprocess.run(
            [python_executable, LOCAL_SCRAPER_SCRIPT_PATH],
            capture_output=True,
            text=True,
            check=True, # Raise CalledProcessError if script fails (non-zero exit code)
            encoding='utf-8' # Ensure consistent text encoding
        )
        st.success(f"Data update script finished successfully!")
        # Optionally display script output (can be long)
        # with st.expander("Show Script Output"):
        #    st.code(process.stdout)
        # Clear cache AFTER successful run
        st.cache_data.clear()
        return True # Indicate success
    except FileNotFoundError:
        st.error(f"Error: Scraper script '{LOCAL_SCRAPER_SCRIPT_PATH}' not found.")
        st.error(f"Make sure it's in the same directory as the Streamlit app or provide the correct path.")
        return False
    except subprocess.CalledProcessError as e:
        st.error(f"Error running the data update script:")
        st.error(f"Exit Code: {e.returncode}")
        st.error("Script Output (stderr):")
        st.code(e.stderr)
        st.error("Script Output (stdout):")
        st.code(e.stdout)
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while trying to run the script: {e}")
        return False


def run_scraper_script():
    """Runs the tutorial_cloud.py script as a subprocess."""
    try:
        python_executable = sys.executable # Get path to current python interpreter
        st.info(f"Starting course data update script (`{SCRAPER_SCRIPT_PATH}`)... Please wait, this may take a few minutes.")
        st.spinner("Executing scraper...")
        # Use Popen for non-blocking execution initially, but wait here for simplicity
        # For a truly non-blocking UI, you'd need more complex state management
        # Using check_output to wait and capture output/errors
        process = subprocess.run(
            [python_executable, SCRAPER_SCRIPT_PATH],
            capture_output=True,
            text=True,
            check=True, # Raise CalledProcessError if script fails (non-zero exit code)
            encoding='utf-8' # Ensure consistent text encoding
        )
        st.success(f"Data update script finished successfully!")
        # Optionally display script output (can be long)
        # with st.expander("Show Script Output"):
        #    st.code(process.stdout)
        # Clear cache AFTER successful run
        st.cache_data.clear()
        return True # Indicate success
    except FileNotFoundError:
        st.error(f"Error: Scraper script '{SCRAPER_SCRIPT_PATH}' not found.")
        st.error(f"Make sure it's in the same directory as the Streamlit app or provide the correct path.")
        return False
    except subprocess.CalledProcessError as e:
        st.error(f"Error running the data update script:")
        st.error(f"Exit Code: {e.returncode}")
        st.error("Script Output (stderr):")
        st.code(e.stderr)
        st.error("Script Output (stdout):")
        st.code(e.stdout)
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while trying to run the script: {e}")
        return False

# --- Initialize Session State ---
# Use session state to track if data needs reloading after scraping
if 'needs_reload' not in st.session_state:
    st.session_state.needs_reload = False


# --- Main App Logic ---

# --- Sidebar ---
st.sidebar.header("Controls & Filters")

# Button to run the scraper
if st.sidebar.button("Update Course Data FROM CLOUD MODEL"):
    if run_scraper_script():
         st.session_state.needs_reload = True # Flag that data should be reloaded
         st.rerun() # Force rerun to reload data immediately
    else:
         st.session_state.needs_reload = False # Reset flag on failure


if st.sidebar.button("Update Course Data FROM LOCAL MODEL"):
    if local_run_scraper_script():
         st.session_state.needs_reload = True # Flag that data should be reloaded
         st.rerun() # Force rerun to reload data immediately
    else:
         st.session_state.needs_reload = False # Reset flag on failure         


# Reload Button (from existing CSV)
if st.sidebar.button("🔄 Reload Data from CSV"):
    st.cache_data.clear() # Clear the cache for the load_data function
    st.success(f"Cleared cache. Data will reload from {CSV_FILE_PATH} on next interaction.")
    st.session_state.needs_reload = True # Flag that data should be reloaded
    st.rerun() # Force rerun to reload data

# Load data - this will now run after buttons cause a rerun
data = load_data(CSV_FILE_PATH)

# --- Filter Widgets (only if data is available) ---
if not data.empty:
    st.sidebar.markdown("---") # Separator
    st.sidebar.subheader("Filter Courses:")

    # Create filter widgets
    course_code_filter = st.sidebar.text_input("Course Code (contains)", key="course_filter")
    course_name_filter = st.sidebar.text_input("Course Name (contains)", key="name_filter")

    instructor_options = [''] + sorted(data['instructor'].astype(str).unique()) if 'instructor' in data.columns else ['']
    instructor_filter = st.sidebar.selectbox("Instructor", options=instructor_options, key="instructor_filter", index=0)

    days_options = sorted(data['days'].astype(str).unique()) if 'days' in data.columns else []
    days_filter = st.sidebar.multiselect("Days", options=days_options, key="days_filter")

    room_filter = st.sidebar.text_input("Room (contains)", key="room_filter")

    min_credits, max_credits = (0, int(data['credits'].max())) if 'credits' in data.columns and not data['credits'].isnull().all() else (0, 10)
    credit_filter = st.sidebar.slider("Credits", min_value=min_credits, max_value=max_credits, value=(min_credits, max_credits), key="credit_filter", disabled=(min_credits==max_credits))

    # --- Filtering Logic ---
    filtered_data = data.copy()
    if course_code_filter:
        filtered_data = filtered_data[filtered_data['course'].str.contains(course_code_filter, case=False, na=False)]
    if course_name_filter:
        filtered_data = filtered_data[filtered_data['course_name'].str.contains(course_name_filter, case=False, na=False)]
    if instructor_filter:
        filtered_data = filtered_data[filtered_data['instructor'] == instructor_filter]
    if days_filter:
        filtered_data = filtered_data[filtered_data['days'].isin(days_filter)]
    if room_filter:
         if 'room' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['room'].str.contains(room_filter, case=False, na=False)]
    if 'credits' in filtered_data.columns and not credit_filter == (min_credits, max_credits):
        filtered_data = filtered_data[filtered_data['credits'].between(credit_filter[0], credit_filter[1], inclusive='both')]

else:
    # If data is empty initially or after failed load, create empty frame for consistency
    filtered_data = pd.DataFrame()


# --- Main Area Display ---
st.title("🎓 Course Data Viewer")

# Display appropriate messages or the dataframe
if data.empty and not os.path.exists(CSV_FILE_PATH):
    st.warning(f"'{CSV_FILE_PATH}' not found. Use the 'Update Course Data' button to generate it.")
elif data.empty:
     st.info("No course data to display. Try reloading or updating.")
else:
    st.write(f"Displaying {len(filtered_data)} out of {len(data)} total courses.")
    st.dataframe(filtered_data, use_container_width=True)

    # Optional: Show some summary stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Total Courses Loaded:** {len(data)}")
    st.sidebar.markdown(f"**Courses Displayed:** {len(filtered_data)}")

# Reset the reload flag after processing
st.session_state.needs_reload = False