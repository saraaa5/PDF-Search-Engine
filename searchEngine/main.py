import os
import pickle

import parse_pdf_and_inputs
import search_engine
import graph


def print_custom_dict(content):
    for key, value in content.items():
        print(f"Index: {key}")
        print(f"Page number: {value['page_number']}")
        print(f"Content:\n\n{value['content']}")
        print("\n\n\n")


def create_trie_for_page(page_text):
    words = page_text.split()
    trie = search_engine.Trie()
    for word in words:
        trie.insert(word)
    return trie


def pickling():
    page_graph1 = graph.Graph(True)

    in_path = 'book.pdf'
    out_path = './book.pdf'
    result = parse_pdf_and_inputs.get_results_from_pdf(out_path)

    for page in result.values():
        index = page['index']
        page_num = page['page_number']
        content = page['content']
        trie = create_trie_for_page(content.lower())
        v = page_graph1.insert_vertex(index, page_num, content)
        v.trie = trie

    page_graph1.find_page_links()
    with open('page_graph.pkl', 'wb') as f:
        pickle.dump(page_graph1, f)
    abs_path = os.path.abspath('page_graph.pkl')
    if os.path.exists(abs_path):
        print(f"Serialization completed. File 'page_graph.pkl' created at: {abs_path}")
    else:
        print("Serialization failed. File not created.")


def unpickling():
    try:
        with open('page_graph.pkl', 'rb') as f:
            page_graph1 = pickle.load(f)
        print("Graph loaded from file.")
        return page_graph1
    except FileNotFoundError:
        print("Serialized graph not found, creating a new one.")
        return graph.Graph(True)


def autocomplete_output(expression, trie, graph):
    expression = expression.strip()
    prefix = expression[:-2]

    res = trie.autocomplete_suggestions(prefix, graph)

    if not res:
        return
    # trie.searching(res, graph)


def main():
    print("\033[94mLoading...\033[0m")
    page_graph1 = unpickling()
    print("\033[94mLoaded!\033[0m")
    trie = search_engine.Trie()
    print('-------------------------------------------------------------')
    print('Use "......" for phrase searching')
    print('Use AND, OR, NOT and brackets for logic expression searching')
    print('Use *** to exit program')
    print('-------------------------------------------------------------\n')

    while True:
        input_txt = input("Search whatever you want! (or '<3' for autocomplete): ")
        # print(len(input_txt))
        input_txt = input_txt.strip()
        if not input_txt:
            print("Error! You must type something!")
            continue
        elif input_txt == "***":
            print("Bye!")
            return
        elif input_txt[-2:] == "<3":
            print("Autocompleting...")
            autocomplete_output(input_txt, trie, page_graph1)
        else:
            print("Searching...")
            trie.searching(input_txt, page_graph1)


# main()
if __name__ == '__main__':
    if not os.path.exists('page_graph.pkl'):
        pickling()
    main()
