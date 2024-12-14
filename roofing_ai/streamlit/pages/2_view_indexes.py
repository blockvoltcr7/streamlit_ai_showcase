import streamlit as st
from utils.pinecone_utils import (
    delete_namespace,
    get_active_indexes,
    get_index_stats,
    query_index,
)


def display_search_results(results):
    """Display search results."""
    st.subheader(f"Search Results ({results['total_results']} matches)")

    if not results["matches"]:
        st.info("No matching documents found.")
        return

    for i, match in enumerate(results["matches"], 1):
        with st.expander(f"Result #{i} - {match['metadata'].get('title', 'Untitled')}"):
            st.write("**Content:**")
            st.write(match["content"])

            st.write("**Metadata:**")
            metadata = match["metadata"]
            cols = st.columns(2)
            with cols[0]:
                st.write(f"Category: {metadata.get('category', 'N/A')}")
                st.write(f"Author: {metadata.get('author', 'N/A')}")
            with cols[1]:
                st.write(f"Date: {metadata.get('date_created', 'N/A')}")
                if tags := metadata.get("tags"):
                    st.write(f"Tags: {', '.join(tags)}")


def view_indexes_page():
    st.title("View & Manage Indexes")

    try:
        indexes = get_active_indexes()
        if not indexes:
            st.warning("No active indexes found")
            return

        # Create tabs for Search and Management
        search_tab, manage_tab = st.tabs(["Search Documents", "Manage Namespaces"])

        with search_tab:
            # Select index and namespace
            selected_index = st.selectbox("Select Index", indexes)

            # Get available namespaces for the selected index
            try:
                stats = get_index_stats(selected_index)
                available_namespaces = list(stats.namespaces.keys())
                # Replace empty namespace with "default" for display
                available_namespaces = [
                    "default" if ns == "" else ns for ns in available_namespaces
                ]

                if available_namespaces:
                    # Show dropdown if namespaces exist
                    namespace = st.selectbox(
                        "Select Namespace",
                        options=available_namespaces,
                        help="Select a namespace to search within",
                        key="search_namespace",
                    )
                    # Convert "default" back to empty string for Pinecone
                    namespace = "" if namespace == "default" else namespace
                else:
                    # Show input field if no namespaces exist
                    namespace = st.text_input(
                        "Create New Namespace",
                        help="No existing namespaces found. Please create a new one.",
                        key="new_namespace",
                    )

                # Search interface
                query = st.text_area("Enter your search query")
                top_k = st.slider("Number of results", 1, 20, 5)

                # Only show search button if namespace is provided
                if namespace.strip():
                    if st.button("Search", type="primary"):
                        if query:
                            try:
                                with st.spinner("Searching..."):
                                    results = query_index(
                                        selected_index, query, namespace, top_k
                                    )
                                    display_search_results(results)
                            except Exception as e:
                                st.error(f"Search error: {str(e)}")
                        else:
                            st.warning("Please enter a search query")
                else:
                    st.error("Please enter a namespace before searching")

            except Exception as e:
                st.error(f"Error fetching namespaces: {str(e)}")

        with manage_tab:
            # Namespace management
            st.subheader("Manage Namespaces")

            # Select index
            selected_index = st.selectbox("Select Index", indexes, key="manage_index")

            # Show index stats
            try:
                stats = get_index_stats(selected_index)
                st.write("### Index Statistics")

                # Create metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Total Vectors",
                        f"{stats.total_vector_count:,}",
                        help="Total number of vectors in the index",
                    )
                with col2:
                    st.metric(
                        "Dimension",
                        stats.dimension,
                        help="Vector dimension size",
                    )
                with col3:
                    st.metric(
                        "Index Fullness",
                        f"{stats.index_fullness:.1%}",
                        help="Percentage of index capacity used",
                    )

                # Display namespace information
                if stats.namespaces:
                    st.write("#### Namespace Distribution")

                    # Create a bar chart for namespace vector counts
                    namespace_data = {
                        ns: ns_stats.vector_count
                        for ns, ns_stats in stats.namespaces.items()
                    }

                    # Handle empty namespace key
                    if "" in namespace_data:
                        namespace_data["default"] = namespace_data.pop("")

                    # Create chart data
                    chart_data = {
                        "Namespace": list(namespace_data.keys()),
                        "Vectors": list(namespace_data.values()),
                    }

                    # Display bar chart
                    st.bar_chart(
                        chart_data, x="Namespace", y="Vectors", use_container_width=True
                    )

                    # Display detailed namespace information in an expander
                    with st.expander("Detailed Namespace Information"):
                        # Create a table for namespace details
                        namespace_table = []
                        for ns, ns_stats in stats.namespaces.items():
                            namespace_table.append(
                                {
                                    "Namespace": "default" if ns == "" else ns,
                                    "Vector Count": f"{ns_stats.vector_count:,}",
                                    "Percentage": f"{ns_stats.vector_count / stats.total_vector_count:.1%}",
                                }
                            )

                        st.table(namespace_table)
                else:
                    st.info("No namespaces found in this index")

                # Show raw stats in expander
                with st.expander("Raw Statistics"):
                    formatted_stats = {
                        "total_vector_count": stats.total_vector_count,
                        "dimension": stats.dimension,
                        "index_fullness": stats.index_fullness,
                        "namespaces": {
                            ns: {"vector_count": ns_stats.vector_count}
                            for ns, ns_stats in stats.namespaces.items()
                        },
                    }
                    st.json(formatted_stats)

            except Exception as e:
                st.error(f"Error retrieving index statistics: {str(e)}")

            # Delete namespace
            st.subheader("Delete Namespace")
            namespace_to_delete = st.text_input(
                "Enter namespace to delete",
                help="Warning: This will delete all documents in the namespace",
            )

            # Changed button type from "danger" to "primary" and added warning color styling
            col1, col2 = st.columns([3, 1])
            with col1:
                confirm = st.checkbox("I understand this action cannot be undone")
            with col2:
                if st.button(
                    "Delete Namespace", type="primary", use_container_width=True
                ):
                    if namespace_to_delete:
                        if confirm:
                            try:
                                delete_namespace(selected_index, namespace_to_delete)
                                st.success(
                                    f"Namespace '{namespace_to_delete}' deleted successfully"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting namespace: {str(e)}")
                        else:
                            st.warning("Please confirm that you understand this action")
                    else:
                        st.warning("Please enter a namespace name")

    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    view_indexes_page()
