from api_connector import fetch_states
import datetime
import json 
from data_parser import parse_data

states = fetch_states()
clean_states = parse_data(states)
print(clean_states)