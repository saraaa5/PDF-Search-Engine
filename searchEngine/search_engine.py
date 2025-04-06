import os
from copy import deepcopy
import string

import fitz
from spellchecker import SpellChecker

from graph import Graph
import re
import numpy as np

graph1 = Graph(True)


class TrieNode(object):
    def __init__(self):
        self.children = {}
        self.isCompleteWord = False

    def get_children(self):
        return self.children

    def set_children(self, new_children):
        self.children = new_children

    def is_complete_word(self):
        return self.isCompleteWord

    def set_is_complete_word(self):
        self.isCompleteWord = bool


def print_phrase(page, results_num, matched_positions):
    content = page.get_content()
    matched_positions.sort()
    matched_positions = deepcopy(matched_positions)

    if len(matched_positions) == 0:
        return
    position = matched_positions[0]
    start_index = max(position[0] - 10, 0)
    end_counter = len(content) - start_index
    if end_counter < 100:
        start_index = max(start_index - 50, 0)

    counter = 0
    page_num = page.get_page_num()
    first_row = content.split("\n")[0]
    header = ' '.join(word for word in first_row.split(" ") if word.strip() and not word.strip().isdigit())

    print(f"\033[93m{results_num + 1}. Page number: {page_num} Title: {header}\033[0m")

    number_of_lines = 0
    print("...", end="")

    content_length = len(content)
    while start_index < content_length:
        if not matched_positions:
            break

        position = matched_positions[0]
        if start_index >= position[1]:
            matched_positions.pop(0)
            if not matched_positions:
                break
            position = matched_positions[0]

        is_highlighted = position[0] <= start_index < position[1]

        if is_highlighted:
            print(f"\033[45m{content[start_index]}\033[0m", end="")
        else:
            print(content[start_index], end="")

        if content[start_index] == '\n':
            number_of_lines += 1

        if counter >= 180 or number_of_lines >= 2:
            print(f"\033[0m...\n")
            break

        start_index += 1
        counter += 1

    print(f"\033[0m", end="")


def clean_word(expression):
    if not expression:
        return ""
    expression = expression.replace("AND", "")
    expression = expression.replace("OR", "")
    expression = expression.replace("NOT", "")
    expression = expression.replace("(", " ")
    expression = expression.replace(")", " ")
    expression = expression.strip()
    return expression


def save_as_pdf(pages, search_input, show=False, phs=False):
    print(search_input)
    if isinstance(search_input, list):
        search_terms = search_input  # Use the list of terms directly
    else:
        search_terms = search_input.split()

    print(search_terms)
    search_terms = [clean_word(term) for term in search_terms]  # Clean each term separately

    doc = fitz.open()

    for page in pages:
        pdf_page = doc.new_page(-1, 595, 842)
        p = fitz.Point(50, 70)
        pdf_page.insert_text(p, page.get_content(), fontname="Times-Roman", fontsize=12, rotate=0)

        page_text = page.get_content().lower()

        for term in search_terms:
            instances = pdf_page.search_for(term)
            print(term + " found on page " + str(page.get_page_num()) + " at positions: ", instances)

            if instances:
                for inst in instances:
                    highlight = pdf_page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=[1, 0.5, 0.5])
                    highlight.update()

    output_filename = f"results_for_{'_'.join(search_terms)}.pdf"

    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, output_filename)

    print(f"Current directory: {current_directory}")
    print(f"Saving file to: {output_path}")

    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print(f"Saved search results to {output_filename}\n")
    print("\033[42mIt might take some time and you must exit the program to load the file!\033[0m")


