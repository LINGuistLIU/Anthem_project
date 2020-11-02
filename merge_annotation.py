"""
This is the code to merge annotations of multiple versions in the WebAnno TSV v3.2 format.
It is currently used to merge the curated treatment annotations with the disorder annotations from the ShAReCLEF2014 data.
"""

import os

def countlines(fname):
    lines = [line for line in open(fname)]
    while "#Text=" not in lines[0]:
        lines = lines[1:]
    print(len(lines), end="\t")
    return lines

def adjust_relID(relID, tokenID2annodict, current_sent_tokenID, treatment_now=True):
    if relID == "_":
        return None

    target_sentID, target_tokenID = current_sent_tokenID.split("-")
    entity = tokenID2annodict[current_sent_tokenID]["entity"]
    entities = entity.split("|")
    if treatment_now == True:
        entity = entities[0]
    else:
        entity = entities[-1]
    if "[" in entity:
        target_entityID = entity.split("[")[-1][:-1]
    else:
        target_entityID = "0"

    relIDlist = relID.split("|")
    new_relIDlist = []
    for relID in relIDlist:
        source_sent_tokenID = relID.split("[")[0]
        # print(source_sent_tokenID, current_sent_tokenID)
        source_sentID, source_tokenID = source_sent_tokenID.split("-")
        # assert source_sentID == target_sentID
        entity = tokenID2annodict[source_sent_tokenID]["entity"]
        entities = entity.split("|")
        if treatment_now == True:
            entity = entities[0]
        else:
            entity = entities[-1]
        if "[" in entity:
            source_entityID = entity.split("[")[-1][:-1]
        else:
            source_entityID = "0"
        if source_entityID != "0" or target_entityID != "0":
            relID = source_sent_tokenID+"["+source_entityID+"_"+ target_entityID +"]"
        else:
            relID = source_sent_tokenID
        new_relIDlist.append(relID)
    return "|".join(new_relIDlist)


