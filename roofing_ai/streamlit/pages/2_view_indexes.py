import streamlit as st
from utils.pinecone_utils import (
    format_stats,
    get_active_indexes,
    get_index_stats,
    query_index,
)


def display_search_results(results):
    """Display search results in a formatted way."""
    st.subheader(f"Search Results ({results['total_results']} matches)")

    if not results.get("matches"):
        st.info("No matching documents found.")
        return

    # Display query information
    st.write(f"**Query:** {results['query']}")
    if results.get("namespace"):
        st.write(f"**Namespace:** {results['namespace']}")

    # Display results
    for i, match in enumerate(results["matches"], 1):
        with st.expander(
            f"#{i} - {match['metadata']['title']} (Score: {match['score']:.4f})"
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Main content
                if description := match["metadata"].get("description"):
                    st.markdown(f"**Description:**\n{description}")

                if snippet := match["metadata"].get("content_snippet"):
                    st.markdown(f"**Content Preview:**\n{snippet}")

            with col2:
                # Metadata sidebar
                st.markdown("**Document Info:**")
                st.write(f"Category: {match['metadata']['category']}")
                st.write(f"Type: {match['metadata']['document_type']}")
                st.write(f"Author: {match['metadata']['author']}")
                st.write(f"Last Updated: {match['metadata']['date_last_updated']}")

            # Tags and Keywords
            if tags := match["metadata"].get("tags"):
                st.markdown("**Tags:**")
                st.write(", ".join(tags))

            if keywords := match["metadata"].get("keywords"):
                st.markdown("**Keywords:**")
                st.write(", ".join(keywords))

            # Document ID for reference
            st.caption(f"Document ID: {match['id']}")


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
                    st.divider()
                    st.subheader("🔍 Search Documents")

                    # Query input
                    query = st.text_area(
                        "Enter your question",
                        placeholder="Type your question here to search through the documents...",
                        key=f"query_{index}",
                        help="Enter a natural language question or search term. The system will find the most relevant documents.",
                    )

                    # Search options
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        top_k = st.number_input(
                            "Number of results",
                            min_value=1,
                            max_value=20,
                            value=5,
                            key=f"top_k_{index}",
                        )

                    # Search button
                    if st.button("🔍 Search", key=f"search_{index}", type="primary"):
                        if query:
                            try:
                                with st.spinner("Searching documents..."):
                                    # Perform semantic search
                                    results = query_index(index, query, top_k=top_k)

                                    # Display results
                                    st.divider()
                                    display_search_results(results)

                            except Exception as e:
                                st.error("Error executing semantic search")
                                st.exception(e)
                        else:
                            st.warning("Please enter a question or search term first")

                except Exception as e:
                    st.error(f"Error retrieving stats for {index}")
                    st.exception(e)

    except Exception as e:
        st.error("Error connecting to Pinecone")
        st.exception(e)


if __name__ == "__main__":
    view_indexes_page()
