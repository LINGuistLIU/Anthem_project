"""
This code converts the disorder and disorder negation annotation in ShAReCLEF2014 task 2 data into "WebAnno TSV v3.2 (WebAnno v3.x)" format.
"""

import os
from convert_ShAReCLEF2014_to_WebAnnoTSV3 import data_reader, \
                                                 example_data_reader, \
                                                 ShAReCLEF2WebAnnoTSV, \
                                                 reformat_tsv, \
                                                 add_negate_relation, \
                                                 add_disjoin_span_relation


def read_treatment_span(treatment_span_file):
    treatment_span_list = []
    with open(treatment_span_file) as f:
        for line in f:
            startID, endID = line.strip().split("-")
            treatment_span_list.append((int(startID), int(endID)))
    return treatment_span_list

def add_treatments_entities(treatment_span_file, webanno_file, new_file):
    treatment_span_list = read_treatment_span(treatment_span_file)
    with open(webanno_file) as f, open(new_file, "w") as fw:
        for line in f:
            items = line.split("\t")
            if len(items) == 13:
                for startID, endID in treatment_span_list:
                    token_start, token_end = items[1].strip().split("-")
                    token_start = int(token_start)
                    token_end = int(token_end)
                    if token_start >= startID and token_end <= endID:
                        if items[4] == "_":
                            print("adding treatment")
                            items[4] = "treatment"
                            items[3] = "*"
                            # items[5] = "*"
                fw.write("\t".join(items))
            else:
                fw.write(line)


def process_one_file(fname, title_list, anno_dir, corpus_dir, treatment_span_dir, outdir):
    prefix = fname.strip().split(".")[0]

    fname_anno = os.path.join(anno_dir, fname)
    annodict_list = data_reader(fname_anno, title_list)

    fname_in = os.path.join(corpus_dir, prefix+".txt")

    fname_out_tmp = os.path.join(outdir, prefix+".tmp")
    ShAReCLEF2WebAnnoTSV(annodict_list=annodict_list, fname_in=fname_in, fname_out=fname_out_tmp)

    treatment_span_file = os.path.join(treatment_span_dir, prefix+".anno")
    ftreatment_added = os.path.join(outdir, prefix + ".treatment")
    add_treatments_entities(treatment_span_file, fname_out_tmp, ftreatment_added)

    fname_out = os.path.join(outdir, prefix)
    reformat_tsv(ftreatment_added, fname_out)

    add_negate_relation(fname_out)

    add_disjoin_span_relation(fname_out+".negate")


def process_all_file(title_list, anno_dir, corpus_dir, treatment_span_dir, outdir):
    file_count = 0
    exclude_list = []
    for fname in os.listdir(anno_dir):
        if ".pipe" in fname:
            file_count += 1
            fname_anno = os.path.join(anno_dir, fname)
            prefix = fname.strip().split(".")[0]
            fname_in = os.path.join(corpus_dir, prefix + ".txt")
            # current_text = corpus_reader(fname_in)

            fname_out_tmp = os.path.join(outdir, prefix + ".tmp")
            annodict_list = data_reader(fname_anno, title_list)
            ShAReCLEF2WebAnnoTSV(annodict_list=annodict_list, fname_in=fname_in, fname_out=fname_out_tmp)

            treatment_span_file = os.path.join(treatment_span_dir, prefix+".anno")
            if os.path.exists(treatment_span_file):
                ftreatment_added = os.path.join(outdir, prefix+".treatment")
                add_treatments_entities(treatment_span_file, fname_out_tmp, ftreatment_added)
            else:
                ftreatment_added = fname_out_tmp

            # fname_out = os.path.join(outdir, prefix + ".tsv")
            fname_out = os.path.join(outdir, prefix)
            reformat_tsv(fname_in=ftreatment_added, fname_out=fname_out)
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

    treatment_span_dir = "../treatments_in_ShAReCLEF_format/"

    # outdir = "../output_data/"
    outdir = "../ShAReCLEF_in_WebAnnoFormat/"
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
    #                  treatment_span_dir=treatment_span_dir,
    #                  outdir=outdir)

    process_all_file(title_list=title_list,
                     anno_dir=annodir,
                     corpus_dir=corpusdir,
                     treatment_span_dir=treatment_span_dir,
                     outdir=outdir)




if __name__ == "__main__":
    main()

