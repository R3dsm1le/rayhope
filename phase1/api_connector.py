import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List 
from homeassistant_api import Client
from homeassistant_api.errors import (
    UnauthorizedError,
    EndpointNotFoundError,
    RequestTimeoutError,
    RequestError,
    HomeassistantAPIError,
)
import json 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()


#Here we fetch all the states from all entities
def fetch_states() -> List[object] | None:
    """
    It Fetches all states from the REST APIs light entities

    Reads HOME_ASSISTANT_URL and HOME_ASSSISTANT_API_KEY from .env
    Sends an authenticated GET request using the homeassistant_api Client.

    Args: 
            None

    Returns: 
            A List with all the entities.
    """
    states = []
    try:
        URL = os.environ.get("HOME_ASSISTANT_URL")
        TOKEN = os.environ.get("HOME_ASSISTANT_API_KEY")
        if not URL or not TOKEN:
            logger.error("Missing required environment variables: HOME_ASSISTANT_URL or HOME_ASSISTANT_API_KEY")
            return None
        client = Client(URL,TOKEN)
        states = client.get_states()
    except UnauthorizedError as auth_err:
         logger.error(f"Authentication failed (check HOME_ASSISTANT_API_KEY): {auth_err}")
    except EndpointNotFoundError as endpoint_err:
         logger.error(f"API endpoint not found (check HOME_ASSISTANT_URL): {endpoint_err}")
    except RequestTimeoutError as timeout_err:
         logger.error(f"Timeout error occurred : {timeout_err}")
    except RequestError as req_err:
        logger.error(f"A request error occurred: {req_err}")
    except HomeassistantAPIError as api_err:
        logger.error(f"Home Assistant API returned an error: {api_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")            
    return states

