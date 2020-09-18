"""
This code converts the disorder and disorder negation annotation in ShAReCLEF2014 task 2 data into "WebAnno TSV v3.2 (WebAnno v3.x)" format.
"""

import os
from nltk.tokenize import word_tokenize

def example_data_reader(fname):
    itemlist = []
    with open(fname) as f:
        for line in f:
            items = line.strip().split("|")
            for item in items:
                item = item.strip()
                if item != "":
                    itemlist.append(item)
    return itemlist

def data_reader(fname, title_list):
    allAnno = []
    with open(fname) as f:
        for line in f:
            items = line.strip().split("|")
            allAnno.append(dict(zip(title_list, items)))
    return allAnno

def corpus_reader(fname):
    text = ""
    with open(fname) as f:
        for line in f:
            text += line
    return text


def ShAReCLEF2WebAnnoTSV(annodict_list, fname_in, fname_out):
    """
    Get spans for disorders and disorder negations from ShAReCLEF2014 data.
    """
    id2disorder = {}
    id2negation = {}
    negationSpan2label = {}
    negationSpan2polarity = {}
    for i, item in enumerate(annodict_list):
        disorder_idx_list = item['DD Spans'].split(",")
        negation_value = item['Cue NI']
        # print(disorder_idx_list, negation_value)
        for disorder_idx in disorder_idx_list:
            id2disorder[disorder_idx] = "disorders"
            if negation_value != "null":
                id2negation[disorder_idx] = "negative"
            else:
                id2negation[disorder_idx] = "*"
        if negation_value != "null":
            negationSpan2label[negation_value] = "disorder\_negation\_indicator"
            negationSpan2polarity[negation_value] = "*"
    # for k, v in id2disorder.items():
    #     print(k, v, id2negation[k])


    whole_string = corpus_reader(fname_in)
    letterlist = [item for item in whole_string]

    with open(fname_in) as f, open(fname_out, "w") as fw:
        fw.write("#FORMAT=WebAnno TSV 3.2" + "\n")
        fw.write("#T_SP=webanno.custom.Anthementities|polarity|span_type" + "\n")
        fw.write("#T_RL=webanno.custom.Anthemrelations|affects|brings_about|functionally_related|relation_polarity|relation_type|temporally_related|BT_webanno.custom.Anthementities" + "\n")
        # fw.write("\n")
        # fw.write("\n")
        line_list = f.readlines()
        start_idx = 0
        end_idx = 0
        # tract_print = 0
        sent_id = 0
        for i, line in enumerate(line_list):
            # tract_print += 1
            if line.strip() != "":
                fw.write("\n\n#Text="+line.replace("\t", " "))
                line_tokenized_temp = word_tokenize(line)
                # line_tokenized = line_tokenized_temp
                line_tokenized = []
                for item in line_tokenized_temp:
                    if item == "''":
                        # print(item)
                        item = '"'
                    if item == '``':
                        item = '"'

                    if len(item) > 1 and item[0] == "-": # for file 15751-026988-DISCHARGE_SUMMARY.txt
                        line_tokenized.append("-")
                        item = item[1:]

                    if "/" in item:
                    # if item == "R/G/M":
                        slashedItems = item.strip().split("/")
                        # if len(slashedItems[0]) > 1 or slashedItems[0].isupper():
                        if item[-1] != "/":
                            for slashed_count, slashedItem in enumerate(slashedItems):
                                if slashedItem.strip() != "":
                                    line_tokenized.append(slashedItem)
                                    if slashed_count != len(slashedItems) - 1:
                                        line_tokenized.append("/")
                        else:
                            line_tokenized.append(item)
                    elif "+MR" in item: # for file 16994-022078-DISCHARGE_SUMMARY.txt
                        item = item.replace("+MR", " + MR")
                        items_now = item.split(" ")
                        for item_now in items_now:
                            line_tokenized.append(item_now)
                    elif "non-" in item: # for file 10539-022213-DISCHARGE_SUMMARY.txt
                        item = item.replace("non-", "non - ")
                        items_now = item.split(" ")
                        for item_now in items_now:
                            line_tokenized.append(item_now)
                    elif item == "sx-free": # for file 20389-024150-DISCHARGE_SUMMARY.txt
                        items_split = item.split("-")
                        line_tokenized.append(items_split[0])
                        line_tokenized.append("-")
                        line_tokenized.append(items_split[1])
                    elif item == "extra-axial": # to account for file 05382-010331-DISCHARGE_SUMMARY.txt
                        line_tokenized.append("extra")
                        line_tokenized.append("-")
                        line_tokenized.append("axial")
                    elif item == "intra-": # to account for file 05382-010331-DISCHARGE_SUMMARY.txt
                        line_tokenized.append("intra")
                        line_tokenized.append("-")
                    elif item == "ABD-": # for file 25775-007416-DISCHARGE_SUMMARY.txt
                        line_tokenized.append("ABD")
                        line_tokenized.append("-")
                    elif item == "material.There": # for file 10907-103779-ECHO_REPORT.txt
                        line_tokenized.append("material")
                        line_tokenized.append(".")
                        line_tokenized.append("There")
                    elif item == "MR.": #for file 12125-022364-DISCHARGE_SUMMARY.txt
                        line_tokenized.append("MR")
                        line_tokenized.append(".")
                    else:
                        line_tokenized.append(item)
                sent_id += 1
                # print(sent_id)
                # print(line_tokenized)
                for j, word in enumerate(line_tokenized):
                    print(word)
                    word_id = j + 1
                    # 1A. sent_word_id
                    # 2B. word span
                    # 3C. word
                    # 4D. polarity of entity, negative if annotated, else *
                    # 5E. entity name if present, else _
                    # 6F. _ if no relation is annotated in the same row, else *
                    # 7G. _ if no relation is annotated in the same row, else *
                    # 8H. _ if no relation is annotated in the same row, else *
                    # 9I. _ if no relation is annotated in the same row, else *
                    # 10J. relation type if annotated, else _
                    # 11K. polarity of relation. _ if no relation is annotated in the same row, else *
                    # 12L. id of related argument if a relation is annotated in the same row, else _
                    # 13M. empty

                    ## 1. sent_word_id
                    sent_word_id = str(sent_id)+"-"+str(word_id)

                    ## 2. word span
                    # print(i, j, len(line_tokenized), len(letterlist))
                    print(">>>", word, i, j, len(line_tokenized), len(letterlist))
                    while letterlist[0] != word[0]:
                        # print(">>>", letterlist[0], word[0])
                        start_idx += 1
                        letterlist.pop(0)
                        print(">>>", word, i, j, len(line_tokenized), len(letterlist))
                    end_idx = start_idx + len(word)
                    current_start_end_id = str(start_idx)+"-"+str(end_idx)


                    ## 4. polarity of entity
                    ## 5. entity name
                    entity_name = "_"
                    entity_polarity = "_"
                    disorder_exist = False
                    for disorder_idx in id2disorder.keys():
                        disorder_start, disorder_end = disorder_idx.strip().split("-")
                        disorder_start = int(disorder_start)
                        disorder_end = int(disorder_end)
                        if start_idx >= disorder_start and end_idx <= disorder_end:
                            entity_name = id2disorder[disorder_idx]
                            entity_polarity = id2negation[disorder_idx]
                            disorder_exist = True
                            print(disorder_idx, current_start_end_id, entity_name, entity_polarity)

                    for negationSpan in negationSpan2label.keys():
                        negation_start, negation_end = negationSpan.strip().split("-")
                        negation_start = int(negation_start)
                        negation_end = int(negation_end)
                        if start_idx >= negation_start and end_idx <= negation_end:
                            entity_name = negationSpan2label[negationSpan]
                            entity_polarity = negationSpan2polarity[negationSpan]
                            print(negationSpan, current_start_end_id, entity_name, entity_polarity)


                    # if entity_name != "_":
                    #     if disorder_exist:
                    #         print(disorder_idx, current_start_end_id, entity_name, entity_polarity)
                    #     else:
                    #         print(negationSpan, current_start_end_id, entity_name, entity_polarity)

                    # print(sent_word_id, current_start_end_id, word, entity_name, entity_polarity)
                    rel_info1 = "_"
                    rel_info2 = "_"
                    rel_info3 = "_"
                    rel_info4 = "_"
                    relation_type = "_"
                    rel_info5 = "_"
                    rel_argID = "_"
                    last_column = ""
                    fw.write("\t".join([sent_word_id, # 1A. sent_word_id
                                        current_start_end_id, # 2B. word span
                                        word, # 3C. word
                                        entity_polarity, # 4D. polarity of entity, negative if annotated, * elif there is entity annotated in the same row, else _
                                        entity_name, # 5E. entity name if present, else _
                                        rel_info1, # 6F. _ if no relation is annotated in the same row, else *
                                        rel_info2, # 7G. _ if no relation is annotated in the same row, else *
                                        rel_info3, # 8H. _ if no relation is annotated in the same row, else *
                                        rel_info4, # 9I. _ if no relation is annotated in the same row, else *
                                        relation_type, # 10J. relation type if annotated, else _
                                        rel_info5, # 11K. polarity of relation. _ if no relation is annotated in the same row, else *
                                        rel_argID, # 12L. id of related argument if a relation is annotated in the same row, else _
                                        last_column])) # 13M. empty
                    if j < len(line_tokenized) - 1:
                        fw.write("\n")
                    delword = len(word)
                    while delword > 0:
                        letterlist.pop(0)
                        start_idx += 1
                        delword -= 1