def renumbering(templines, templist):
    multi_token_span = []
    # klist = ["sent_word_id", "word_span", "word", "entity_polarity", "entity", "F6", "G7",
    #               "H8", "I9", "relation", "relation_polarity", "L12", "rel_id", "new_line"]
    klist = ["entity_polarity", "entity", "F6", "G7", "H8", "I9", "relation", "relation_polarity", "L12", "rel_id"]
    partial_klist = ["entity_polarity", "F6", "G7", "H8", "I9", "relation", "relation_polarity", "L12"]
    for idx in templist:
        entitylist = templines[idx]["entity"]
        for item in entitylist:
            if "[" in item and "]" in item:
                if item not in multi_token_span:
                    multi_token_span.append(item)
    print(multi_token_span)
    originalID2newID = {item:i+1 for i, item in enumerate(multi_token_span)}

    for idx in templist:
        entitylist = templines[idx]["entity"]
        if len(entitylist) == 1:
            entity = entitylist[0]
            if "[" in entity:
                entityID = "[" + str(originalID2newID[entity]) + "]"
                entity = entity.split("[")[0] + entityID
            templines[idx]["entity"] = entity

            for k in partial_klist:
                assert len(templines[idx][k]) == 1
                ANNO = templines[idx][k][0]
                if "[" in ANNO:
                    ANNO = ANNO.split("[")[0] + entityID
                templines[idx][k] = ANNO
        else:
            treatment, disorder = entitylist
            if treatment != "_" and disorder != "_":
                if "[" in treatment:
                    treatmentID = "[" + str(originalID2newID[treatment]) + "]"
                    treatment = treatment.split("[")[0] + treatmentID
                if "[" in disorder:
                    disorderID = "[" + str(originalID2newID[disorder]) + "]"
                    disorder = disorder.split("[")[0] + disorderID
                templines[idx]["entity"] = treatment + "|" + disorder

                for k in partial_klist:
                    ANNO = templines[idx][k]
                    if len(ANNO) == 1:
                        # print(k, ANNO)
                        assert "[" not in ANNO[0]
                        templines[idx][k] = ANNO[0]
                    else:
                        treatmentANNO, disorderANNO = ANNO
                        if "[" in treatmentANNO:
                            treatmentANNO = treatmentANNO.split("[")[0] + treatmentID
                        if "[" in disorderANNO:
                            disorderANNO = disorderANNO.split("[")[0] + disorderID
                        templines[idx][k] = treatmentANNO + "|" + disorderANNO
            elif treatment != "_":
                # but disorder == "_"
                if "[" in treatment:
                    treatmentID = "[" + str(originalID2newID[treatment]) + "]"
                    treatment = treatment.split("[")[0] + treatmentID
                templines[idx]["entity"] = treatment

                for k in partial_klist:
                    ANNO = templines[idx][k]
                    if len(ANNO) == 1:
                        treatmentANNO = ANNO[0]
                    else:
                        treatmentANNO, disorderANNO = templines[idx][k]
                        assert disorderANNO == "_"
                    if "[" in treatmentANNO:
                        treatmentANNO = treatmentANNO.split("[")[0] + treatmentID
                    templines[idx][k] = treatmentANNO
            elif disorder != "_":
                # but treatment == "_"
                if "[" in disorder:
                    disorderID = "[" + str(originalID2newID[disorder]) + "]"
                    disorder = disorder.split("[")[0] + disorderID
                templines[idx]["entity"] = disorder

                for k in partial_klist:
                    ANNO = templines[idx][k]
                    if len(ANNO) == 1:
                        disorderANNO = ANNO[0]
                    else:
                        treatmentANNO, disorderANNO = templines[idx][k]
                        assert treatmentANNO == "_"
                    if "[" in disorderANNO:
                        disorderANNO = disorderANNO.split("[")[0] + disorderID
                    templines[idx][k] = disorderANNO

    tokenID2annodict = {}
    for idx, annodict in templines.items():
        tokenID2annodict[annodict["sent_word_id"]] = {k:v for k, v in annodict.items()}

    relIDset = set()
    for idx in templist:
        current_tokenID = templines[idx]["sent_word_id"]
        rel_idlist = templines[idx]["rel_id"]
        # print(rel_idlist)
        relIDset.add(tuple(rel_idlist))
        if len(rel_idlist) == 1:
            treatment_relID = rel_idlist[0]
            disorder_relID = "_"
        else:
            treatment_relID, disorder_relID = rel_idlist

        treatment_relID = adjust_relID(treatment_relID, tokenID2annodict, current_tokenID, treatment_now=True)
        disorder_relID = adjust_relID(disorder_relID, tokenID2annodict, current_tokenID, treatment_now=False)
        if treatment_relID and disorder_relID:
            templines[idx]["rel_id"] = "|".join([treatment_relID, disorder_relID])
        elif treatment_relID:
            templines[idx]["rel_id"] = treatment_relID
        elif disorder_relID:
            templines[idx]["rel_id"] = disorder_relID
        else:
            templines[idx]["rel_id"] = "_"

    print("relID:\t", relIDset)
    return templines



def combine_curated_and_original(curated_lines, disorder_lines):
    newlines = {}
    templines = {}
    templist = []
    curatedlen = set()
    count = 0
    for l1, l2 in zip(curated_lines, disorder_lines):
        items1 = l1.split("\t")
        items2 = l2.split("\t")
        curatedlen.add(len(items1))

        if len(items1) == len(items2) == 1:
            newlines[count] = l1
        elif len(items1) == 4:
            newlines[count] = l2
        else:
            currentline = {"sent_word_id": items2[0],
                           "word_span": items2[1],
                           "word": items2[2],
                           "entity_polarity": [items2[3]],
                           "entity": [items2[4]],
                           "F6": [items2[5]],
                           "G7": [items2[6]],
                           "H8": [items2[7]],
                           "I9": [items2[8]],
                           "relation": [items2[9]],
                           "relation_polarity": [items2[10]],
                           "L12": [items2[11]],
                           "rel_id": [items2[12]],
                           "new_line": items2[13]}
            if len(items1) == 7:
                # print(items1)
                sent_word_id, word_span, word, entity_polarity, entity, F6, new_line = items1
                if entity_polarity != "_":
                    currentline["entity_polarity"].append(entity_polarity)
                if entity != "_":
                    currentline["entity"].append(entity)
                if F6 != "_":
                    currentline["F6"].append(F6)
            else:
                # print(items1)
                sent_word_id, word_span, word, entity_polarity, entity, F6, G7, \
                H8, I9, relation, relation_polarity, L12, rel_id, new_line = items1
                if entity_polarity != "_":
                    currentline["entity_polarity"].append(entity_polarity)
                if entity != "_":
                    currentline["entity"].append(entity)
                if F6 != "_":
                    currentline["F6"].append(F6)
                if G7 != "_":
                    currentline["G7"].append(G7)
                if H8 != "_":
                    currentline["H8"].append(H8)
                if I9 != "_":
                    currentline["I9"].append(I9)
                if relation != "_":
                    currentline["relation"].append(relation)
                if relation_polarity != "_":
                    currentline["relation_polarity"].append(relation_polarity)
                if L12 != "_":
                    currentline["L12"].append(L12)
                if rel_id != "_":
                    currentline["rel_id"].append(rel_id)
            templines[count] = currentline
            templist.append(count)
        count += 1

    new_templines = renumbering(templines, templist)
    klist = ["sent_word_id", "word_span", "word", "entity_polarity", "entity", "F6", "G7",
             "H8", "I9", "relation", "relation_polarity", "L12", "rel_id", "new_line"]
    for idx, annodict in new_templines.items():
        outlist = []
        for k in klist:
            outlist.append(annodict[k])
        newlines[idx] = "\t".join(outlist)
    # print(curatedlen)
    # print(templines)
    # assert templines[1]["F6"][0] == templines[1]["F6"][1]
    # newline_list = []
    # for i in range(len(newlines)):
    #     newline_list.append(newlines[i])
    return newlines

