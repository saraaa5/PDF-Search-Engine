from structures.pqueue import PQItem, PQError


class HeapNode(object):

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def get_key(self):
        return self._key

    def set_key(self, key):
        self._key = key

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def __eq__(self, other):
        return self._key == other.get_key()

    def __ne__(self, other):
        return self._key != other.get_key()

    def __lt__(self, other):
        return self._key < other.get_key()

    def __le__(self, other):
        return self._key <= other.get_key()

    def __gt__(self, other):
        return self._key > other.get_key()

    def __ge__(self, other):
        return self._key >= other.get_key()

    def __str__(self):
        return str(self._key)


class MinHeap(object):

    def __init__(self):
        self._data = []
        self._heap_size = 0

    def is_empty(self):
        return self._heap_size == 0

    def min(self):
        """
                Pronalazi i vraća najmanji element heap-a
                :return: uređeni par (prioritet, vrednost) za minimalni element
                """
        if self.is_empty():
            raise PQError("Heap je prazan")
        return self._data[0].key, self._data[0].value

    def _left(self, index):
        """
        Metoda izračunava indeks levog potomka čvora.

        Argument:
        - `i`: indeks čvora čiji se potomak računa
        """
        return index * 2 + 1

    def _right(self, index):
        """
        Metoda izračunava indeks desnog potomka čvora.

        Argument:
        - `i`: indeks čvora čiji se potomak računa
        """
        return index * 2 + 2

    def _parent(self, index):
        """
        Metoda izračunava indeks roditelja čvora.

        Argument:
        - `i`: indeks čvora čiji se roditelj računa
        """
        return (index - 1) // 2

    def _swap(self, a, b):
        """
        Metoda menja vrednosti čvorova sa zadatim indeksima.

        Argument:
        - `a`: indeks prvog čvora
        - `b`: indeks drugog čvora
        """
        self._data[a], self._data[b] = self._data[b], self._data[a]

    def add(self, key, value=None):
        """
        Metoda dodaje novi element u heap
        :param key: prioritet novog čvora
        :param value: vrednost novog čvora
        """
        new_item = PQItem(key, value)
        self._data.append(new_item)
        self._heap_size += 1
        self._upheap(len(self._data)-1)

    def _upheap(self, index):
        """
        Metoda postavlja čvor na ispravnu poziciju poređenjem sa roditeljem
        :param index: pozicija čvora
        """
        parent_index = self._parent(index)
        if parent_index < 0 or self._data[index] > self._data[parent_index]:
            return
        self._swap(index, parent_index)
        self._upheap(parent_index)

    def min(self):
        """
        Pronalazi i vraća najmanji element heap-a
        :return: uređeni par (prioritet, vrednost) za minimalni element
        """
        if self.is_empty():
            raise PQError("Heap je prazan")
        return self._data[0].key, self._data[0].value

    def remove_min(self):
        """
        Uklanaj i vraća najmanji element heap-a
        :return: uređeni par (prioritet, vrednost) za minimalni element
        """
        if self.is_empty():
            raise PQError("Heap je prazan")

        self._swap(0, self._heap_size-1)
        ret_node = self._data.pop(self._heap_size-1)
        self._heap_size -= 1

        self._downheap(0)
        return ret_node.key, ret_node.value

    def has_left(self, index):
        l = self.left(index)
        return l < self._heap_size - 1

    def has_right(self, index):
        r = self.right(index)
        return r < self._heap_size - 1

    def _downheap(self, index):
        """
        Metoda (ponovo) uspostavlja ispravan redosled elemenata heap-a. Od tri čvora (roditelj, levo i desno dete),
        pronalazi se najmanji i on se postavlja na poziciju roditelja. Postupak se ponavlja dok svi elementi heap-a
        ne dođu u ispravan poredak.
        :param index: pozicija za koju se utvrđuje element
        """
        left_child = self._left(index)
        right_child = self._right(index)

        min_index = index

        if left_child < self._heap_size and self._data[left_child] < self._data[index]:
            min_index = left_child

        if right_child < self._heap_size and self._data[right_child] < self._data[min_index]:
            min_index = right_child

        if min_index != index:
            self._swap(min_index, index)
            self._downheap(min_index)

    def __str__(self):
        ret_val = "["
        for node in self._data:
            if ret_val == "[":
                ret_val = ret_val + str(node)
                continue
            ret_val = ret_val + ", " + str(node)
        ret_val = ret_val + "]"
        return ret_val

    def return_data(self):
        return self._data

    def __len__(self):
        return len(self._data)


class MaxHeap(object):
    def __init__(self, data):
        self._data = data
        self._heap_size = len(data)
        self._build_max_heap()

    def has_left(self, index):
        l = self.left(index)
        return l < self._heap_size

    def has_right(self, index):
        r = self.right(index)
        return r < self._heap_size

    def _left(self, i):
        """
        Metoda izračunava indeks levog potomka čvora.

        Argument:
        - `i`: indeks čvora čiji se potomak računa
        """
        return 2 * i + 1

    def _right(self, i):
        """
        Metoda izračunava indeks desnog potomka čvora.

        Argument:
        - `i`: indeks čvora čiji se potomak računa
        """
        return 2 * i + 2

    def parent(self, position):
        return (position - 1) // 2

    def _swap(self, a, b):
        """
        Metoda menja vrednosti čvorova sa zadatim indeksima.

        Argument:
        - `a`: indeks prvog čvora
        - `b`: indeks drugog čvora
        """
        self._data[a], self._data[b] = self._data[b], self._data[a]

    def _build_max_heap(self):
        """
        Metoda vrši formiranje max heapa.
        """
        self._size = len(self._data)

        # svi elementi sa indeksom većim od n/2 biće listovi stabla
        start = (self._size - 1) // 2
        for i in range(start, -1, -1):
            self._max_heapify(i)

    def _max_heapify(self, i):
        """
        Metoda formira max-heap od podstabla sa korenom u čvoru i.

        Argument:
        - `i`: indeks korena podstabla
        """

        # određivanje levog i desnog potomka čvora
        left = self._left(i)
        right = self._right(i)

        # provera levog potomka
        #   - da li je još na heapu
        #   - da li je podatak levog veći od podatka korena
        if left < self._heap_size and self._data[left] > self._data[i]:
            largest = left
        else:
            largest = i

        # provera desnog potomka
        if right < self._heap_size and self._data[right] > self._data[largest]:
            largest = right

        # zameni vrednosti ako nisu u max-heap redosledu
        if largest != i:
            self._swap(i, largest)
            self._max_heapify(largest)

    def m_heapify(self, i):
        l_index = self.left(i)
        r_index = self.right(i)

        max = i
        if l_index < self._heap_size and self._data[l_index] < self._data[max]:
            max = l_index
        if self.has_right(i) and self._data[r_index] < self._data[max]:
            max = r_index

        if max != i:
            self.swap(max, i)
            self.m_heapify(max)

    def __str__(self):
        ret_val = "["
        for node in self._data:
            if ret_val == "[":
                ret_val = ret_val + str(node)
                continue
            ret_val = ret_val + ", " + str(node)
        ret_val = ret_val + "]"
        return ret_val

    def get_items(self):
        return self._data

    def sort(self):
        """
        Heap sort algoritam
        """
        for i in range(self._size-1, 0, -1):
            # zameni prvi i poslednji
            self._swap(0, i)

            # izbaci poslednji sa heapa
            self._heap_size -= 1

            # preostale elemente transformiši u max-heap
            self._max_heapify(0)

    def get_data(self):
        return self.array