def reformat_tsv(fname_in, fname_out):
    """
    Add numbering for multi-token entities.
    """
    with open(fname_in) as f:
        line_list = f.readlines()

    with open(fname_out, "w") as fw:
        sentlist = []
        multiword_count = 1
        entity2multiword_count = {}
        for line in line_list:
            items = line.split("\t")
            if len(items) == 1:
                identical_count = 0
                for idx, item in enumerate(sentlist[:-1]):
                    entity = item[4]
                    entity_next = sentlist[idx+1][4]
                    entity_next_span = sentlist[idx+1][1]
                    entity_span = item[1]
                    if entity == entity_next:
                        if entity != "_":
                            entity2multiword_count[entity_span] = multiword_count
                            entity2multiword_count[entity_next_span] = multiword_count
                            identical_count += 1
                    else:
                        if identical_count > 0:
                            multiword_count += 1
                        identical_count = 0
                # to handle the last word is within multi-token entity case
                if identical_count != 0:
                    multiword_count += 1

                for item in sentlist:
                    sent_word_id, \
                    current_start_end_id, \
                    word, \
                    entity_polarity, \
                    entity_name, \
                    rel_info1, \
                    rel_info2, \
                    rel_info3, \
                    rel_info4, \
                    relation_type, \
                    rel_info5, \
                    rel_argID, \
                    last_column = item
                    if current_start_end_id in entity2multiword_count:
                        multiword_entity_index = "["+str(entity2multiword_count[current_start_end_id])+"]"
                        entity_name = entity_name + multiword_entity_index
                        entity_polarity = entity_polarity + multiword_entity_index
                    fw.write("\t".join([sent_word_id,
                                        current_start_end_id,
                                        word,
                                        entity_polarity,
                                        entity_name,
                                        rel_info1,
                                        rel_info2,
                                        rel_info3,
                                        rel_info4,
                                        relation_type,
                                        rel_info5,
                                        rel_argID,
                                        last_column]))
                fw.write(line)
                sentlist = []
            else:
                sentlist.append(items)
        if sentlist != []:
            identical_count = 0
            for idx, item in enumerate(sentlist[:-1]):
                entity = item[3]
                entity_next = sentlist[idx + 1][3]
                entity_next_span = sentlist[idx + 1][1]
                entity_span = item[1]
                if entity == entity_next:
                    if entity != "_":
                        entity2multiword_count[entity_span] = multiword_count
                        entity2multiword_count[entity_next_span] = multiword_count
                        identical_count += 1
                else:
                    if identical_count > 0:
                        multiword_count += 1
                    identical_count = 0

            for item in sentlist:
                sent_word_id, \
                current_start_end_id, \
                word, \
                entity_polarity, \
                entity_name, \
                rel_info1, \
                rel_info2, \
                rel_info3, \
                rel_info4, \
                relation_type, \
                rel_info5, \
                rel_argID, \
                last_column = item
                if current_start_end_id in entity2multiword_count:
                    multiword_entity_index = "[" + str(entity2multiword_count[current_start_end_id]) + "]"
                    entity_name = entity_name + multiword_entity_index
                    entity_polarity = entity_polarity + multiword_entity_index
                fw.write("\t".join([sent_word_id,
                                    current_start_end_id,
                                    word,
                                    entity_polarity,
                                    entity_name,
                                    rel_info1,
                                    rel_info2,
                                    rel_info3,
                                    rel_info4,
                                    relation_type,
                                    rel_info5,
                                    rel_argID,
                                    last_column]))

