import sys
import urllib.request
import time
from tqdm import tqdm
from xml.etree import ElementTree

# Define the base URL for the NCBI E-utilities API
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Define the search term to use for the API query
search_term = "Homo sapiens[Organism] AND {}[Gene Name]"

# Define the delay between each request
delay = 1 # in seconds

if len(sys.argv) < 3:
    print("Please provide input file as argument 1 and output file as argument 2")
    sys.exit(1)
	
# Get the input and output file paths from the command line arguments
input_file_path = sys.argv[1]
output_file_path = sys.argv[2]

# Read the gene names from the input file
with open(input_file_path, "r") as file:
    gene_names = [line.strip() for line in file]

# Loop over the gene names and retrieve the NCBI gene IDs and summaries for each
gene_data = []
for gene_name in tqdm(gene_names):
    # Construct the API URL for the current gene name
    url = base_url + "esearch.fcgi?db=gene&term=" + urllib.parse.quote_plus(search_term.format(gene_name))
    # Send the API request and parse the response XML
    response = urllib.request.urlopen(url).read()
    root = ElementTree.fromstring(response)
    # Extract the list of gene IDs from the response XML
    id_list = root.find("IdList")
    if id_list is not None and len(id_list) > 0:
        gene_id = id_list[0].text
        # Construct the API URL for the current gene ID
        url = "https://www.ncbi.nlm.nih.gov/gene/" + gene_id + "?report=full_report"
        # Send the API request and parse the response HTML
        response = urllib.request.urlopen(url).read().decode("utf-8")
        # Extract the gene summary from the response HTML
        summary_start = response.find("<dt>Summary</dt>")
        if summary_start != -1:
            summary_start = response.find("<dd>", summary_start) + len("<dd>")
            summary_end = response.find("</dd>", summary_start)
            summary = response[summary_start:summary_end].strip()
        else:
            summary = "Not found"
        # Add the gene name, ID, and summary to the list
        gene_data.append((gene_name, gene_id, summary))
    # Delay before sending the next request
    time.sleep(delay)

# Write the gene data to the output file
with open(output_file_path, "w") as file:
    for gene_name, gene_id, summary in gene_data:
        file.write(gene_name + "\t" + summary + "\n")

