import os
import math
import sys
import datetime
import ast
import re

def tag_sentence(test_file, model_file, out_file):
    alpha = 1e-4
    beta = 1e-7
    lambdaa = 0.95
    g2 = 5e-5
    v = 5
    
    model_dict = open(model_file)
    model_dict = model_dict.read()
    model_dict = ast.literal_eval(model_dict)

    t_t_prev = model_dict['t_t_prev']
    words_u_tags = model_dict['words_u_tags']
    list_tags = model_dict['list_tags']
    tags = model_dict['tags']
    words = model_dict['words']

    reader = open(test_file)
    test_lines = reader.readlines()
    reader.close()

    N = len(list_tags)
    
    # Get all words that appear only a few times in training set
    words_few = [k for k,value in words.items() if value <= v]
    # Get p(wi | ti) of such words
    words_u_tags_few = {k:v for k,v in words_u_tags.items() if k[0] in words_few}
    # Predetermined list of suffixes
    suffixes = ['able','al','an','ance','ancy','ant','ary','ate','ed','ee','en','ence','ent','er','ful',
               'ible','ic','ing','ion','ish','ism','ist','ity','ive','ize','less','logy','ly',
               'ness','or','ous','ship']

    def obtain_suf(word):
        for suffix in suffixes:
            if word.endswith(suffix):
                return suffix
        else:
            return "nosuffix"

    suf_tag = {} # Obtain counts of suffixes follwed by tag
    tag_sub = {} # Obtain counts of tags of words with few occurences

    for key in words_u_tags_few.keys():
        word = key[0]
        tag = key[1]
        suf = obtain_suf(word)

        if (suf,tag) not in suf_tag.keys():
            suf_tag[(suf,tag)] = 1
        else:
            suf_tag[(suf,tag)] += 1  

        if tag not in tag_sub.keys():
            tag_sub[tag] = 1
        else:
            tag_sub[tag] += 1

    # Counvert into probabilities
    for key in suf_tag.keys():
        suf_tag[key] /= tag_sub[key[1]]

    # Obtain p(ti | ti-1)
    def get_value_a(dic, key):
        if key in dic.keys():
            value = (dic[key] + alpha)/(1 + N* alpha)
        else:
            value = alpha / (1+N*alpha)
        # lambdaa parameter controls the interpolation parameter
        return value * lambdaa + tags[key[0]] * (1-lambdaa)  

    # Obtain p(wi | ti)
    def get_value_b(dic, key):

        # Manual tagging of digits
        if re.sub(r'[^\w\s]','',key[0] ).isdigit():
            if key[1] == "CD":
                return 1
            else:
                return 0

        # Unknown words model
        if key[0] not in words.keys():
            word = key[0]
            tag = key[1]
            suf = obtain_suf(word)
            if (suf,tag) not in suf_tag.keys():
                return g2
            else:
                return suf_tag[(suf,tag)] + g2
        
        if key in dic.keys():
            return (dic[key] + beta)/(1 + N* beta)
        else:
            return beta / (1+N*beta)

    def get_max(prob_mat,s,t,T):
        costs = [prob_mat[s_prime][t] * get_value_a(t_t_prev, (list_tags[s],list_tags[s_prime])) \
                   for s_prime in range(0,N-1)]
        highest_cost = max(costs)
        highest_index = costs.index(highest_cost) 
        return highest_cost, highest_index
    
    def viterbi(line):
        
        list_words = line.split()
        T = len(list_words)

        prob_mat = [[ 0 for i in range(T) ] for j in range(N) ]
        backpointer = [[ 0 for i in range(T) ] for j in range(N) ]

        # Initialize first column
        for row in range(0,N-1):
            a = get_value_a(t_t_prev, (list_tags[row],'<s>'))
            b = get_value_b(words_u_tags, (list_words[0], list_tags[row]))
            prob_mat[row][0] =  a * b

        for t in range(1, T):
            for s in range(0, N-1):
                highest_cost, highest_index = get_max(prob_mat, s, t-1,T)
                prob_mat[s][t] = highest_cost * get_value_b(words_u_tags, (list_words[t] , list_tags[s]))
                backpointer[s][t] = highest_index

        _ , cur_index = get_max(prob_mat, N-1, T-1 ,T)
        final_path = [cur_index]
        for i in range(T-1,0,-1):
            cur_index =  backpointer[cur_index][i]
            final_path.append(cur_index)
        final_path.reverse()
        final_string = ""

        final_string = ""
        for i in range(len(final_path)):
            final_string += list_words[i] + "/"
            final_string += list_tags[final_path[i]] + " "

        return final_string


    output_lines = []
    for line in test_lines:
        output = viterbi(line)
        output_lines.append(output)
    with open(out_file, 'w') as f:
        f.write('\n'.join(output_lines))
        
    print('Finished...')

if __name__ == "__main__":
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
