"""
The ShAReCLEF2014 data has line breaks in the middle of sentences.
This is the code to merge such lines.
"""

import os

def renumbering(new_textlist):
    oldID2newID = {}
    for i, new_text in enumerate(new_textlist):
        sentID = str(i+1)
        for j in range(1, len(new_text)):
            tokenID = str(j)
            newID = sentID + "-" + tokenID
            current_line = new_text[j]
            items = current_line.split("\t")
            oldID2newID[items[0]] = newID
            items[0] = newID
            new_text[j] = "\t".join(items)

    for i, new_text in enumerate(new_textlist):
        for j in range(1, len(new_text)):
            current_line = new_text[j]
            items = current_line.split("\t")
            if items[12][0].isdigit():
                relIDlist = items[12].split("|")
                new_relIDlist = []
                for relID in relIDlist:
                    if "[" in relID:
                        oldID, numID = relID.split("[")
                        relID = oldID2newID[oldID] + "[" + numID
                    else:
                        relID = oldID2newID[relID]
                    new_relIDlist.append(relID)
                items[12] = "|".join(new_relIDlist)
            new_text[j] = "\t".join(items)
    return new_textlist



def combine_lines(textlist):
    new_textlist = []
    i = 0
    new_text = []
    last_merged = False
    while i < len(textlist):
        current_text = textlist[i]
        if new_text == []:
            new_text = current_text

        if i == len(textlist) - 1:
            if not last_merged:
                new_textlist.append(current_text)
        else:
            next_text = textlist[i+1]
            current_last_token = current_text[-1].strip().split("\t")[2][-1]
            next_first_token = next_text[1].strip().split("\t")[2][0]
            if current_last_token != "." and next_first_token.islower():
                new_text[0] = new_text[0][:-1] + " " + next_text[0][6:]
                new_text.extend(next_text[1:])
                if i+1 == len(textlist) - 1:
                    last_merged = True
            else:
                new_textlist.append(new_text)
                new_text = []
        i += 1

    new_textlist = renumbering(new_textlist)

    print(len(textlist), len(new_textlist))
    # for i, line in enumerate(new_textlist):
    #     print(i+1, line)
    # print(new_textlist)

    return new_textlist

def process_one_file(fname, foutname):
    with open(fname) as f, open(foutname, "w") as fw:
        lines = [line for line in f]
        for line in lines[:5]:
            fw.write(line)

        textlist = [[]]
        for line in lines[5:]:
            if line.strip() == "":
                textlist.append([])
            else:
                textlist[-1].append(line)

        new_textlist = combine_lines(textlist)
        for i, textlist in enumerate(new_textlist):
            for line in textlist:
                fw.write(line)
            if i != len(new_textlist) - 1:
                fw.write("\n")

def main():
    datadir = "../disorder_and_treatments"
    outdir = "../disorder_and_treatments_lineCombined"
    os.makedirs(outdir, exist_ok=True)
    filelist = []
    for item in os.listdir(datadir):
        filelist.append(item)
    filelist.sort()
    # filelist = ["00098-016139-DISCHARGE_SUMMARY.tsv"]
    # filelist = ["15295-348292-RADIOLOGY_REPORT.tsv"]
    for file in filelist:
        print(file)
        fname = os.path.join(datadir, file)
        foutname = os.path.join(outdir, file)
        process_one_file(fname, foutname)

if __name__ == "__main__":
    main()