import fitz


def extract_page_number(text, previous_page_num):
    try:
        # mnoge str pdf-ova  imaju broj strane na vrhu, cesto kao poslednju rec prve linije
        first_line = text.split("\n")[0]
        page_num = int(first_line.split()[-1].strip())
    except:
        if previous_page_num is not None:
            page_num = previous_page_num + 1
        else:
            page_num = None
    return page_num


def get_results_from_pdf(file_path):
    pdf = fitz.open(file_path)
    result = {}
    previous_page_num = None
    index = 0
    for page in pdf:
        text = page.get_text("text")
        page_num = extract_page_number(text, previous_page_num)
        result[index] = {
            'index': index,
            'page_number': page_num,
            'content': text
        }
        previous_page_num = page_num
        index += 1
    return result


# def next_page_input():
#     input_txt = input("Type '>' for next page, '<' for previous page, 'pdf' for exporting, '?' to search again  ")
#     input_txt = input_txt.strip()
#     if not input_txt:
#         return 1
#     if input_txt == "?":
#         return 0
#     if input_txt == "<":
#         return -1
#     if input_txt.lower() == "pdf":
#         return 2
#     return 1
