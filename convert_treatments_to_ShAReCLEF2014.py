"""
This code convert the automatically annotated treatments to the ShAReCLEF2014 task2 data format.
NOTE: it relies on the output of convert_ShAReCLEF2014_to_WebAnnoTSV3.py to get the token spans.
"""

import os


def read_treatments(treatment_file):
    """
    read in the text automatically labeled with treatment enties,
    and store the text in a dictionary: {text_chunk_id: text_chunk(with treatment annotation)}
    """
    textchunkID2text = {}
    textchunkID = 0
    with open(treatment_file) as f:
        for line in f:
            if line.strip() != "":
                textchunkID += 1
                textchunkID2text[textchunkID] = line
    return textchunkID2text

def read_webannofile(webanno_file):
    """
    read in the webanno_file,
    and store the annotation for each text chunk in a dictionary of lists: {text_chunk_id: list_of_annotation for each token in this text chunk}
    """
    textchunkID2annolist = {}
    with open(webanno_file) as f:
        annolist = []
        for line in f:
            items = line.split("\t")
            if len(items) == 14:
                annolist.append(items)
            else:
                if annolist != []:
                    textchunkID = int(annolist[0][0].strip().split("-")[0])
                    textchunkID2annolist[textchunkID] = annolist
                annolist = []

        if annolist != []:
            textchunkID = int(annolist[0][0].strip().split("-")[0])
            textchunkID2annolist[textchunkID] = annolist
    return textchunkID2annolist

def _get_before_and_treatment_length(textpiece):
    count = 0
    idx = len(textpiece.replace("<treatment>", ""))
    suffixcount = 0
    for i, item in enumerate(textpiece): #11
        if textpiece[i : (i+len("<treatment>"))] == "<treatment>":
            idx = count+len("<treatment>")
            if textpiece[idx:][-1] in ['.', ':', ',', '?', '!', ';']:
                suffixcount = 1
                return count, len(textpiece[idx:])-1, suffixcount
            return count, len(textpiece[idx:]), suffixcount
        else:
            count += 1
    return count, len(textpiece[idx:]), suffixcount

def convert_treatment_to_ShAReCLEF(textchunkID2text, textchunkID2annolist, new_file):
    with open(new_file, "w") as fw:
        for textchunkID, annolist in textchunkID2annolist.items():
            # print(len(annolist))
            text_with_treatments = textchunkID2text[textchunkID]
            startID = int(annolist[0][1].strip().split("-")[0])
            text_list = text_with_treatments.split("</treatment>")

            token_start_end_list = []
            for i, anno in enumerate(annolist):
                token_start = int(anno[1].split("-")[0])
                token_end = int(anno[1].split("-")[-1])
                token_start_end_list.append((token_start, token_end))
            # print(len(token_start_end_list))

            for i, textpiece in enumerate(text_list[:-1]):
                beforeTreatment_length, treatment_length, suffixcount = _get_before_and_treatment_length(textpiece)
                startID = startID + beforeTreatment_length
                endID = startID + treatment_length
                span = str(startID) + "-" + str(endID)
                fw.write(span+"\n")
                startID = endID + suffixcount


def process_one_file(treatment_file, webanno_file, new_file):
    textchunkID2text = read_treatments(treatment_file)
    textchunkID2annolist = read_webannofile(webanno_file)
    convert_treatment_to_ShAReCLEF(textchunkID2text, textchunkID2annolist, new_file)


def process_all_files(treatment_dir, webanno_dir, out_dir):
    for item in os.listdir(treatment_dir):
        if ".txt" in item and item != "07990-021809-DISCHARGE_SUMMARY.txt":
            # we ignore the file 07990-021809-DISCHARGE_SUMMARY.txt because it's almost empty and does not really contain a useful medical record.
            # For file 00098-016139-DISCHARGE_SUMMARY, original line 19 and line 20 are combined to form line 19 in current files, because the ShAReCLEF annotation has a disjoint disorder which cross the original line 19 and line 20.
            prefix = item.split(".")[0]
            treatment_file = os.path.join(treatment_dir, item)
            webanno_file = os.path.join(webanno_dir, prefix+".tsv")
            new_file = os.path.join(out_dir, prefix+".anno")
            if not os.path.exists(webanno_file):
                print(webanno_file)
            process_one_file(treatment_file, webanno_file, new_file)


def main():
    treatment_dir = "../treatments/"
    webanno_dir = "../ShAReCLEF_in_WebAnnoFormat/"
    out_dir = "../treatments_in_ShAReCLEF_format/"
    os.makedirs(out_dir, exist_ok=True)

    process_all_files(treatment_dir, webanno_dir, out_dir)


if __name__ == "__main__":
    main()