import os
import random
import re
import sys
from collections import defaultdict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    
    res = defaultdict(float)
    N = len(corpus.keys())      # Total number of pages in corpus
    n = len(corpus[page])       # Number of pages connected to page
    
    if n == 0:                  # If current page has no outgoing links
        for p in corpus:
            res[p] = (damping_factor/N) + ((1 - damping_factor)/N)
    
    else:
        for p in corpus:
            if p in corpus[page]:           
                res[p] = (damping_factor/n) + ((1 - damping_factor)/N)
            else:
                res[p] = (1 - damping_factor)/N
    
    return res


def sample_pagerank(corpus, damping_factor, n):
    
    PagesSampleCount = defaultdict(int)
    prevSample = random.choice(list(corpus.keys()))
    
    for _ in range(n - 1):
        transitionModel = transition_model(corpus, prevSample, damping_factor)
        PagesSampleCount[prevSample] += 1
        prevSample = random.choices(list(transitionModel.keys()), weights = list(transitionModel.values()))[0]
        
    res = defaultdict(float)
    for page in corpus:
        res[page] = PagesSampleCount[page]/n
    
    return res
        

def iterate_pagerank(corpus, damping_factor):
    
    N = len(corpus)
    linksFromPages = reverse_corpus(corpus)

    res = {}
    for page in corpus:
        res[page] = 1.0/N

    while True:
        
        max_change = 0
        new_ranks = {}
        
        for page in res:
            new_ranks[page] = (((1 - damping_factor)/N) + damping_factor * 
                                (links_sum(corpus, res, page, linksFromPages)))
            new_ranks[page] += damping_factor * sum(res[p] for p in corpus if not corpus[p]) / N
            
            max_change = max(max_change, abs(new_ranks[page] - res[page]))
        
        res = new_ranks
        
        if max_change <= 0.001:
            break

    return res


def reverse_corpus(corpus):
    
    res = defaultdict(set)
    
    for page in corpus:
        for p in corpus[page]:
            res[p].add(page)
    
    return res


def links_sum(corpus, currProb, page, linksFromPages):
    
    res = 0
    
    for p in linksFromPages[page]:
        res += currProb[p]/len(corpus[p])
    
    return res  


if __name__ == "__main__":
    main()
