# PDF Search Engine

A command-line search engine for PDF documents. It parses a PDF book, indexes all pages into a graph data structure, and supports rich text searches with PageRank-based result ranking.

## Features

- **Single word search** — find pages containing a specific word, ranked by relevance
- **Multi-word search** — search for multiple terms at once
- **Phrase search** — exact phrase matching using `"double quotes"`
- **Boolean logic search** — combine terms with `AND`, `OR`, `NOT`, and parentheses
- **Autocomplete** — type a prefix followed by `<3` to get word suggestions
- **Spell suggestions** — Jaccard similarity-based suggestions when no match is found
- **Export to PDF** — save highlighted search results as a new PDF file
- **PageRank ranking** — results are ranked using a graph-based algorithm that factors in cross-page references and term frequency
- **Persistent index** — the page graph is serialized to disk (`page_graph.pkl`) so it only needs to be built once

## Project Structure

```
searchEngine/
├── main.py                  # Entry point and REPL loop
├── parse_pdf_and_inputs.py  # PDF parsing with PyMuPDF
├── search_engine.py         # Core search logic, Trie, PageRank
├── graph.py                 # Graph, Vertex, Edge data structures + KMP matching
├── page_graph.pkl           # Cached serialized page graph (auto-generated)
├── book.pdf                 # The PDF to be indexed
└── structures/
    ├── heap.py              # MinHeap and MaxHeap implementations
    ├── pqueue.py            # Priority queue
    └── stack.py             # Stack
```

## Requirements

- Python 3.7+
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`)
- [pyspellchecker](https://pyspellchecker.readthedocs.io/)
- [NumPy](https://numpy.org/)

Install dependencies:

```bash
pip install pymupdf pyspellchecker numpy
```

## Usage

1. Place your PDF file at `searchEngine/book.pdf`.
2. Run the search engine:

```bash
cd searchEngine
python main.py
```

On the first run, the PDF will be parsed and indexed (this may take a moment). The index is saved to `page_graph.pkl` for fast startup on subsequent runs.

3. Use the interactive prompt to search:

```
-------------------------------------------------------------
Use "......" for phrase searching
Use AND, OR, NOT and brackets for logic expression searching
Use *** to exit program
-------------------------------------------------------------

Search whatever you want! (or '<3' for autocomplete):
```

### Search Examples

| Query | Description |
|---|---|
| `algorithm` | Search for a single word |
| `binary search tree` | Search for multiple words |
| `"dynamic programming"` | Exact phrase search |
| `tree AND graph` | Boolean AND |
| `sort OR search` | Boolean OR |
| `recursion NOT stack` | Boolean NOT |
| `(tree OR graph) AND algorithm` | Combined boolean expression |
| `dyna<3` | Autocomplete for words starting with `dyna` |

### Navigation

After results are displayed, use the following options:
- `n` — next page of results
- `p` — previous page of results
- `pdf` — export top 10 results to a highlighted PDF file
- `e` — exit back to the search prompt
- `***` — quit the program

## How It Works

1. **Indexing**: The PDF is parsed page by page using PyMuPDF. Each page becomes a `Vertex` in a directed `Graph`. The graph's edges are built by scanning page text for cross-references like *"see page 42"*.

2. **Trie index**: Each page's text is inserted into a `Trie` to support fast prefix lookups and autocomplete.

3. **KMP matching**: Exact phrase/substring search on page content uses the Knuth-Morris-Pratt algorithm for efficient pattern matching.

4. **PageRank**: Search results are ranked using a PageRank-inspired algorithm. Each page's rank is influenced by how often the search term appears on it and how many other pages link to it.

5. **Boolean expressions**: Logic queries are parsed using a tokenizer and converted from infix to postfix notation (shunting-yard algorithm), then evaluated per page.
