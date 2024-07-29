import streamlit as st
import time

class SimulatedDatabaseConnection:
    """
    A class to simulate a database connection.
    
    This class is used to demonstrate how st.cache_resource works with
    non-data objects like database connections.
    """

    def __init__(self, connection_string):
        """
        Initialize the simulated database connection.

        Args:
            connection_string (str): A string representing the database connection details.
        """
        self.connection_string = connection_string
        self.connected_at = time.time()

    def query(self, sql):
        """
        Simulate executing a SQL query.

        Args:
            sql (str): The SQL query to execute.

        Returns:
            str: A string representing the execution of the query.
        """
        return f"Executing '{sql}' on connection established at {self.connected_at}"

@st.cache_resource
def get_database_connection(connection_string):
    """
    Get or create a database connection.

    This function is cached using st.cache_resource. It will return the same
    connection object for the same connection_string, simulating connection pooling.

    Args:
        connection_string (str): The connection string for the database.

    Returns:
        SimulatedDatabaseConnection: A simulated database connection object.
    """
    # Simulate an expensive connection process
    time.sleep(2)
    return SimulatedDatabaseConnection(connection_string)

def main():
    """
    Main function to run the Streamlit app.

    This function sets up the Streamlit interface and demonstrates the use of
    st.cache_resource with a simulated database connection.
    """
    st.title("Streamlit Cache Resource Demo")

    st.write("This demo shows how `st.cache_resource` works with a simulated database connection.")

    # First connection
    st.subheader("First Connection (ref1)")
    connection_string1 = "database1:3306"
    start_time = time.time()
    s1 = get_database_connection(connection_string1)
    end_time = time.time()
    st.write(f"Time taken: {end_time - start_time:.2f} seconds")
    st.write(s1.query("SELECT * FROM table1"))

    # Second connection (same as first)
    st.subheader("Second Connection (ref1 again)")
    start_time = time.time()
    s2 = get_database_connection(connection_string1)
    end_time = time.time()
    st.write(f"Time taken: {end_time - start_time:.2f} seconds")
    st.write(s2.query("SELECT * FROM table2"))
    st.write(f"s1 == s2: {s1 is s2}")

    # Third connection (different connection string)
    st.subheader("Third Connection (ref2)")
    connection_string2 = "database2:3306"
    start_time = time.time()
    s3 = get_database_connection(connection_string2)
    end_time = time.time()
    st.write(f"Time taken: {end_time - start_time:.2f} seconds")
    st.write(s3.query("SELECT * FROM table3"))
    st.write(f"s1 == s3: {s1 is s3}")

    # Clear cache for the function
    if st.button("Clear cache for get_database_connection"):
        get_database_connection.clear()
        st.write("Cache cleared for get_database_connection")

    # Clear all cached resources
    if st.button("Clear all cached resources"):
        st.cache_resource.clear()
        st.write("All cached resources cleared")

if __name__ == "__main__":
    main()