# PDF Search Engine

A search engine for PDF documents that parses document pages, builds efficient data structures for indexing, and allows users to perform ranked text searches through a console interface.

## Features

- PDF document parsing
- Page indexing
- Ranked search results
- Context snippets for matched results
- Multi-word query support
- Boolean operators:
  - AND
  - OR
  - NOT
- Phrase search
- Autocomplete suggestions
- "Did you mean?" suggestions
- Result pagination
- Serialization for faster startup
- PDF result exporting

## Data Structures & Algorithms

- Trie for efficient word lookup
- Graph for page relationship modeling
- Ranking algorithm based on:
  - keyword frequency
  - page references
  - linked page relevance

## Technologies

- Python
- PDF processing libraries
- Trie
- Graphs
- File serialization

## How it works

When the application starts, it parses a PDF document and creates indexing structures for efficient searching.

Users can then enter search queries such as:

- single keywords
- multiple keywords
- phrases
- boolean expressions

The system returns ranked pages along with text snippets showing where matches were found.

## Learning outcomes

This project helped me improve my understanding of:

- information retrieval systems
- indexing
- ranking algorithms
- advanced data structures
- PDF processing
