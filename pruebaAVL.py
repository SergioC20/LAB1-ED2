import re
import time
import datetime
from collections import defaultdict

class Node:
    def __init__(self, key, name):
        self.key = key
        self.name = name
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def get_height(self, root):
        if not root:
            return 0
        return root.height

    def get_balance(self, root):
        if not root:
            return 0
        return self.get_height(root.left) - self.get_height(root.right)

    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert(self, root, key, name):
        if not root:
            return Node(key, name)
        elif key < root.key:
            root.left = self.insert(root.left, key, name)
        else:
            root.right = self.insert(root.right, key, name)

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        balance = self.get_balance(root)

        if balance > 1 and key < root.left.key:
            return self.right_rotate(root)
        if balance < -1 and key > root.right.key:
            return self.left_rotate(root)
        if balance > 1 and key > root.left.key:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.key:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def delete(self, root, key):
        if not root:
            return root, False

        if key < root.key:
            root.left, deleted = self.delete(root.left, key)
        elif key > root.key:
            root.right, deleted = self.delete(root.right, key)
        else:
            deleted = True
            if root.left is None:
                return root.right, deleted
            elif root.right is None:
                return root.left, deleted

            temp = self.get_min_value_node(root.right)
            root.key = temp.key
            root.name = temp.name
            root.right, _ = self.delete(root.right, temp.key)

        if root is None:
            return root, deleted

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root), deleted
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root), deleted
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root), deleted
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root), deleted

        return root, deleted

    def get_min_value_node(self, root):
        if root is None or root.left is None:
            return root
        return self.get_min_value_node(root.left)

    def search(self, root, key):
        if root is None or root.key == key:
            return root

        if root.key < key:
            return self.search(root.right, key)

        return self.search(root.left, key)

def process_file(filename):
    tree = AVLTree()
    root = None

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
            root = tree.insert(root, key, name)
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
                result = tree.search(root, key)
                end_time = time.time()
                end_dt = datetime.datetime.now()
                elapsed_time = end_time - start_time
                timings['Search'].append((key, elapsed_time))
                found = result is not None
                name = result.name if found else ""
                log_entries.append(f'Search: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Encontrado: {"sí" if found else "no"}, Nombre: {name}')
               
            elif command == "Delete":
                result = tree.search(root, key)
                name = result.name if result else ""
                root, deleted = tree.delete(root, key)
                end_time = time.time()
                end_dt = datetime.datetime.now()
                elapsed_time = end_time - start_time
                timings['Delete'].append((key, elapsed_time))
                log_entries.append(f'Delete: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Encontrado: {"sí" if deleted else "no"}, Nombre: {name if deleted else ""}')
               

    log_filename = f"log-AVLTree-{filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(log_filename, 'w') as log_file:
        log_file.write('\n'.join(log_entries))

    with open('timing_results.txt', 'w') as f:
        
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

    with open('timing_results.txt', 'r') as f:
        timing_results_content = f.read()
        print(timing_results_content)

if __name__ == "__main__":
    filename = input("Ingrese el nombre del archivo de comandos: ")
    process_file(filename)