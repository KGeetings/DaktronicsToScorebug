import requests
import json
import time
import os
from typing import Dict, Any

class BasketballDataParser:
	def __init__(self, url: str, output_dir: str = "game_data"):
		self.url = url
		self.output_dir = output_dir
		self.fields_to_extract = [
			"Main_Clock_Time__mm_ss_ss_t__",
			"Home_Team_Score",
			"Guest_Team_Score",
			"Home_Time_Outs_Left___Total",
			"Guest_Time_Outs_Left___Total",
			"Period_Text___1st_____OT______OT_2__",
			"Period_Description___End_of_1st____",
			"Home_Possession_Indicator______or_____",
			"Guest_Possession_Indicator______or_____",
			"Home_Team_Fouls",
			"Guest_Team_Fouls",
			"Shot_Clock_Time__mm_ss____",
			"Time_Out_Time__mm_ss____"
		]

		# Create output directory if it doesn't exist
		os.makedirs(output_dir, exist_ok=True)

		# Initialize previous values dictionary
		self.previous_values = {}

		# Define text transformations
		self.text_transformations = {
			"Home_Possession_Indicator______or_____": {
				">": ".",
				"<": ".",  # Remove left arrow if present
				"None": "", # Handle "None" string
				"": ""    # Handle empty string
			},
			"Guest_Possession_Indicator______or_____": {
				">": ".",
				"<": ".",  # Remove left arrow if present
				"None": "", # Handle "None" string
				"": ""    # Handle empty string
			},
			"Home_Time_Outs_Left___Total": {str(i): "I " * i for i in range(10)},
			"Guest_Time_Outs_Left___Total": {str(i): "I " * i for i in range(10)}
		}

	def fetch_data(self) -> Dict[str, Any]:
		#Fetch JSON data from the URL.
		try:
			response = requests.get(self.url)
			response.raise_for_status()
			return response.json()
		except requests.RequestException as e:
			print(f"Error fetching data: {e}")
			return None

	def extract_field_value(self, data: Dict[str, Any], field_name: str) -> str:
		try:
			for column in data['table'][0]['range']['column']:
				if column['name'] == field_name:
					for row in data['table'][0]['range']['row']:
						if row['title'] == 'Value':
							for field in row['field']:
								if field['name'] == field_name:
									# Return None for empty strings
									return field['value'] if field['value'].strip() else None
			return None
		except (KeyError, IndexError):
			return None

	def transform_value(self, field_name: str, value: str) -> str:
		if field_name in self.text_transformations:
			transforms = self.text_transformations[field_name]
			for original, replacement in transforms.items():
				if value == original:
					return replacement
			# If no transformation matches, return original value
			return value
		return value

	def save_field_to_file(self, field_name: str, value: str):
		# Apply any transformations
		value = self.transform_value(field_name, value)

		# If value is None (and not possession strings, since these expect to be none), do not save anything to the file
		#print(f"Field name: '{field_name}' Value: '{value}'")
		if value is None:
			value = ""

		# Store the new value
		self.previous_values[field_name] = value

		filename = os.path.join(self.output_dir, f"{field_name}.txt")

		# Read the existing content of the file
		#if os.path.exists(filename):
		#	with open(filename, 'r') as f:
		#		existing_content = f.read()
		#	# Check if the existing content matches the new value
		#	if existing_content == value:
		#		return

		filename = os.path.join(self.output_dir, f"{field_name}.txt")
		with open(filename, 'w') as f:
			f.write(str(value))

	def process_data(self):
		data = self.fetch_data()
		if not data:
			return

		# Extract and save each field
		for field in self.fields_to_extract:
			value = self.extract_field_value(data, field)
			self.save_field_to_file(field, value)

def main():
	# URL of the basketball data
	url = "http://192.168.10.166//player/dataset/tables/RTD%2FAS5-Basketball.json"

	# Create parser instance
	parser = BasketballDataParser(url)

	# Continuous monitoring loop
	try:
		while True:
			parser.process_data()
			time.sleep(0.1)  # Add a small delay to prevent excessive CPU usage, oops
	except KeyboardInterrupt:
		print("\nStopping data collection...")

if __name__ == "__main__":
	main()