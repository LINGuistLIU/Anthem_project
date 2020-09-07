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
    id2disorder = {}
    id2negation = {}
    for i, item in enumerate(annodict_list):
        disorder_idx = item['DD Spans']
        negation_value = item['Cue NI']
        if "," not in disorder_idx: # TO BE IMPROVED
            id2disorder[disorder_idx] = "Disease\_disorder"
            if "," not in negation_value and negation_value != "null":
                id2negation[disorder_idx] = "negative"
            else:
                id2negation[disorder_idx] = "*"

    whole_string = corpus_reader(fname_in)
    letterlist = [item for item in whole_string]

    with open(fname_in) as f, open(fname_out, "w") as fw:
        fw.write("#FORMAT=WebAnno TSV 3.2" + "\n")
        fw.write("#T_SP=webanno.custom.AnthemEntities|category|polarity" + "\n")
        fw.write("#T_RL=webanno.custom.AnthemRelations|category|polarity|BT_webanno.custom.AnthemEntities" + "\n")
        # fw.write("\n")
        # fw.write("\n")
        line_list = f.readlines()
        start_idx = 0
        end_idx = 0
        for i, line in enumerate(line_list):
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
                    line_tokenized.append(item)
                sent_id = i + 1
                # print(line_tokenized)
                for j, word in enumerate(line_tokenized):
                    word_id = j + 1
                    # 1. sent_word_id
                    # 2. word span
                    # 3. word
                    # 4. entity name if present, else _
                    # 5. polarity of entity, positive or negative if annotated, else *
                    # /6. relation, in the same row as the tail
                    # /7. polarity of relation
                    # /8. index of the relation head

                    ## 1. sent_word_id
                    sent_word_id = str(sent_id)+"-"+str(word_id)

                    ## 2. word span
                    # print(i, j, len(line_tokenized), len(letterlist))
                    while letterlist[0] != word[0]:
                        # print(">>>", letterlist[0], word[0])
                        start_idx += 1
                        letterlist.pop(0)
                        # print(">>>", word, i, j, len(line_tokenized), len(letterlist))
                    end_idx = start_idx + len(word)
                    current_start_end_id = str(start_idx)+"-"+str(end_idx)

                    ## 4. entity name
                    ## 5. polarity of entity
                    entity_name = "_"
                    entity_polarity = "_"
                    for disorder_idx in id2disorder.keys():
                        disorder_start, disorder_end = disorder_idx.strip().split("-")
                        disorder_start = int(disorder_start)
                        disorder_end = int(disorder_end)
                        if start_idx >= disorder_start and end_idx <= disorder_end:
                            entity_name = id2disorder[disorder_idx]
                            entity_polarity = id2negation[disorder_idx]
                    # print(sent_word_id, current_start_end_id, word, entity_name, entity_polarity)
                    fw.write("\t".join([sent_word_id, current_start_end_id, word, entity_name, entity_polarity, "_", "_", "_"]))
                    if j < len(line_tokenized) - 1:
                        fw.write("\n")
                    delword = len(word)
                    while delword > 0:
                        letterlist.pop(0)
                        start_idx += 1
                        delword -= 1

def reformat_tsv(fname_in, fname_out):
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
                    entity = item[3]
                    entity_next = sentlist[idx+1][3]
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

                for item in sentlist:
                    sent_word_id, current_start_end_id, word, entity_name, entity_polarity, relation, relation_polarity, relation_head = item
                    if current_start_end_id in entity2multiword_count:
                        multiword_entity_index = "["+str(entity2multiword_count[current_start_end_id])+"]"
                        entity_name = entity_name + multiword_entity_index
                        entity_polarity = entity_polarity + multiword_entity_index
                    fw.write("\t".join([sent_word_id, current_start_end_id, word, entity_name, entity_polarity, relation, relation_polarity, relation_head]))
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
                sent_word_id, current_start_end_id, word, entity_name, entity_polarity, relation, relation_polarity, relation_head = item
                if current_start_end_id in entity2multiword_count:
                    multiword_entity_index = "[" + str(entity2multiword_count[current_start_end_id]) + "]"
                    entity_name = entity_name + multiword_entity_index
                    entity_polarity = entity_polarity + multiword_entity_index
                fw.write("\t".join([sent_word_id, current_start_end_id, word, entity_name, entity_polarity, relation,
                                    relation_polarity, relation_head]))

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

    fname_out = os.path.join(outdir, prefix+".tsv")
    reformat_tsv(fname_out_tmp, fname_out)

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
    for fname in os.listdir(anno_dir):
        if ".pipe" in fname:
            file_count += 1
            fname_anno = os.path.join(anno_dir, fname)
            prefix = fname.strip().split(".")[0]
            fname_in = os.path.join(corpus_dir, prefix + ".txt")
            # current_text = corpus_reader(fname_in)

            print(file_count, '\t', fname_in)

            fname_out_tmp = os.path.join(outdir, prefix + ".tmp")
            fname_out = os.path.join(outdir, prefix + ".tsv")
            annodict_list = data_reader(fname_anno, title_list)
            ShAReCLEF2WebAnnoTSV(annodict_list=annodict_list, fname_in=fname_in, fname_out=fname_out_tmp)
            reformat_tsv(fname_in=fname_out_tmp, fname_out=fname_out)


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

    # process_one_file(fname="18531-010240-DISCHARGE_SUMMARY.pipe.txt",
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

