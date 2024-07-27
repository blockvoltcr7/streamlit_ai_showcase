import streamlit as st
import time

class SimulatedDatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connected_at = time.time()

    def query(self, sql):
        return f"Executing '{sql}' on connection established at {self.connected_at}"

@st.cache_resource
def get_database_connection(connection_string):
    # Simulate an expensive connection process
    time.sleep(2)
    return SimulatedDatabaseConnection(connection_string)

def main():
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