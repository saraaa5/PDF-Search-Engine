import re


class Vertex(object):

    def __init__(self, index, page_num, content):
        self._index = index
        self._page_num = page_num
        self._content = content
        self.coming_links = []
        self.outgoing_links = []

    def get_incoming_links(self):
        return self.coming_links

    def get_outgoing_links(self):
        return self.outgoing_links

    def get_index(self):
        return self._index

    def get_page_num(self):
        return self._page_num

    def get_content(self):
        return self._content

    def count_phrase_appearances(self, phrase):
        return self.KMPSearch(phrase, self._content)

    def KMPSearch(self, pat, txt):
        M = len(pat)
        N = len(txt)
        txt = txt.lower()
        pat = pat.lower()
        # create lps[] that will hold the longest prefix suffix
        # values for pattern
        lps = [0] * M
        j = 0  # index for pat[]

        # Preprocess the pattern (calculate lps[] array)
        self.computeLPSArray(pat, M, lps)

        i = 0  # index for txt[]
        overall_counter = 0
        result = []
        while (N - i) >= (M - j):
            if pat[j] == txt[i]:
                i += 1
                j += 1

            if j == M:
                ind = i - j
                overall_counter += 1
                result.append(ind)
                j = lps[j - 1]

            # mismatch after j matches
            elif i < N and pat[j] != txt[i]:
                # Do not match lps[0..lps[j-1]] characters,
                # they will match anyway
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

        return (result, overall_counter)

    # Function to compute LPS array
    def computeLPSArray(self, pat, M, lps):
        len = 0  # length of the previous longest prefix suffix

        lps[0] = 0  # lps[0] is always 0
        i = 1

        # the loop calculates lps[i] for i = 1 to M-1
        while i < M:
            if pat[i] == pat[len]:
                len += 1
                lps[i] = len
                i += 1
            else:
                # This is tricky. Consider the example.
                # AAACAAAA and i = 7. The idea is similar
                # to search step.
                if len != 0:
                    len = lps[len - 1]

                    # Also, note that we do not increment i here
                else:
                    lps[i] = 0
                    i += 1


class Edge(object):
    def __init__(self, dest, source, value=None):
        self._value = value
        self._destination = dest
        self._source = source

    def get_source(self):
        return self._source

    def get_destination(self):
        return self._destination

    def get_value(self):
        return self._value

    def __str__(self):
        return str((str(self._source), str(self._destination)))


class Graph(object):
    def __init__(self, directed=False):
        self.vertexes = {}

    def get_out(self):
        return self._out

    def get_in(self):
        return self._in

    def get_pages(self):
        return self.vertexes.values()

    def insert_vertex(self, index, page_num, content):
        v = Vertex(index, page_num, content)
        self.vertexes[page_num] = v
        return v

    def vertex_count(self):
        return len(self._in)

    def get_vertex(self, vertex_index):
        vertices = self.vertices()
        if vertex_index in vertices:
            return vertices[vertex_index]

    def get_vertex_by_page_num(self, page_num):
        for vertex in self.vertexes.values():
            if vertex.get_page_num() == page_num:
                return vertex

    def edges(self):
        ret_val = []
        for veze in self._out.values():
            ret_val.extend(veze)
        return ret_val

    def degree(self, vertex, out=True):
        if out:
            return len(self._out[vertex])
        return len(self._in[vertex])

    def incident_edges(self, vertex, out=True):
        if out:
            return self._out[vertex]
        return self._in[vertex]

    def remove_vertex(self, vertex):
        izlazne = self._out[vertex]
        self._out.pop(vertex)
        ulazne = self._in[vertex]
        self._in.pop(vertex)
        for veza in izlazne:
            self._in[veza[1]].pop(veza)
        for veza in ulazne:
            self._out[veza[1]].pop(veza)

    def remove_edge(self, edge):
        self._out[edge.get_source()].pop(edge)
        self._in[edge.get_destination()].pop(edge)

    def get_edge(self, source, destination):
        for edge in self._out[source]:
            if edge.get_destination() == destination:
                return edge
        return None

    def find_page_links(self):

        regex = r"see\s*page\s*(\d+)|see\s*pages\s*(\d+)\s*and\s*(\d+)|on\s*page\s*(\d+)|from\s*page\s*(\d+)"

        for page in self.get_pages():
            page_content = page.get_content()
            page_num = page.get_page_num()
            matches = re.finditer(regex, page_content, re.IGNORECASE)
            links = []
            for match in matches:
                for group in match.groups():
                    if group:
                        current = self.get_vertex_by_page_num(page_num)
                        current.outgoing_links.append((int(group)))

                        v = self.get_vertex_by_page_num(int(group))
                        v.coming_links.append(page_num)