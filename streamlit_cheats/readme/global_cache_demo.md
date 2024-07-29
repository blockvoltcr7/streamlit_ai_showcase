# Cache Global Resources in Streamlit

## What is `st.cache_resource`?

`st.cache_resource` is a powerful caching decorator in Streamlit designed to optimize the performance of your Streamlit applications by caching global resources. Unlike `st.cache_data` which is used for caching data objects, `st.cache_resource` is specifically for non-data objects that you want to keep in memory and reuse across multiple reruns of your app.

## Why is it useful?

1. **Performance Improvement**: By caching resource-intensive objects, `st.cache_resource` can significantly speed up your Streamlit app, especially for operations that involve creating or connecting to external resources.

2. **Resource Efficiency**: It helps in managing resources effectively by reusing existing connections or objects instead of creating new ones for each rerun or user interaction.

3. **Consistency**: Ensures that the same resource instance is used across different parts of your app, which can be crucial for maintaining state or ensuring consistent behavior.

4. **Cost Reduction**: For cloud-based resources or services charged by connection or instance, reusing resources can lead to significant cost savings.

5. **Simplified Code**: Allows you to write cleaner code by abstracting away the complexity of resource management and reuse.

## What is it used for?

`st.cache_resource` is typically used for:

1. **Database Connections**: Maintaining persistent database connections.
2. **API Clients**: Keeping instances of API clients that might have rate limiting or connection pooling.
3. **Machine Learning Models**: Holding loaded ML models in memory for quick inference.
4. **Global Configuration Objects**: Storing application-wide settings or configurations.
5. **External Service Connections**: Managing connections to external services like message queues, caches, or search engines.

## How is it used in real-world applications?

Here are some real-world examples of using `st.cache_resource`:

### 1. Database Connection Pool

```python
import streamlit as st
import psycopg2
from psycopg2.pool import SimpleConnectionPool

@st.cache_resource
def get_db_pool():
    return SimpleConnectionPool(1, 10,
        dbname="your_db",
        user="your_user",
        password="your_password",
        host="your_host"
    )

# Usage
pool = get_db_pool()
with pool.getconn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM your_table")
        data = cur.fetchall()
    pool.putconn(conn)

st.write(data)
```

This example creates a connection pool to a PostgreSQL database. The pool is created once and reused across multiple queries, improving performance and resource management.

### 2. Loading a Large Machine Learning Model

```python
import streamlit as st
import tensorflow as tf

@st.cache_resource
def load_model():
    return tf.keras.models.load_model('path/to/your/model.h5')

# Usage
model = load_model()
prediction = model.predict(new_data)
st.write(prediction)
```

Here, a large TensorFlow model is loaded once and kept in memory. This is particularly useful for models that take a long time to load but are quick to make predictions once loaded.

### 3. API Client with Rate Limiting

```python
import streamlit as st
import requests
from ratelimit import limits, sleep_and_retry

class APIClient:
    @sleep_and_retry
    @limits(calls=5, period=1)  # 5 calls per second
    def call_api(self, endpoint):
        response = requests.get(f"https://api.example.com/{endpoint}")
        return response.json()

@st.cache_resource
def get_api_client():
    return APIClient()

# Usage
client = get_api_client()
data = client.call_api("some_endpoint")
st.write(data)
```

This example creates an API client with built-in rate limiting. The client is created once and reused, ensuring that rate limits are respected across all uses of the API in the Streamlit app.

## Best Practices

1. Use `st.cache_resource` for objects that are expensive to create but can be reused.
2. Be mindful of memory usage, as cached resources persist in memory.
3. Use the `clear()` method or `st.cache_resource.clear()` when you need to reset or update the cached resources.
4. Consider adding error handling and reconnection logic for resources like database connections that might become stale over time.

By effectively using `st.cache_resource`, you can create Streamlit apps that are not only functional but also performant and resource-efficient, providing a better experience for your users and more efficient use of your computing resources.