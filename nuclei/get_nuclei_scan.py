import os
import json
import subprocess
import re

def remove_ansi_escape_codes(text):
    """Remove ANSI escape codes from the given text."""
    ansi_escape = re.compile(r'\x1B\[[0-9;]*[mK]')
    return ansi_escape.sub('', text)

def update_nuclei_results(input_file, output_file, target):
    """Process nuclei results from the input file and save to the output JSON file."""
    nuclei_results = []
    with open(input_file, 'r') as f:
        for line in f:
            # Remove bold and color text using the custom function
            line = remove_ansi_escape_codes(line)
            parts = line.strip().split(' ', 4)
            if len(parts) < 4:  # Handle cases where there might be less than 4 parts
                continue  # Skip this line
            result = {
                "detect_engine": parts[0][1:-1],  # Remove the first and last character
                "type": parts[1][1:-1],
                "severity": parts[2][1:-1],
                "url": parts[3][::],
                "response": parts[4][1:-1] if len(parts) > 4 else "null",
                "target": target  # Add the target key with the provided URL
            }
            nuclei_results.append(result)

    with open(output_file, 'w') as f:
        for result in nuclei_results:
            json.dump(result, f)
            f.write('\n')

def process_targets(targets_file, templates_dir):
    """Process each target and create/update JSON files with nuclei results."""
    targets = []
    with open(targets_file, 'r') as f:
        targets = [line.strip().split('://')[1] for line in f]

    # Define the output directory
    output_directory = '/var/log/nuclei'

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for target in targets:
        # Construct the output file path
        output_file = f"{target.replace('.', '_')}.json"

        # Remove previous JSON file if it exists
        if os.path.exists(output_file):
            os.system("rm -f /var/log/nuclei/*.json")

        # Run the nuclei command and update results
        subprocess.run(['go/bin/nuclei', '-target', f'https://{target}', '-t', templates_dir, '-silent', '-no-mhe'],
                       stdout=open(f"{target}.txt", 'w'))
        update_nuclei_results(f"{target}.txt", output_file, target)  # Pass the current target to the function

        # Delete the temporary text file
        os.remove(f"{target}.txt")
         # Add scan results to output directory
        os.system("cat {0} > {1}/report.json".format(output_file, output_directory))
        os.system("sleep 60.0")
        os.system("rm -f {}".format(output_file))
        os.system("sleep 30.0")

if __name__ == "__main__":
    targets_file = "urls.txt"
    templates_dir = "/root/nuclei-templates"
    process_targets(targets_file, templates_dir)
