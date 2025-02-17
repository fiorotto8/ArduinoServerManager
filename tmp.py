import re

def extract_number_from_string(string):
        # Define a regular expression pattern to match the number after a colon
        pattern = r':\s*([-+]?\d*\.\d+|\d+)'  # Matches floating-point or integer numbers
        
        # Search for the pattern in the string
        match = re.search(pattern, string)
        
        if match:
            # Extract the matched number
            number_str = match.group(1)
            
            # Convert the extracted number string to a float
            number = float(number_str)
            return number
        else:
            return None  # Return None if no match found
        

inp = ['Current position: 11.00', 'PANDA']

print(inp[0])

print(extract_number_from_string(inp[0]))