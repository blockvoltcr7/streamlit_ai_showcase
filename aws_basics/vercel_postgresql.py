from typing import Optional, Tuple

import pg8000.native


class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.POSTGRES_URL = "postgres://default:DoVnEB0csy9P@ep-noisy-bush-a4hrp4tj-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
        url_parts = self.POSTGRES_URL.replace("postgres://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_port_db = url_parts[1].split("/")
        host_port = host_port_db[0].split(":")

        self.config = {
            "user": user_pass[0],
            "password": user_pass[1],
            "host": host_port[0],
            "port": int(host_port[1]),
            "database": host_port_db[1].split("?")[0],
            "ssl_context": True,
        }

    def connect(self) -> Tuple[bool, Optional[str]]:
        """
        Establishes a connection to the PostgreSQL database.
        Returns: Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            self.conn = pg8000.native.Connection(**self.config)
            print("Connection to PostgreSQL established successfully.")
            return True, None
        except Exception as e:
            return False, f"Error connecting to PostgreSQL: {str(e)}"

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Tests the database connection by executing a simple query.
        Returns: Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            version = self.conn.run("SELECT version();")
            return (
                True,
                f"Successfully connected to PostgreSQL. Version: {version[0][0]}",
            )
        except Exception as e:
            return False, f"Error executing query: {str(e)}"

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()


def main():
    # Initialize database connection
    db = DatabaseConnection()

    # Connect to the database
    success, error = db.connect()
    if not success:
        print(error)
        return

    # Test the connection
    success, message = db.test_connection()
    print(message)

    # Close the connection
    db.close()


if __name__ == "__main__":
    main()
