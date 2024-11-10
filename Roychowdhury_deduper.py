#!/usr/bin/env python3
import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(description="Deduplicate reads in sorted SAM file")
    parser.add_argument("-f", "--file", help="Absolute path to input sorted SAM file (sorted by chromosome)")
    parser.add_argument("-o", "--outfile", help="Absolute path to output deduplicated and sorted SAM file")
    parser.add_argument("-u", "--umi", help="File containing list of UMIs")
    return parser.parse_args()


def breakCigar(cigar: str) -> tuple:
    '''Takes one part of CIGAR string consisting of number followed by letter and returns
    tuple with number and letter.'''
    match = re.match(r'(\d+)([M,D,N,I,S])', cigar)
    try:
        number = int(match.group(1))
        letter = match.group(2)
        return number, letter
    except:
        raise Exception("Not a valid CIGAR string")

def findPosition(cigar: str, pos: int, strand: str) -> int:
    '''Takes CIGAR string, 1-based leftmost position, and strand ("+" or "-") as inputs.
    Adjusts position according to characters in CIGAR string. Returns 5' position of read as int.'''
    ciglist: list = re.findall(r"\d*[M,D,N,S]{1}", cigar)
    if strand == "+":
        number, letter = breakCigar(ciglist[0])
        if letter == "S":
            return pos - number
        else:
            return pos
    elif strand == "-":
        for i in range(len(ciglist)):
            number, letter = breakCigar(ciglist[i])
            if letter == "S" and i == 0: #if there's softclipping at the 3' end
                continue
            elif letter == "S" and i == len(ciglist)-1: #if there's softclipping at the 5' end
                pos += number
            else: #if there's an M, D, or N
                pos += number
        return pos - 1

    else:
        return -1 #return negative number if strand info is not in correct format
 
def checkUMI(umi: str, umiset: set) -> bool:
    '''Takes UMI string and UMI set as inputs and checks if string is in the set. Returns True
    if it is, otherwise returns False.'''
    if umi in umiset:
        return True
    else:
        return False

def returnStrand(bitflag: int) -> str:
    '''Takes bitwise flag as integer input and returns the strand the read is on as "+" for plus/sense
    or "-" as minus/antisense.'''
    if ((bitflag & 16) == 16):
        return "-"
    else:
        return "+"

def getAlignment(line: str) -> tuple:
    '''Takes line in SAM file as string input. Gets 5' position and strand info
    and returns values in a tuple.'''
    fields: list = line.split()
    bitflag: int = int(fields[1]) #bitwise flag
    cigar: str = fields[5] #CIGAR string
    leftpos: int = int(fields[3]) #1-based leftmost mapping position
    strand: str = returnStrand(bitflag)
    pos = findPosition(cigar, leftpos, strand) #5' mapping position
    if pos < 0:
        raise RuntimeError("Invalid 5' position calculated")
    else:
        return (pos, strand)

def main():
    header_lines: int = 0 #number of header lines
    bad_umis: int = 0 #number of invalid umis
    dupli_count: int=0 #number of duplicates
    unique: int = 0 #number of unique reads
    args = get_args()
    umis: set = set() 
    with open(args.umi, "r") as fh: #store valid UMIs from text file in set
        for line in fh:
            line = line.strip()
            umis.add(line)

    # Create dict for storing alignment location
    # Keys will be UMI sequences and values will be sets of tuples containing 5' position and strand
    loc: dict[str, set] = {}

    with open(args.file, "r") as fh, open(args.outfile, "w") as wf:
        current_chrom: str = ""
        for line in fh:
            line = line.strip()
            if line.startswith("@"):
                wf.write(f"{line}\n")
                header_lines += 1
                continue
            fields: list = line.split("\t")
            umi: str = fields[0].split(":")[-1] #extract UMI from QNAME
            if checkUMI(umi, umis) == False: #if not valid UMI
                bad_umis += 1
                continue
            chrom: str = fields[2] #chromosome number
            if chrom != current_chrom:
                loc.clear()
                current_chrom = chrom
            alignment: tuple = getAlignment(line) #get 5' position and strand
            if umi not in loc: #if UMI not encountered previously
                loc[umi] = {alignment}
                wf.write(f"{line}\n")
                unique += 1
            else: #if UMI was encountered already
                if alignment not in loc[umi]: #only write the line if the position is not in dict
                    wf.write(f"{line}\n")
                    loc[umi].add(alignment)
                    unique += 1
                else:
                    dupli_count += 1
    # Report number of header lines, invalid UMIs, unique reads, and removed duplicates
    print(f"Number of header lines: {header_lines}")
    print(f"Number of wrong UMIs: {bad_umis}")
    print(f"Number of unique reads: {unique}")
    print(f"Number of duplicates: {dupli_count}")




if __name__ == "__main__":
    main()
    # print(getAlignment("NS500451:154:HWKTMBGXX:1:11101:24260:1121:CTGTTCAC	0	2	76814284	36	71M	*	0	0	TCCACCACAATCTTACCATCCTTCCTCCAGACCACATCGCGTTCTTTGTTCAACTCACAGCTCAAGTACAA	6AEEEEEEAEEAEEEEAAEEEEEEEEEAEEAEEAAEE<EEEEEEEEEAEEEEEEEAAEEAAAEAEEAEAE/	MD:Z:71	NH:i:1	HI:i:1	NM:i:0	SM:i:36	XQ:i:40	X2:i:0	XO:Z:UU"))
    # print(findPosition("7M", 1, "-")) #7
    # print(findPosition("2M1D2M1I2M", 1, "+")) #1
    # print(findPosition("5M2S", 1, "-")) #7
    # print(findPosition("2S2M3S", 3, "-")) #7
    # print(findPosition("2S5M1I3=5X2M1S", 3, "-")) #10