#Ensure all libraries are installed. They can be installed with the following command
#pip install requests tqdm beautifulsoup4 nltk bs4
import csv
import requests
import sys
import time
from operator import itemgetter
from bs4 import BeautifulSoup
from tqdm import tqdm # Import the tqdm module for the progress bar
from nltk.corpus import words
import os

# Check if the input file was provided as a command-line argument
if len(sys.argv) < 2:
    print("Please provide an input file as a command-line argument")
    sys.exit()

input_file = sys.argv[1]

# Create the output file name
base_output_file = 'output_file'
output_file_number = 1
output_file_name = f"{base_output_file}{output_file_number}.txt"

# Check if the output file already exists, and if it does, increment the output file number
while os.path.exists(output_file_name):
    output_file_number += 1
    output_file_name = f"{base_output_file}{output_file_number}.txt"

# Open the input file and read the gene names into a list
gene_names = []
with open(input_file, 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        if len(row) < 1:  # Skip rows with no data
            continue
        gene_name = row[0].strip()
        if not gene_name:  # Skip rows with no gene name
            continue
        gene_names.append(gene_name)

# Perform a PubMed search for each gene name and count the number of results
results = []
for gene_name in tqdm(gene_names): # Use tqdm to create a progress bar for the loop
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=1&term={gene_name}"
    search_response = requests.get(search_url)
    try:
        search_results = search_response.json()
        num_results = int(search_results["esearchresult"]["count"])
    except (KeyError, ValueError):
        num_results = 0
    
    # Check if gene_name is a dictionary word
    dictionary_words = set(words.words())
    if gene_name.lower() in dictionary_words:
        warning = "WARNING: This gene is a dictionary word."
    else:
        warning = ""
    
    results.append((gene_name, num_results, warning))
    time.sleep(1)  # Add a delay of one second between each request to avoid rate limits

# Sort the results by count in descending order
results_sorted = sorted(results, key=itemgetter(1), reverse=True)

# Write the results to the output file
with open(output_file_name, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    for row in results_sorted:
        writer.writerow(row)
        
print(f"Output written to {output_file_name}")
