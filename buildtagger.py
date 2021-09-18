import os
import math
import sys
import datetime


def train_model(train_file, model_file):

    # Reading in training file
    reader = open(train_file)
    train_lines = reader.readlines()
    reader.close()
    
    tags = {} # Keeps track of the tags in the corpora and probability of them occuring
    words_u_tags = {} # Keep track of probabilities of (word followed by particular tag)
    t_t_prev = {} # Keep track of probabilities of (tag followed by particular tag)
    words = {} # Keep track of all the counts of words in the corpora

    num_lines = 0

    for line in train_lines:
        num_lines += 1
        prev_tag = "<s>"
        cur_out_line = line.strip()
        cur_out_tags = cur_out_line.split(' ')
        cur_out_tags.append('DummyWord/<eos>')

        for word_tag in cur_out_tags:
            word, tag = word_tag.rsplit('/',1)
            
            # Counts of tags 
            if tag in tags.keys():
                tags[tag] += 1
            else:
                tags[tag] = 1

            # Counts of words followed by a particular tag
            if (word,tag) in words_u_tags:
                words_u_tags[(word,tag)] += 1
            else:
                words_u_tags[(word,tag)] = 1

            # Counts of tag followed by particular tag
            if (tag,prev_tag) in t_t_prev:
                t_t_prev[(tag,prev_tag)] += 1
            else:
                t_t_prev[(tag,prev_tag)] = 1
                
            # Counts of words
            if word in words.keys():
                words[word] += 1
            else:
                words[word] = 1
                
            prev_tag = tag

    # Ensure that <eos> is last tag
    list_tags = list(tags.keys())
    eos_index = list_tags.index("<eos>")
    list_tags[eos_index], list_tags[-1] = list_tags[-1], list_tags[eos_index]
            
    # Converting counts into probailities
    for key in t_t_prev:
        if key[1] == "<s>":
            t_t_prev[key] /= num_lines
        else:
            t_t_prev[key] /= tags[key[1]]

    for key in words_u_tags:
        words_u_tags[key] /= tags[key[1]]

    sum_tags_values = sum(tags.values())
    for tag in tags:
        tags[tag] /= sum_tags_values

    # Putting all dictionaries into one dictionary for saving
    output_dic = {
        "t_t_prev": t_t_prev,
        "words_u_tags": words_u_tags,
        "list_tags": list_tags,
        'tags': tags,
        'words': words
    }

    # Saving output_dic
    with open(model_file, 'w') as f:
        print(output_dic, file=f)

if __name__ == "__main__":
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