def add_negate_relation(fname_in, datadir="../../shareclef-ehealth-evaluation-lab-2014-task-2-disorder-attributes-in-clinical-reports-1.0/EvaluationWorkbenchFolderDistribution_2014ShARECLEF/CLEFAnnotationOutputDirectory/"):
    """
    Add negate relation to connect disorder_negation_indicators with the corresponding disorders.
    """
    fname_out = fname_in+".negate"
    fShAReCLEF = os.path.join(datadir, fname_in.split("/")[-1].split(".")[0]+".pipe.txt")
    spanstart2annolist = {}
    spanstart2stID = {}
    spanstart2span = {}
    with open(fname_in) as f:
        for line in f:
            items = line.split("\t")
            if len(items) == 13:
                span_start = items[1].split("-")[0]
                spanstart2span[span_start] = items[1]
                annolist = items[2:]
                spanstart2annolist[span_start] = annolist
                spanstart2stID[span_start] = items[0]

    with open(fShAReCLEF) as fanno:
        for line in fanno:
            items = line.strip().split("|")
            disorder_spanlist = items[1].split(",")
            negation_span = items[4]

            if negation_span != "null":
                negation_span_start = negation_span.split("-")[0]
                target_disorder_span_start = disorder_spanlist[-1].split("-")[0]
                for disorderSpan in disorder_spanlist:
                    if spanstart2annolist[disorderSpan.split("-")[0]][1] == "negative":
                        target_disorder_span_start = disorderSpan.split("-")[0]
                        break
                # target_disorder_span_start = disorder_spanlist[0].split("-")[0]
                update_row = spanstart2annolist[target_disorder_span_start]
                for i, label in enumerate(update_row[3:-1]):
                    i = i + 3
                    if i == 7:
                        spanstart2annolist[target_disorder_span_start][i] = "negate"
                        # print(target_disorder_span_start)
                        # print(spanstart2annolist[target_disorder_span_start])
                    else:
                        spanstart2annolist[target_disorder_span_start][i] = "*"
                slot_ID = spanstart2stID[negation_span_start]

                # in the data, negation_span are always joint. There is not disjoint negation indicator.
                # if len(disorder_spanlist) > 1:
                negID = "0"
                disorderID = "0"
                if "[" in update_row[2]:
                    disorderID = update_row[2].split("[")[-1].replace("]", "")

                negation_span_start_row = spanstart2annolist[negation_span_start]
                if "[" in negation_span_start_row[2]:
                    negID = negation_span_start_row[2].split("[")[-1].replace("]", "")

                if negID == "0" and disorderID == "0":
                    suffix = ""
                else:
                    neg_start = int(negation_span_start)
                    disorder_start = int(target_disorder_span_start)
                    if neg_start < disorder_start:
                        suffix = negID + "_" + disorderID
                    else:
                        suffix = disorderID + "_" + negID
                    suffix = "[" + suffix + "]"
                slot_ID = slot_ID + suffix
                spanstart2annolist[target_disorder_span_start][-2] = slot_ID
                # spanstart2annolist[target_disorder_span_start][-1] = "\n"
                # print(target_disorder_span_start)
                # print(spanstart2annolist[target_disorder_span_start])
    with open(fname_in) as f, open(fname_out, "w") as fw:
        for line in f:
            items = line.split("\t")
            if len(items) == 13:
                stID = items[0]
                span = items[1]
                spanstart = span.split("-")[0]
                annolist = spanstart2annolist[spanstart]
                outlist = [stID, span] + annolist
                # print(outlist)
                fw.write("\t".join(outlist))
            else:
                fw.write(line)

