import os
import random
import re
import sys

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
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()
    no_of_pages = len(corpus)
    for k in corpus.keys():
        probability_distribution[k] = (1 - damping_factor) / no_of_pages
    no_of_links_from_page = len(corpus[page])
    for v in corpus[page]:
        probability_distribution[v] = probability_distribution[v] + damping_factor / no_of_links_from_page
    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict(corpus)
    for k in page_rank:
        page_rank[k] = 0
    current_page = random.choice(list(corpus))
    page_rank[current_page] = 1
    for _ in range(1, n):
        current_transition_model = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(population=list(current_transition_model),
                                      weights=list(current_transition_model.values()))[0]
        page_rank[current_page] = page_rank[current_page] + 1
    for k in page_rank:
        page_rank[k] = page_rank[k] / n
    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    number_of_pages = len(corpus)
    old_page_rank = dict(corpus)
    for k in old_page_rank:
        old_page_rank[k] = 1 / number_of_pages
    new_page_rank = dict(old_page_rank)
    max_error = 0.001
    error = 1
    while error > max_error:
        error = 0
        old_page_rank = dict(new_page_rank)
        for k in new_page_rank:
            new_page_rank[k] = 0
            for i in corpus:
                if k in corpus[i]:
                    new_page_rank[k] = new_page_rank[k] + old_page_rank[i] / len(corpus[i])
            new_page_rank[k] = damping_factor * new_page_rank[k] + (1 - damping_factor) / number_of_pages
            current_error = abs(new_page_rank[k] - old_page_rank[k])
            if current_error > error:
                error = current_error
    return new_page_rank


if __name__ == "__main__":
    main()
