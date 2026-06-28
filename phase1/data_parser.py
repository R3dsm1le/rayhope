import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



#Here we filter the entities for just having lights and also checking attributes from them 
def parse_data(raw_data : list[object] | None) -> list[dict] | None: 
    """
    This function takes the List returned from fetch_states() and checks for required fields

    Args : 
        List of States from fetch_states() : List

    Returns: 

        This function returns a cleaned list of states : List
    
    """
    light_entities = []
    if raw_data is None:
        return
    for idx, entity in enumerate(raw_data):
        entity_brightness = entity.attributes.get('brightness')
        if entity.entity_id.startswith('light'):
           if entity.state not in ['on','off']:
             continue
           if entity.state == "off":
             entity_brightness = 0.0
           else:
             entity_brightness = float(entity_brightness) / 2.55
           light_entities.append({"entity_id" : entity.entity_id, "state" : entity.state, "brightness" : entity_brightness, "last_changed" : entity.last_changed.strftime("%B %d, %Y, %I:%M %p")})       
    return light_entities           
    














