def add_disjoin_span_relation(fname_in, datadir="../../shareclef-ehealth-evaluation-lab-2014-task-2-disorder-attributes-in-clinical-reports-1.0/EvaluationWorkbenchFolderDistribution_2014ShARECLEF/CLEFAnnotationOutputDirectory/"):
    """
    Add disjoin_span_relation to connect the parts of disjoint disorder entities.
    """
    prefix = fname_in.split(".")[:-1]
    prefix = ".".join(prefix)
    fname_out = prefix + ".tsv"
    fShAReCLEF = os.path.join(datadir, fname_in.split("/")[-1].split(".")[0] + ".pipe.txt")
    spanstart2annolist = {}
    spanstart2stID = {}
    spanstart2span = {}
    with open(fname_in) as f:
        for line in f:
            items = line.split("\t")
            if len(items) == 13:
                span_start = items[1].split("-")[0]
                spanstart2span[span_start] = items[1]
                annolist = items[2:]
                spanstart2annolist[span_start] = annolist
                spanstart2stID[span_start] = items[0]

    with open(fShAReCLEF) as fanno:
        processed_spanlist_count = {}
        for line in fanno:
            items = line.strip().split("|")
            disorder_spanlist = items[1].split(",")
            # negation_spanlist = items[4].split(",")
            processed_spanlist_count[','.join(disorder_spanlist)] = processed_spanlist_count.get(','.join(disorder_spanlist), 0) + 1
            # processed_spanlist_count[negation_spanlist] = processed_span_count.get(negation_spanlist, 0) + 1

            if len(disorder_spanlist) > 1 and processed_spanlist_count[','.join(disorder_spanlist)] == 1:
                for i in range(1, len(disorder_spanlist)):
                    prev_start = disorder_spanlist[i-1].split("-")[0]
                    cur_start = disorder_spanlist[i].split("-")[0]
                    update_row = spanstart2annolist[cur_start]

                    existing_rel = spanstart2annolist[cur_start][7]

                    for i, label in enumerate(update_row[3:-2]):
                        i = i + 3
                        if i == 7:
                            if existing_rel != "_":
                                spanstart2annolist[cur_start][i] = "disjoint\_span|" + spanstart2annolist[cur_start][i]
                            else:
                                spanstart2annolist[cur_start][i] = "disjoint\_span"
                            # print(cur_start)
                            # print(spanstart2annolist[cur_start])
                        else:
                            spanstart2annolist[cur_start][i] = "*"
                    slot_ID = spanstart2stID[prev_start]

                    # in the data, negation_span are always joint. There is not disjoint negation indicator.
                    # if len(disorder_spanlist) > 1:
                    prevID = "0"
                    curID = "0"
                    if "[" in update_row[2]:
                        curID = update_row[2].split("[")[-1].replace("]", "")

                    prev_start_row = spanstart2annolist[prev_start]
                    if "[" in prev_start_row[2]:
                        prevID = prev_start_row[2].split("[")[-1].replace("]", "")

                    if prevID == "0" and curID == "0":
                        suffix = ""
                    else:
                        neg_start = int(prev_start)
                        disorder_start = int(cur_start)
                        if neg_start < disorder_start:
                            suffix = prevID + "_" + curID
                        else:
                            suffix = curID + "_" + prevID
                        suffix = "[" + suffix + "]"
                    slot_ID = slot_ID + suffix
                    if existing_rel != "_":
                        spanstart2annolist[cur_start][-2] = slot_ID + "|" + spanstart2annolist[cur_start][-2]
                    else:
                        spanstart2annolist[cur_start][-2] = slot_ID

    with open(fname_in) as f, open(fname_out, "w") as fw:
        for line in f:
            items = line.split("\t")
            if len(items) == 13:
                stID = items[0]
                span = items[1]
                spanstart = span.split("-")[0]
                annolist = spanstart2annolist[spanstart]
                if "negative" in annolist[1] :
                    new_col = "*" + annolist[1][len("negative"):]
                    annolist = annolist[:3] + [new_col] + annolist[3:]
                else:
                    annolist = annolist[:3] + [annolist[1]] + annolist[3:]
                outlist = [stID, span] + annolist
                # print(outlist)
                fw.write("\t".join(outlist))
            else:
                if line.strip() == "#T_SP=webanno.custom.Anthementities|polarity|span_type":
                    line = "#T_SP=webanno.custom.Anthementities|polarity|span_type|span_type_disorders"
                    fw.write(line+"\n")
                else:
                    fw.write(line)
                    