class Trie(object):
    def __init__(self):
        self._words = []
        self.root = TrieNode()
        self.spell = SpellChecker()

    def insert(self, word):
        for i in range(len(word)):
            current = self.root
            for letter in word[i:]:
                if letter not in current.children:
                    current.children[letter] = TrieNode()
                current = current.children[letter]
            current.end_of_word = True

    def search(self, substring):
        substring = substring.lower()
        current = self.root
        for char in substring:
            if char not in current.children:
                return False
            current = current.children[char]
        return True

    def searching(self, search_input, graph):
        print("Searching for: ", search_input)
        if '"' in search_input:
            self.search_phrase(search_input, graph)
        elif "AND" in search_input or "NOT" in search_input or "OR" in search_input:
            print("Searching for logic expression: \033[35m", search_input, "\033[0m ...")
            self.search_logic_expression(search_input, graph)
        else:
            words = search_input.split(" ")
            if len(words) == 1:
                self.search_single_word(search_input, graph)
            else:
                self.search_multiple_words(words, graph)

    def search_logic_expression(self, search_input, graph):
        search_input = search_input.strip()
        results = self.page_rank(graph, search_input, True)

        results.sort(key=lambda x: x.rank, reverse=True)
        tokens = self.tokenize(search_input)
        search_input = self.infix_to_postfix(tokens)
        txt = []
        for token in search_input:
            if token in ['AND', 'OR', 'NOT']:
                continue
            txt.append(token)

        search_words_str = ", ".join(txt)

        print(f"Searching for words: \033[35m{search_words_str}\033[0m ...")

        YELLOW = "\033[33m"
        PINK = "\033[45m"
        RESET = "\033[0m"

        results_per_page = 10
        total_results = len(results)
        # print("Total results: ", total_results)
        current_page = 0
        while True:
            start_index = current_page * results_per_page
            end_index = min(start_index + results_per_page, total_results)
            # print("\033[2J\033[H")
            print('start_index: ', start_index, ' end_index: ', end_index)
            a = 1
            for i in range(start_index, end_index):
                page = results[i]
                content = page.get_content()
                # Highlight each search word in the content
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{i + 1}) Page number: {page.get_page_num()} Rank: {page.rank}")
                for word in txt:
                    matches = re.finditer(word.lower(), content.lower())
                    for match in matches:
                        print(
                            f"...{content[match.start() - 10:match.start()]}{PINK}{content[match.start():match.end()]}{RESET}{content[match.end():match.end() + 10]}...")

                a += 1
            # print(f"\nAVAILBLE pages: " + str(a // 10 + 1))
            # print("a : ", a)
            if a > 1:
                print("\n -------------------------")
                if current_page > 0:
                    print("Previous page: p")
                if a >= 10:
                    print("Next page: n")
                print("PDF file: pdf")
                print("Exit: e")
                print("-------------------------\n ")

                user_input = input("Enter option: ").strip().lower()
                if user_input == 'n' and a >= 10:
                    current_page += 1
                elif user_input == 'p' and current_page > 0:
                    current_page -= 1
                elif user_input == 'e':
                    break
                elif user_input == "pdf":
                    save_as_pdf(results[:10], txt, True, True)
                    break
                else:
                    print("Invalid option, please choose again.")
                    continue

            else:
                print("We didn't find any matches! :(")
                break

        return results

    def infix_to_postfix(self, tokens):
        output = []
        operators = []
        precedence = {'OR': 1, 'AND': 2, 'NOT': 3}

        for token in tokens:
            if self.is_operand(token):
                output.append(token)
            elif token in precedence:
                while (operators and operators[-1] != '(' and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()  # Pop the '('

        while operators:
            output.append(operators.pop())

        return output

    def is_operand(self, token):
        # Check if the token is an operand (number/variable)
        return token not in ['AND', 'OR', 'NOT', '(', ')']

    def search_single_word(self, search_input, graph):
        if not search_input:
            return []
        print("Searching for word: \033[35m", search_input, "\033[0m ...")
        page_list = self.page_rank(graph, search_input)
        page_list.sort(key=lambda x: x.rank, reverse=True)

        YELLOW = "\033[33m"
        PINK = "\033[45m"
        RESET = "\033[0m"

        results_per_page = 10
        total_results = len(page_list)
        current_page = 0

        while True:
            start_index = current_page * results_per_page
            end_index = min(start_index + results_per_page, total_results)

            # print("\033[2J\033[H")
            a = 1

            for i in range(start_index, end_index):
                page = page_list[i]
                content = page.get_content()
                matches = re.finditer(search_input.lower(), content.lower())
                match_count = sum(1 for _ in matches)
                if match_count == 0:
                    continue

                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{i + 1}) Page number: {page.get_page_num()} Rank: {page.rank}")
                matches = re.finditer(search_input.lower(), content.lower())

                for match in matches:
                    print(
                        f"...{content[match.start() - 10:match.start()]}{PINK}{content[match.start():match.end()]}{RESET}{content[match.end():match.end() + 10]}...")

                a = a + 1
            # print(f"\nPage {current_page + 1} of {a // 10 + 1}")
            if a > 1:
                print("\n -------------------------")
                if current_page > 0:
                    print("Previous page: p")
                if a >= 10:
                    print("Next page: n")
                print("PDF file: pdf")
                print("Exit: e")
                print("-------------------------\n ")

                user_input = input("Enter option: ").strip().lower()
                if user_input == 'n' and a >= 10:
                    current_page += 1
                elif user_input == 'p' and current_page > 0:
                    current_page -= 1
                elif user_input == 'e':
                    break
                elif user_input == "pdf":
                    save_as_pdf(page_list[:10], search_input, True)
                    break
                else:
                    print("Invalid option, please choose again.")
                    continue

            else:
                print("We didn't find any matches! :(")
                self.inspect_phrase(search_input, graph)
                break

        return

    def inspect_phrase(self, search_input, graph):

        correction = self.inspect_single_word(search_input.lower(), graph)
        print("Did you mean: ", correction)

    def inspect_single_word(self, search_input, graph):
        candidates = self.spell.candidates(search_input)
        candidate = {}
        candidates = []
        for page in graph.vertexes.values():
            content = page.get_content()
            for word in content.split():
                word = word.lower()
                similarity = self.jaccard_similarity(search_input, word)
                candidate = (word, similarity)
                candidates.append(candidate)
        candidates.sort(key=lambda x: x[1], reverse=True)
        if len(candidates) == 0:
            return "unfortunately, there are no suggestions for this word."

        return candidates[0][0]

    def autocomplete_suggestions(self, prefix, graph):
        res = self.find_auto_complete(prefix, graph)
        if not res:
            print("NO AUTOCOMPLETE SUGGESTIONS")
            return False
        else:
            res_str = ", ".join(res)
            print(f"AUTOCOMPLETE SUGGESTIONS: \033[95m{res_str}\033[0m\n")
            return res

    def find_auto_complete(self, prefix, graph):
        suggestions = {}
        for page in graph.vertexes.values():
            content = page.get_content().lower()
            words = content.split()
            for word in words:
                word = word.strip(string.punctuation)  # Uklanja interpunkcijske znakove s krajeva reči
                if word.startswith(prefix):
                    if word in suggestions:
                        suggestions[word] += 1
                    else:
                        suggestions[word] = 1

        # Sortiranje po broju pojavljivanja reči u opadajućem redosledu
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        top_suggestions = [word for word, count in sorted_suggestions[:3]]

        return top_suggestions

    def jaccard_similarity(self, word1, word2):
        set1 = set(word1)
        set2 = set(word2)

        intersection = set1.intersection(set2)
        union = set1.union(set2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def find_prefix(self, prefix: str):
        node = self.root
        if len(self.root.children) == 0:
            return False, 0
        for char in prefix:
            char_not_found = True
            for child in node.children:
                if child.char == char:
                    char_not_found = False
                    node = child
                    break
            if char_not_found:
                return False, 0
        return True, node

    def search_multiple_words(self, search_input, graph):
        if not search_input:
            return []

        page_list = self.page_rank(graph, search_input)
        page_list.sort(key=lambda x: x.rank, reverse=True)

        search_words_str = ", ".join(search_input)
        print(f"Searching for words: \033[35m{search_words_str}\033[0m ...")

        YELLOW = "\033[33m"
        PINK = "\033[45m"
        RESET = "\033[0m"

        results_per_page = 10
        total_results = len(page_list)
        current_page = 0

        while True:
            start_index = current_page * results_per_page
            end_index = min(start_index + results_per_page, total_results)

            if start_index >= total_results:
                print("No more results.")
                break

            for i in range(start_index, end_index):
                page = page_list[i]
                content = page.get_content()
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{i + 1}) Page number: {page.get_page_num()} Rank: {page.rank}")
                for word in search_input:
                    matches = re.finditer(word.lower(), content.lower())
                    for match in matches:
                        print(
                            f"...{content[match.start() - 10:match.start()]}{PINK}{content[match.start():match.end()]}{RESET}{content[match.end():match.end() + 10]}...")

            print("\n -------------------------")
            if current_page > 0:
                print("Previous page: p")
            if end_index < total_results:
                print("Next page: n")
            print("PDF file: pdf")
            print("Exit: e")
            print("-------------------------\n ")

            user_input = input("Enter option: ").strip().lower()

            if user_input == 'n' and end_index < total_results:
                current_page += 1
            elif user_input == 'p' and current_page > 0:
                current_page -= 1
            elif user_input == 'e':
                break
            elif user_input == "pdf":
                save_as_pdf(page_list[:10], search_input, True)
                break
            else:
                print("Invalid option, please choose again.")
                continue

    def search_phrase(self, search_input, graph):
        if not search_input:
            return []
        search_input = search_input.replace('"', '')
        words = search_input.strip().split(" ")
        phrase = ' '.join(words)
        print("Searching for phrase: \033[35m", phrase, "\033[0m ...")
        page_list = self.page_rank(graph, phrase)
        page_list.sort(key=lambda x: x.rank, reverse=True)

        YELLOW = "\033[33m"
        PINK = "\033[45m"
        RESET = "\033[0m"

        results_per_page = 10
        total_results = len(page_list)
        current_page = 0

        while True:
            start_index = current_page * results_per_page
            end_index = min(start_index + results_per_page, total_results)

            # print("\033[2J\033[H")
            a = 1
            for i in range(start_index, end_index):
                page = page_list[i]
                content = page.get_content()
                matches = re.finditer(phrase.lower(), content.lower())
                match_count = sum(1 for _ in matches)
                if match_count == 0:
                    continue

                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{YELLOW}---------------------------------------------------------{RESET}")
                print(f"{i + 1}) Page number: {page.get_page_num()} Rank: {page.rank}")
                matches = re.finditer(phrase.lower(), content.lower())

                for match in matches:
                    print(
                        f"...{content[match.start() - 10:match.start()]}{PINK}{content[match.start():match.end()]}{RESET}{content[match.end():match.end() + 10]}...")
                a = a + 1
            # print(f"\nPage {current_page + 1} of {a // 10 + 1}")
            if a > 1:
                print("\n -------------------------")
                if current_page > 0:
                    print("Previous page: p")
                if a >= 10:
                    print("Next page: n")
                print("PDF file: pdf")
                print("Exit: e")
                print("-------------------------\n ")

                user_input = input("Enter option: ").strip().lower()
                if user_input == 'n' and a >= 10:
                    current_page += 1
                elif user_input == 'p' and current_page > 0:
                    current_page -= 1
                elif user_input == 'e':
                    break
                elif user_input == "pdf":
                    save_as_pdf(page_list[:10], search_input, True)
                    break
                else:

                    print("Invalid option, please choose again.")
                    continue

            else:
                print("We didn't find any matches! :(")
                break

        return

    def page_rank(self, graph, phrase, expression=False, damping_factor=0.85, max_iterations=100, tol=1.0e-6):

        num_pages = len(graph.vertexes)
        ranks = np.ones(num_pages) / num_pages
        new_ranks = np.zeros(num_pages)

        for iteration in range(max_iterations):
            i = 0
            for page in graph.vertexes.values():
                rank_sum = 0
                counter = 0
                if not expression:

                    if isinstance(phrase, str):
                        matches = re.finditer(phrase.lower(), page.get_content().lower())
                        for match in matches:
                            counter += 1
                    else:
                        for word in phrase:
                            matches = re.finditer(word.lower(), page.get_content().lower())
                            for match in matches:
                                counter += 1
                else:
                    tokens = self.tokenize(phrase)
                    postfix = self.infix_to_postfix(tokens)
                    counter = self.evaluate_page(page, postfix)
                p_occurrences = counter
                page.occurrences = p_occurrences
                for in_link in page.get_incoming_links():
                    in_page = graph.vertexes[in_link]
                    rank_sum += ranks[in_link] / len(in_page.get_outgoing_links())

                new_ranks[i] = (1 - damping_factor) / num_pages + damping_factor * rank_sum
                new_ranks[i] += p_occurrences
                i += 1
            if np.linalg.norm(new_ranks - ranks, ord=1) < tol:
                break

            ranks = new_ranks.copy()
        page_list = []
        for i, page in enumerate(graph.vertexes.values()):
            if page.occurrences == 0:
                continue
            page.rank = ranks[i]
            page_list.append(page)
        return page_list

    def tokenize(self, query):
        import re
        tokens = re.findall(r'\(|\)|AND|OR|NOT|[^\s()]+', query)
        return tokens

    def evaluate_page(self, page, postfix):
        result_stack = []
        counter_collective = 0
        # print(postfix)
        for token in postfix:

            if token not in ['NOT', 'AND', 'OR']:
                result_stack.append(token)

            elif token == 'AND':

                if len(result_stack) == 1:
                    operand1 = result_stack.pop()
                    matches = re.finditer(operand1, page.get_content().lower())
                    counter = 0
                    for match in matches:
                        counter += 1
                    if counter == 0:
                        return 0
                    else:
                        counter_collective += counter
                elif len(result_stack) > 1:
                    operand1 = result_stack.pop()
                    operand2 = result_stack.pop()
                    matches1 = re.finditer(operand1, page.get_content().lower())
                    matches2 = re.finditer(operand2, page.get_content().lower())
                    counter1 = 0
                    counter2 = 0
                    for match in matches1:
                        counter1 += 1
                    for match in matches2:
                        counter2 += 1
                    if counter1 == 0 or counter2 == 0:
                        return 0
                    else:
                        counter_collective += counter1 + counter2



            elif token == 'OR':

                if len(result_stack) == 1:
                    operand1 = result_stack.pop()
                    matches = re.finditer(operand1, page.get_content().lower())
                    counter = 0
                    for match in matches:
                        counter += 1
                    counter_collective += counter

                elif len(result_stack) > 1:
                    operand2 = result_stack.pop()
                    operand1 = result_stack.pop()

                    matches1 = re.finditer(operand1, page.get_content().lower())
                    matches2 = re.finditer(operand2, page.get_content().lower())
                    counter1 = 0

                    counter2 = 0
                    for match in matches1:
                        counter1 += 1
                    for match in matches2:
                        counter2 += 1

                    counter_collective += counter1 + counter2

            elif token == 'NOT':

                if len(result_stack) == 1:
                    operand1 = result_stack.pop()
                    matches = re.finditer(operand1, page.get_content().lower())
                    counter = 0
                    for match in matches:
                        counter += 1
                    if counter > 0:
                        return 0

                elif len(result_stack) > 1:
                    operand1 = result_stack.pop()
                    operand2 = result_stack.pop()
                    matches1 = re.finditer(operand1, page.get_content().lower())
                    matches2 = re.finditer(operand2, page.get_content().lower())
                    counter1 = 0
                    counter2 = 0
                    for match in matches1:
                        counter1 += 1
                    for match in matches2:
                        counter2 += 1
                    if counter2 == 0 or counter1 > 0:
                        return 0
                    else:
                        counter_collective += counter2

        return counter_collective


