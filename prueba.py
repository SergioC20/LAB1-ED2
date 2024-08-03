import re
import time
import datetime
from collections import defaultdict

class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t  # Minimum degree (defines the range for number of keys)

    def insert(self, k, name):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode()
            self.root = temp
            temp.children.insert(0, root)
            self.split_child(temp, 0)
            self.insert_non_full(temp, k, name)
        else:
            self.insert_non_full(root, k, name)

    def insert_non_full(self, x, k, name):
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append((None, None))
            while i >= 0 and k < x.keys[i][0]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = (k, name)
        else:
            while i >= 0 and k < x.keys[i][0]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self.split_child(x, i)
                if k > x.keys[i][0]:
                    i += 1
            self.insert_non_full(x.children[i], k, name)

    def split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BTreeNode(y.leaf)
        x.children.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t) - 1]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.children = y.children[t: 2 * t]
            y.children = y.children[0: t]

    def search(self, k, x=None):
        if x is None:
            x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]:
            i += 1
        if i < len(x.keys) and k == x.keys[i][0]:
            return x, i
        elif x.leaf:
            return None
        else:
            return self.search(k, x.children[i])

    def delete(self, k):
        if not self.root.keys:
            return False
        deleted = self._delete(self.root, k)
        if not self.root.keys and self.root.children:
            self.root = self.root.children[0]
            return deleted

    def _delete(self, x, k):
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]:
            i += 1
        if x.leaf:
            if i < len(x.keys) and x.keys[i][0] == k:
                del x.keys[i]
                return True
            return False
        if i < len(x.keys) and x.keys[i][0] == k:
            return self._delete_internal_node(x, k, i)
        elif i < len(x.children):
            if len(x.children[i].keys) >= t:
                return self._delete(x.children[i], k)
        else:
            if i > 0 and len(x.children[i - 1].keys) >= t:
                self._borrow_from_prev(x, i)
            elif i < len(x.children) - 1 and len(x.children[i + 1].keys) >= t:
                self._borrow_from_next(x, i)
            else:
                if i < len(x.children) - 1:
                    self._merge(x, i)
                else:
                    self._merge(x, i - 1)
            return self._delete(x.children[i], k)
        return False

    def _delete_internal_node(self, x, k, i):
        t = self.t
        if x.leaf:
            if x.keys[i][0] == k:
                del x.keys[i]
                return True
            return False
        if len(x.children[i].keys) >= t:
            x.keys[i] = self._get_pred(x.children[i])
            return self._delete(x.children[i], x.keys[i][0])
        elif len(x.children[i + 1].keys) >= t:
            x.keys[i] = self._get_succ(x.children[i + 1])
            return self._delete(x.children[i + 1], x.keys[i][0])
        else:
            self._merge(x, i)
            return self._delete(x.children[i], k)

    def _borrow_from_prev(self, x, i):
        child = x.children[i]
        sibling = x.children[i - 1]
        child.keys.insert(0, x.keys[i - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        x.keys[i - 1] = sibling.keys.pop()

    def _borrow_from_next(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        child.keys.append(x.keys[i])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        x.keys[i] = sibling.keys.pop(0)

    def _merge(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        child.keys.append(x.keys[i])
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        del x.keys[i]
        del x.children[i + 1]

    def _get_pred(self, x):
        while not x.leaf:
            x = x.children[-1]
        return x.keys[-1]

    def _get_succ(self, x):
        while not x.leaf:
            x = x.children[0]
        return x.keys[0]


def process_file(filename, t):
    tree = BTree(t)

    with open(filename, 'r') as file:
        lines = file.readlines()
    
    pattern_insert = re.compile(r'Insert:\{id:(\d+),nombre:"(.+?)"\}')
    pattern_search_delete = re.compile(r'(Search|Delete):\{id:(\d+)\}')

    timings = {
        'Insert': [],
        'Search': [],
        'Delete': []
    }

    log_entries = []

    for line in lines:
        line = line.strip()
        if match := pattern_insert.match(line):
            key = int(match.group(1))
            name = match.group(2)
            start_time = time.time()
            start_dt = datetime.datetime.now()
            tree.insert(key, name)
            end_time = time.time()
            end_dt = datetime.datetime.now()
            elapsed_time = end_time - start_time
            timings['Insert'].append((key, elapsed_time))
            log_entries.append(f'Insert: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Nombre: {name}')
        elif match := pattern_search_delete.match(line):
            command = match.group(1)
            key = int(match.group(2))
            start_time = time.time()
            start_dt = datetime.datetime.now()
            if command == "Search":
                result = tree.search(key)
                end_time = time.time()
                end_dt = datetime.datetime.now()
                elapsed_time = end_time - start_time
                timings['Search'].append((key, elapsed_time))
                found = result is not None
                name = result[0].keys[result[1]][1] if found else ""
                log_entries.append(f'Search: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Encontrado: {"sí" if found else "no"}, Nombre: {name}')
            elif command == "Delete":
                result = tree.search(key)
                name = result[0].keys[result[1]][1] if result else ""
                deleted = tree.delete(key)
                end_time = time.time()
                end_dt = datetime.datetime.now()
                elapsed_time = end_time - start_time
                timings['Delete'].append((key, elapsed_time))
                log_entries.append(f'Delete: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Encontrado: {"sí" if deleted else "no"}, Nombre: {name if deleted else ""}')

    log_filename = f"log-BTree-{filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(log_filename, 'w') as log_file:
        log_file.write('\n'.join(log_entries))

    with open('timing_resultsB.txt', 'w') as f:
        for operation in ["Insert", "Search", "Delete"]:
            f.write(f'\n{operation}:\n')

            sorted_timings = sorted(timings[operation], key=lambda x: x[1])
            top_10_max = sorted_timings[-10:]
            top_10_min = sorted_timings[:10]
            average_timing = sum(time for _, time in sorted_timings) / len(sorted_timings) if sorted_timings else 0

            f.write('Top 10 maximos:\n')
            for key, elapsed_time in reversed(top_10_max):
                f.write(f'Id: {key}, Tiempo: {elapsed_time:.6f} segundos\n')
            
            f.write('Top 10 minimos:\n')
            for key, elapsed_time in top_10_min:
                f.write(f'Id: {key}, Tiempo: {elapsed_time:.6f} segundos\n')
            
            f.write(f'Promedio: {average_timing:.6f} segundos\n')
            f.write('\n')

        f.write('Tiempo total de todas las operaciones:\n')
        f.write(f'Insert: {sum(time for _, time in timings["Insert"]):.6f} segundos\n')
        f.write(f'Search: {sum(time for _, time in timings["Search"]):.6f} segundos\n')
        f.write(f'Delete: {sum(time for _, time in timings["Delete"]):.6f} segundos\n')

    with open('timing_resultsB.txt', 'r') as f:
        timing_results_content = f.read()
        print(timing_results_content)

if __name__ == "__main__":
    t = int(input("Ingrese el grado mínimo del árbol B (t): "))
    filename = input("Ingrese el nombre del archivo de comandos: ")
    process_file(filename, t)