def process_one_file(fname, title_list, anno_dir, corpus_dir, outdir):
    # fname = "07683-016743-DISCHARGE_SUMMARY.pipe.txt"
    # fname = "00098-016139-DISCHARGE_SUMMARY.pipe.txt"
    # fname = "18531-010240-DISCHARGE_SUMMARY.pipe.txt"
    prefix = fname.strip().split(".")[0]

    fname_anno = os.path.join(anno_dir, fname)
    annodict_list = data_reader(fname_anno, title_list)

    fname_in = os.path.join(corpus_dir, prefix+".txt")
    text = corpus_reader(fname_in)

    fname_out_tmp = os.path.join(outdir, prefix+".tmp")
    ShAReCLEF2WebAnnoTSV(annodict_list=annodict_list, fname_in=fname_in, fname_out=fname_out_tmp)

    fname_out = os.path.join(outdir, prefix)
    reformat_tsv(fname_out_tmp, fname_out)

    add_negate_relation(fname_out)

    add_disjoin_span_relation(fname_out+".negate")

    # -------------- disorder entities -------------------#

    # for i, item in enumerate(annodict_list):
    #     span = item['DD Spans']
    #     if "," not in span:
    #         startid, endid = span.strip().split("-")
    #         startid = int(startid)
    #         endid = int(endid)
    #         print(i, '\t', span, '\t', text[startid:endid])

    # -------------- negation of disorder entities -------------------#
    # for i, item in enumerate(annodict_list):
    #     span = item['Cue NI']
    #     if "," not in span and span != "null":
    #         startid, endid = span.strip().split("-")
    #         startid = int(startid)
    #         endid = int(endid)
    #         print(i, '\t', span, '\t', text[startid:endid])

    # ------------- print out everything --------------#
    # for i, item in enumerate(allAnno):
    #     for k, v in item.items():
    #         # print(i, '\t', k, '\t', v)
    #         if "Cue " in k and v != 'null':
    #             print(i, '\t', k, '\t', v)

