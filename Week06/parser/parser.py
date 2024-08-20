import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | VP | S Conj S | S P S
NP -> N | Det N | Det NP | P NP | Adj NP | Adv NP | Conj NP | N NP | N Adv
VP -> V | V NP | Adv VP | V Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    
    nltk.download('punkt', quiet=True)
    
    sentence = sentence.lower()
    
    tokenized = nltk.tokenize.word_tokenize(sentence)
    
    res = [word for word in tokenized if not (len(word) == 1 and not word.isalpha())]
    print(res)    
    return res


def np_chunk(tree):
    
    np_chunks = []

    for subtree in tree.subtrees(lambda t: t.label() == 'NP'):
        if not any(child.label() == 'NP' for child in subtree.subtrees(lambda t: t != subtree)):
            np_chunks.append(subtree)

    return np_chunks

if __name__ == "__main__":
    main()
