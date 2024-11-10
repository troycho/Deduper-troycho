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
---
10/24/24:
**CIGAR String Function**

```
def findPosition(cig: str, pos: int, strand: str) -> int:
    '''Takes CIGAR string, 1-based leftmost position, and strand ("+" or "-") as inputs. Checks for soft-clipping, insertions, and/or deletions in the CIGAR string and adjusts position accordingly. Returns 5' position of read as int.'''
```

```
if plus strand:
	extract number and letter of item in ciglist[0] --> WRITE EXTRACT FUNCTION
	if letter is S:
		return pos - number
	else:
		return pos

if minus strand:
	for i in range(len(ciglist)):
		extract number and letter of item in ciglist[i] --> WRITE EXTRACT FUNCTION
		if letter is S and i==0:
			continue
		elif letter is S and i==len(ciglist)-1:
			pos += number
		else: 
			pos += number
	return pos - 1 
```

---
10/26/24:
**New draft of pseudocode for main algorithm**
```
# Create set of valid UMIs from text file
umis = {set of 96 UMIs}
# Create dict for storing alignment location
# Keys will be UMI sequences and values will be tuples containing position # and strand
loc = {}

Open output SAM file in write mode

With open input sorted SAM file in read mode and output SAM file in write mode:
	current_chrom = None
	Read in input file one line at a time:
		Write out line and continue to next line if header (starts with @)
		Extract UMI and check if valid
		If UMI is not valid, continue to next line
		Extract chromosome number from line
		If chromosome number != current_chrom:
			Clear the loc dict
			Update current_chrom to the new chromosome number
		Generate alignment tuple
		If alignment tuple is not in loc dict under UMI:
			Write line to output file
			Add alignment tuple to dict

```
With this new algorithm, I will no longer need my "process_lines" function from before.

---
# Running script
Output from SLURM:
```
Number of header lines: 65
Number of wrong UMIs: 0
Number of unique reads: 13719048
Number of duplicates: 4467362
	Command being timed: "./Roychowdhury_deduper.py -f sorted_C1_SE.sam -o realoutput.sam -u STL96.txt"
	User time (seconds): 104.92
	System time (seconds): 3.48
	Percent of CPU this job got: 99%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 1:48.94
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 453536
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 240828
	Voluntary context switches: 884
	Involuntary context switches: 130
	Swaps: 0
	File system inputs: 0
	File system outputs: 0
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
```

Command to count the number of reads associated with each chromosome in the deduplicated sam file:
```
grep -v "^@" realoutput.sam | awk '{print $3}' | sort | uniq -c | awk '{print $2 "\t" $1}' | sort -n -k1 > output.txt
```