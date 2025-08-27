"""Example script to fetch Instagram user posts using ensembledata.

Loads the API token from a .env file using python-dotenv. Ensure there's a
line like ENSEMBLE_DATA_API=your_token in the .env file at the project root
or current working directory when running this script.
"""

import os
from dotenv import load_dotenv  # python-dotenv
from ensembledata.api import EDClient


def get_client() -> EDClient:
    """Load environment variables and return an initialized EDClient.

    Raises:
        RuntimeError: if ENSEMBLE_DATA_API is not set in the environment.
    """
    # Load variables from .env (does nothing if already loaded)
    load_dotenv()

    token = os.getenv("ENSEMBLE_DATA_API")
    if not token:
        raise RuntimeError(
            "Missing ENSEMBLE_DATA_API environment variable. Add it to your .env file."  # noqa: E501
        )
    return EDClient(token=token)


def main():
    client = get_client()
    result = client.instagram.user_posts(
        user_id=18428658,
        depth=1,
    )

    print("Posts data:")
    print(result.data)
    print("Units charged:", result.units_charged)


if __name__ == "__main__":  # pragma: no cover
    main()

