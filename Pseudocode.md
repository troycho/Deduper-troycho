# Problem 
PCR duplicates arise from the PCR amplification step during library preparation, which is a problem because they can affect the type of analysis we wish to conduct. Our goal is to remove these artificial duplicates after aligning the reads to a reference genome. The definition of a PCR duplicate is that it has the same chromosome number, position number, same UMI, and is on the same strand as another sequence in the SAM file.  

*Inputs:* sorted SAM file (sorted by chromosome); list of UMIs
*Output:* deduplicated sorted SAM file 

# Algorithm Pseudocode
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
		Write line to output if it's a header line (starts with @), then continue to next line in file
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

# High level functions
```
def findPosition(cig: str, pos: int, strand: str) -> int:
    '''Takes CIGAR string, 1-based leftmost position, and strand ("+" or "-") as inputs. Checks for soft-clipping, insertions, and/or deletions in the CIGAR string and adjusts position accordingly. Returns "true position" of read as int.'''

Input: "2S12M", 20, "+"
Output: 18
```

```
def checkUMI(umi: str) -> bool:
    '''Takes UMI string as input and checks if it's in the set of valid UMIs. Returns True if it is, otherwise returns False.'''

Input: "ACTGTCAT"
Output: False
```

```
def parseStrand(bitflag: int) -> str:
	'''Takes bitwise flag as integer and returns the strand the read is on as "+" for forward/sense 
	or "-" as reverse/antisense.'''

Input: 16
Output: "-"
```

```
def getAlignment(line: str) -> tuple:
	'''Takes line in SAM file as string input. Extracts position and strand info and returns values in a tuple. Calls the findPosition
	and parseStrand functions.'''

Input: "NS500451:154:HWKTMBGXX:1:11101:24260:1121:CTGTTCAC	0	2	76814284	36	71M	*	0	0	TCCACCACAATCTTACCATCCTTCCTCCAGACCACATCGCGTTCTTTGTTCAACTCACAGCTCAAGTACAA	6AEEEEEEAEEAEEEEAAEEEEEEEEEAEEAEEAAEE<EEEEEEEEEAEEEEEEEAAEEAAAEAEEAEAE/	MD:Z:71	NH:i:1	HI:i:1	NM:i:0	SM:i:36	XQ:i:40	X2:i:0	XO:Z:UU"
Output: (76814284, "+")
```

```
def process_lines(chromolines: list) -> None:
	'''Takes a list of SAM file lines for a particular chromosome. Iterates through list and generates an alignment position tuple for each line with the getAlignment function. Uses loc dict to store UMIs and alignment location in key-value pairs and uses the dict to check for PCR duplicates. Ultimately, this function writes all lines that are not PCR duplicates to the output file. Returns None.'''
```