def process_all_file(title_list, anno_dir, corpus_dir, outdir):
    file_count = 0
    # exclude_list = ["../output_data/18531-010240-DISCHARGE_SUMMARY.tsv",
    #                 "../output_data/20288-027184-DISCHARGE_SUMMARY.tsv",
    #                 "../output_data/08114-027513-DISCHARGE_SUMMARY.tsv",
    #                 "../output_data/05065-011493-DISCHARGE_SUMMARY.tsv",
    #                 "../output_data/12618-027862-DISCHARGE_SUMMARY.tsv"]
    exclude_list = []
    for fname in os.listdir(anno_dir):
        if ".pipe" in fname:
            file_count += 1
            fname_anno = os.path.join(anno_dir, fname)
            prefix = fname.strip().split(".")[0]
            fname_in = os.path.join(corpus_dir, prefix + ".txt")
            # current_text = corpus_reader(fname_in)

            fname_out_tmp = os.path.join(outdir, prefix + ".tmp")
            # fname_out = os.path.join(outdir, prefix + ".tsv")
            fname_out = os.path.join(outdir, prefix)
            annodict_list = data_reader(fname_anno, title_list)
            ShAReCLEF2WebAnnoTSV(annodict_list=annodict_list, fname_in=fname_in, fname_out=fname_out_tmp)
            reformat_tsv(fname_in=fname_out_tmp, fname_out=fname_out)
            print(file_count, '\t', fname_out)
            if fname_out not in exclude_list:
                add_negate_relation(fname_out)
                add_disjoin_span_relation(fname_out + ".negate")



def main():
    # example data
    ftemplate = "../example_data/template"
    fexample = "../example_data/example_template"
    ftask2a = "../example_data/example_task2a_output"
    ftask2b = "../example_data/example_task2b_output"

    title_list = example_data_reader(ftemplate)
    example_list = example_data_reader(fexample)
    task2a_list = example_data_reader(ftask2a)
    task2b_list = example_data_reader(ftask2b)

    # title2example = dict(zip(title_list, example_list))
    # title2taskA = dict(zip(title_list, task2a_list))
    # title2taskB = dict(zip(title_list, task2b_list))

    # real data

    datadir = "../../shareclef-ehealth-evaluation-lab-2014-task-2-disorder-attributes-in-clinical-reports-1.0/EvaluationWorkbenchFolderDistribution_2014ShARECLEF/"

    annodir = os.path.join(datadir, "CLEFAnnotationOutputDirectory")
    corpusdir = os.path.join(datadir, "corpus")
    knowtatordir = os.path.join(datadir, "ShAReTask2TrainingKnowtatorFiles")

    outdir = "../output_data/"
    os.makedirs(outdir, exist_ok=True)

    # process_one_file(fname="00098-016139-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="18531-010240-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="08114-027513-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="12125-022364-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="00381-006281-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="01163-001840-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="05382-010331-DISCHARGE_SUMMARY.pipe.txt",
    # process_one_file(fname="10907-103779-ECHO_REPORT.pipe.txt",
    # process_one_file(fname="25775-007416-DISCHARGE_SUMMARY.pipe.txt",
    #                  title_list=title_list,
    #                  anno_dir=annodir,
    #                  corpus_dir=corpusdir,
    #                  outdir=outdir)

    process_all_file(title_list=title_list,
                     anno_dir=annodir,
                     corpus_dir=corpusdir,
                     outdir=outdir)




if __name__ == "__main__":
    main()

