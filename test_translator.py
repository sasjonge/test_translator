import re
import json


def parse_to_json_structure(input_str):
    # Clean input by removing unnecessary whitespace and newlines
    input_str = input_str.replace("\n", "").replace("\t", "").strip()

    # Mapping patterns for keywords to their JSON-like names
    patterns = {
        r'an Action': "anAction",
        r'an Object': "anObject",
        r'a Location': "anLocation",
        r'the Location': "theLocation",
        r'the Object': "theObject",
        r'the Action': "theAction"
    }

    # Recursive function to parse nested structures
    def parse_nested(content):
        # Determine if content has any of the patterns
        for pattern, json_key in patterns.items():
            match = re.search(f"{pattern}\\s*\\((.*)\\)", content)
            if match:
                inner_content = match.group(1)
                elements = split_elements(inner_content)

                # Build the nested structure dictionary
                result_dict = {}
                for element in elements:
                    if "=" in element:
                        key, value = map(str.strip, element.split("=", 1))

                        # Recursively check if the value is a nested structure
                        if any(re.search(pat, value) for pat in patterns):
                            result_dict[key] = parse_nested(value)
                        else:
                            # Clean up any extraneous parentheses or quotes at the end of values
                            result_dict[key] = value.strip('"').strip(")")
                    else:
                        result_dict[element] = None  # Handle standalone keys without values

                return {json_key: [result_dict]}

        return content  # Return content if no patterns match (base case)

    # Helper function to handle nested element splitting
    def split_elements(inner_content):
        elements = []
        bracket_level = 0
        current_element = ""
        in_quotes = False  # Track if we are inside quotes to avoid splitting within strings
        
        for char in inner_content:
            if char == '"':
                in_quotes = not in_quotes
            elif char == "(" and not in_quotes:
                bracket_level += 1
            elif char == ")" and not in_quotes:
                bracket_level -= 1
            
            if char == "," and bracket_level == 0 and not in_quotes:
                elements.append(current_element.strip())
                current_element = ""
            else:
                current_element += char

        if current_element:
            elements.append(current_element.strip())
        
        return elements

    # Start parsing the entire string
    return json.dumps(parse_nested(input_str), indent=4)


def remove_entity_wrapper(input_str):
    # Regular expression to match 'entity(' at the beginning and ')' at the end
    pattern = r'^entity\s*\((.*)\)$'
    
    # Remove newlines and extra spaces for easier processing
    input_str = ' '.join(input_str.split())
    
    # Use regex to find and extract the inner content of the entity
    match = re.match(pattern, input_str)
    
    if match:
        return match.group(1)
    else:
        return input_str  # If 'entity(...)' is not found, return original string


# Test the function with your string
input_str = '''
an Action (
    type="Transporting",
    objectActedOn=( an Object(
            type="Milk",
            location = a Location(
                storagePlace="?storagePlace",
                spatialRelation="?spatialRelation"))),
    target=(the Location(
                targetObject=an Object(
                    name="Table1")
                )
    )
)
'''

output_str = remove_entity_wrapper(input_str)
print(output_str)

output_json = parse_to_json_structure(output_str)
print(output_json)