def reformat(foutname, fdisordername, curated_lines, disorder_lines):
    with open(foutname, "w") as fw, open(fdisordername) as fdisorde:
        for line in fdisorde:
            if "#Text=" not in line:
                fw.write(line)
            else:
                break

        newlines = combine_curated_and_original(curated_lines, disorder_lines)

        for i in range(len(newlines)):
            line = newlines[i]
            fw.write(line)

def main():
    curated_dir = "../Anthem_curated_documents_2020-10-30_1731/curation"
    annotated_dir = "../Anthem_project_2020-10-30_1710/annotation"
    disorder_dir = "../ShAReCLEF_in_WebAnnoFormat"
    outdir = "../disorder_and_treatments"
    os.makedirs(outdir, exist_ok=True)

    # 1 	 ../Anthem_curated_documents_2020-10-30_1731/curation/03392-360395-RADIOLOGY_REPORT.tsv/CURATION_USER.tsv	204	204	204
    # {1, 7}
    # 2 	 ../Anthem_curated_documents_2020-10-30_1731/curation/00500-097836-ECHO_REPORT.tsv/CURATION_USER.tsv	426	426	426
    # {1, 7}
    # 3 	 ../Anthem_curated_documents_2020-10-30_1731/curation/08870-061373-ECG_REPORT.tsv/CURATION_USER.tsv	57	57	57
    # {1, 4}
    # 4 	 ../Anthem_curated_documents_2020-10-30_1731/curation/09040-052377-ECG_REPORT.tsv/CURATION_USER.tsv	56	56	56
    # {1, 4}
    # 5 	 ../Anthem_curated_documents_2020-10-30_1731/curation/00211-027889-DISCHARGE_SUMMARY.tsv/CURATION_USER.tsv	1584	1584	1584
    # {1, 14}

    count = 0
    filelist = []
    for item in os.listdir(curated_dir):
        filelist.append(item)
    filelist.sort()
    # filelist = ["00098-016139-DISCHARGE_SUMMARY.tsv"]
    # filelist = ["00414-104513-ECHO_REPORT.tsv"]
    for item in filelist:
        fcurated = os.path.join(curated_dir, item, "CURATION_USER.tsv")
        fannotated = os.path.join(annotated_dir, item, "summer.ploegman.tsv")
        fdisorder = os.path.join(disorder_dir, item)
        fout = os.path.join(outdir, item)
        count += 1
        print(count, '\t', fcurated, end="\t")
        curated_lines = countlines(fcurated)
        annotated_lines = countlines(fannotated)
        disorder_lines = countlines(fdisorder)
        assert len(curated_lines) == len(disorder_lines)
        assert len(disorder_lines) == len(annotated_lines)
        print()
        reformat(foutname=fout, fdisordername=fdisorder, curated_lines=curated_lines, disorder_lines=disorder_lines)


if __name__ == "__main__":
    main()

