#!/bin/bash

# This script calls CpG islands from a file with different sequences where each row is sequence name in column 1 and sequence in column 2. This is useful to check for CpG island in Chip-seq peaks. For compatibility with this script, process the Chip-seq peak bedfile with bedtools getfasta (to obtain sequences) and specify the option -tab to produce a tab-delimited file.
# Specify your input file as the first argument (e.g. sh CpG_island_check.sh INPUT.txt)
# Check if the file exists
if [ ! -f $1 ]; then
  echo "Error: input file does not exist."
  exit 1
fi

# Read the input file and extract the second column
# (assuming the columns are separated by whitespace)
# and save the result to a new file
awk '{print $2}' $1 > column2.txt

# Create an empty file to store the results
touch CpG_island_results.txt

# Define the window size and interval
window_size=200
interval=1

# Initialize the line counter
line_number=1

# Read the file line by line
while read line
do
  # Convert the line to uppercase for case-insensitive matching
  line=$(echo $line | tr '[:lower:]' '[:upper:]')

  # Initialize the variables for calculating CpG islands
  observed=0
  expected=0
  gc_content=0

  # Iterate over the sequence with the defined window size and interval
  for ((i=0; i<${#line}-${window_size}; i+=$interval))
  do
    # Extract the window from the sequence
    window=${line:i:window_size}

    # Count the number of Cs and Gs in the window
    c=$(echo $window | grep -o "C" | wc -l)
    g=$(echo $window | grep -o "G" | wc -l)

    # Calculate the expected number of CpGs in the window
    expected=$(echo "$c * $g / $window_size" | bc -l)

    # Count the number of CGs in the window (case-insensitive)
    cg=$(echo $window | grep -oi "CG" | wc -l)

    # Calculate the observed number of CpGs in the window
    observed=$cg

    # Calculate the GC content in the window
    gc_content=$(echo "($c + $g) / $window_size" | bc -l)

    # Check if the window contains a CpG island
    if [ $(echo "$observed/$expected > 0.6" | bc -l) -eq 1 ] && [ $(echo "$gc_content > 0.5" | bc -l) -eq 1 ]; then
      # If the window is a CpG island, print the line number and "yes"
      # to the results file and break from the loop
      echo "$line_number yes" >> CpG_island_results.txt
      break
    fi
  done

  # If no CpG islands were found in the line, print the line number and "no"
  # to the results file
  if [ $(echo "$observed/$expected <= 0.6" | bc -l) -eq 1 ] || [ $(echo "$gc_content <= 0.5" | bc -l) -eq 1 ]; then
    echo "$line_number no" >> CpG_island_results.txt
  fi

  # Increment the line counter
  ((line_number++))
done < column2.txt
