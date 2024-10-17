# Part 1 - Pseudocode

10/11/24:<br>
*Problem*: PCR duplicates arise from the PCR amplification step during library preparation, which is a problem because they can affect the type of analysis we wish to conduct. Our goal is to remove these artificial duplicates after aligning the reads to a reference genome. The definition of a PCR duplicate is that it has the same chromosome number, position number, same UMI, and is on the same strand as another sequence in the SAM file.  

*Inputs:* sorted SAM file (sorted by chromosome); list of UMIs
*Output:* deduplicated sorted SAM file  

*Examples to include in test SAM file (tab-delimited):*
- Same exact entry (PCR duplicate)
- Non-duplicates with everything the same except UMI
- PCR duplicate with soft-clipping
- Non-duplicate with soft-clipping
- Different chromosome number entries
- Non-duplicates with same UMI and chromosome number but not same position # and strand
- Invalid UMI
- insertions
- deletions

<br>*Possible useful functions:*
- argparse
- left_position function that adjusts for soft-clipping
- extract UMI from header and check if it's in the list of known UMIs
- parse for strand info and return "+" or "-"
- generate alignment position tuple
	- will use the adjust position for soft-clipping and parse for strand info functions
- process chromosome lines in list

**First draft of pseudocode:**
```
# Create set of valid UMIs from text file
umis = {set of 96 UMIs}
# Create dict for storing alignment location
# Keys will be UMI sequences and values will be tuples containing position # and strand
loc = {}

Open output SAM file in write mode

With open input sorted SAM file in read mode:
	current_chrom = None
	chrom_lines = []
	Read in input file one line at a time:
		Continue to next line if header (starts with @)
		Extract UMI and check if valid
		If UMI is not valid, continue to next line
		Extract chromosome number from line
		If chromosome number != current_chrom:
			Process lines in chrom_lines if list is not empty (see process_lines function)
			Clear the loc dict
			Clear chrom_lines
			Update current_chrom to the new chromosome number
		Append line to chrom_lines
	If chrom_lines not empty, process lines

Close output file handle

```

- [ ] **Question:** if soft-clipping occurs at the right end of a read, how do we adjust the position of the read?