import streamlit as st
from utils.pinecone_utils import format_stats, get_active_indexes, get_index_stats


def view_indexes_page():
    st.title("View Indexes")

    try:
        indexes = get_active_indexes()

        if not indexes:
            st.warning("No active indexes found")
            return

        # Display total number of indexes
        st.subheader(
            f"Found {len(indexes)} active {'index' if len(indexes) == 1 else 'indexes'}"
        )

        # Create tabs for each index
        tabs = st.tabs(indexes)

        for index, tab in zip(indexes, tabs):
            with tab:
                try:
                    # Get and format index statistics
                    stats = get_index_stats(index)

                    formatted_stats = format_stats(stats)

                    # Display basic stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Total Vectors", formatted_stats.get("Total Vectors", 0)
                        )
                    with col2:
                        st.metric("Dimension", formatted_stats.get("Dimension", 0))
                    with col3:
                        st.metric(
                            "Index Fullness",
                            formatted_stats.get("Index Fullness", "0%"),
                        )

                    # Display namespaces if any
                    if formatted_stats.get("Namespaces"):
                        st.subheader("Namespaces")
                        for ns_name, ns_data in formatted_stats["Namespaces"].items():
                            st.metric(
                                f"Namespace: {ns_name}",
                                f"Vectors: {ns_data['Vector Count']}",
                            )

                    # Display raw stats in expander
                    with st.expander("Raw Statistics"):
                        st.json(stats)

                    # Add query interface
                    st.subheader("Query Index")
                    query = st.text_area(
                        "Enter your query",
                        placeholder="Type your search query here...",
                        key=f"query_{index}",
                    )

                    if st.button("Search", key=f"search_{index}"):
                        if query:
                            st.info("Query functionality coming soon!")
                        else:
                            st.warning("Please enter a query first")

                except Exception as e:
                    st.error(f"Error retrieving stats for {index}")
                    st.exception(e)

    except Exception as e:
        st.error("Error connecting to Pinecone")
        st.exception(e)


if __name__ == "__main__":
    view_indexes_page()
