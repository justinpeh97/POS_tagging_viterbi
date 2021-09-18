# POS Tagging using Hidden Markov Model (Viterbi) algorithm

Part-of-speech tagging (POS tagging) is the task of tagging a word in a text with its part of speech. A part of speech is a category of words with similar grammatical properties. Common English parts of speech are noun, verb, adjective, adverb, pronoun, preposition, conjunction, etc.

Given the input sentence: 
"He also is a consensus manager ."

The POS tagger should output the following: 
"He/PRP also/RB is/VBZ a/DT consensus/NN manager/NN ./."

This repository contains a Hidden Markov Model (Viterbi) algorithm used to perform POS tagging, achieving a test accuracy of 95.88%.

buildtagger.py processes the training labelled text and extracts out the necessary statistics (such as P(word|tag)) for the Viterbi algorithm.
runtagger.py performs the Viterbi algorithm on a test text file and outputs the sentences with the POS tagging.
eval.py reads in the output from runtagger.py and the actual correct test output and computes the accuracy of the Viterbi algorithm.

Run the followings commands to test the algorithm:

python buildtagger.py sents.train model-file
python runtagger.py sents.test model-file sents.out
python eval.py sents.out sents.answer

Note that runtagger.py takes 1-2 minutes to run.
