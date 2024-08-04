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
    def get_height(self, root):  #devuelve la altura del nodo 'root'
        if not root:
            return 0 #Si root es None devuelve 0
        return root.height

    def get_balance(self, root): #balanceo del arbol 
        if not root:
            return 0
        return self.get_height(root.left) - self.get_height(root.right) #calcula y devuelve el factor de balanceo de root (diferencia entre el subarbol izquierdo  y derecho)

    def right_rotate(self, z):
        y = z.left #'y' se convierte en el nuevo nodo raiz
        T3 = y.right #T3 es el subarbol derecho de 'y'
         #realiza la rotacion
        y.right = z #'y' se convierte en la nueva raiz y 'z' se convierte en el subarbol derecho
        z.left = T3 # 'T3' se convierte en el subarbol izquiedo de 'z'
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right)) #se actualizan las alturas
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y #'y' es la nueva raiz del subarbol

    def left_rotate(self, z): #rotacion a la izquierda
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
        elif key < root.key: #si es menor se inserta a la izquierda
            root.left = self.insert(root.left, key, name)
        else: 
            root.right = self.insert(root.right, key, name) #si es mayor se inserta a la derecha

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))  #actuzliza la altura: 1 + la altura maxima de cada subarbol

        balance = self.get_balance(root) #calculamos el balance del arbol

        if balance > 1 and key < root.left.key: #rotacion a la derecha
            return self.right_rotate(root)
        if balance < -1 and key > root.right.key: #rotacion a la izquierda
            return self.left_rotate(root)
        if balance > 1 and key > root.left.key: #rotacion izquierda - derecha
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.key: #rotacion derecha - izquierda
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def delete(self, root, key):
        if not root:
            return root, False #retorna falso si no se elimino un nodo

        if key < root.key:
            root.left, deleted = self.delete(root.left, key) #eliminacion  del nodo en el subarbol izquiedo
        elif key > root.key:
            root.right, deleted = self.delete(root.right, key) # eliminacion del nodo en el subarbol derecho
        else: 
            deleted = True # se encontro el nodo a eliminar
            if root.left is None: #si no hay nodo en el lado izquierdo se devuelve al lado derecho del subarbol
                return root.right, deleted
            elif root.right is None: #si no hay nodo en el lado derecho se devuelve al lado izquierdo del subarbol
                return root.left, deleted
            #nodos con dos hijos
            temp = self.get_min_value_node(root.right) #nodo con el valor minimo del lado derecho
            root.key = temp.key #se remplazan los nodos actuales con los nodos temporales
            root.name = temp.name
            root.right, _ = self.delete(root.right, temp.key) # elimina el nodo de valor mínimo del subárbol derecho.

        if root is None:
            return root, deleted

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right)) #actualiza la altura

        balance = self.get_balance(root) #calcula el balance

        if balance > 1 and self.get_balance(root.left) >= 0: #rotacion a la derecha
            return self.right_rotate(root), deleted
        if balance < -1 and self.get_balance(root.right) <= 0: #rotacion a la izquierda
            return self.left_rotate(root), deleted
        if balance > 1 and self.get_balance(root.left) < 0: #rotacion izquierda-derecha
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root), deleted
        if balance < -1 and self.get_balance(root.right) > 0: #rotacion derecha-izquierda
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root), deleted

        return root, deleted #retorna el nodo actual e indica con un booleano si se elimino un nodo

    def get_min_value_node(self, root): #valor minimo en el subarbol
        if root is None or root.left is None: #indica que el subarbol esta vacio o que el nodo actual no tiene hijo izquierdo
            return root
        return self.get_min_value_node(root.left) #funcion recursiva para seguir buscando el nodo minimo

    def search(self, root, key): #buscar el valor del nodo
        if root is None or root.key == key: #si hemos llegado a un nodo que no existe o hemos encontrado el nodo que estamos buscando
            return root

        if root.key < key: #la clave del nodo actual es menor a la que estamos buscanfo 
            return self.search(root.right, key) #buscamos en el subarbol derecho

        return self.search(root.left, key) #buscamos en el subarbol izquierdo
    
class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = [] #lista de las claves en el nodo
        self.children = [] #lista de hijos del nodo
        self.leaf = leaf #boolenao que indica si el nodo es una hoja

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t  # Grado mínimo (define el rango para el número de claves)

    def insert(self, k, name):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1: #verifica si la raiz esta llena
            temp = BTreeNode() #crea un nuevo nodo tem que sera la raiz nueva
            self.root = temp 
            temp.children.insert(0, root) #inserta la raiz actual como el primer hijo de tem
            self.split_child(temp, 0) #divide el antiguo nodo raiz
            self.insert_non_full(temp, k, name) #inserta la nueva clave en la raiz no llena
        else:
            self.insert_non_full(root, k, name) #si la raiz no esta llena llama a la funcion insert_non_full

    def insert_non_full(self, x, k, name): #metodo para la raiz cuando no esta llena
        i = len(x.keys) - 1 #inicializa 'i' como el nodo de la ultima clave en el nodo 'x'
        if x.leaf: # 'x' es una hoja
            x.keys.append((None, None)) # se añade espacio para la nueva clave
            while i >= 0 and k < x.keys[i][0]: #se desplazan las claves mayores a la clave 'k'
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = (k, name) #se inserta 'k' en la posicion correcta 
        else: 
            while i >= 0 and k < x.keys[i][0]: # se encuenrtra el hijo adecuado para descender
                i -= 1 #se decrementa 'i' hasta que 'k' no sea menor
            i += 1 # se incrementa 'i' para obtener el indice del hijo apropiado
            if len(x.children[i].keys) == (2 * self.t) - 1: #en caso de que el hijo este lleno
                self.split_child(x, i) #divide el hijo
                if k > x.keys[i][0]: #insertar en el hijo izquierdo o derecho
                    i += 1
            self.insert_non_full(x.children[i], k, name)

    def split_child(self, x, i): 
        t = self.t
        y = x.children[i] #hijo de 'x' en la posicion 'i' que esta lleno
        z = BTreeNode(y.leaf) #nodo hermano de 'y' si 'y' es una hoja
        x.children.insert(i + 1, z) #inserta el nuevo hijo en 'x'
        x.keys.insert(i, y.keys[t - 1]) #la clave mediana de 'y' se mueve a 'x'
        z.keys = y.keys[t: (2 * t) - 1] #las claves superiores de 'y' se asignan a 'z'
        y.keys = y.keys[0: t - 1] #'y' contiene solo los valoes inferiores
        if not y.leaf: 
            z.children = y.children[t: 2 * t] #se mueven los hijos superiores de 'y' a 'z'
            y.children = y.children[0: t] #los hijo inferiores permanecen en 'y'

    def search(self, k, x=None):
        if x is None: #inicializa la busqueda desde la raiz
            x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]: #recorre la lista de las claves 
            i += 1
        if i < len(x.keys) and k == x.keys[i][0]: #compureba si se ha encontrado la clave
            return x, i
        elif x.leaf: 
            return None #la clave no esta en el arbol y retona 'None'
        else:
            return self.search(k, x.children[i]) 

    def delete(self, k):
        if not self.root.keys: #la raiz está vacia
            return False
        deleted = self._delete(self.root, k)
        if not self.root.keys and self.root.children: #verifica si raiz no tiene claves  pero tiene hijos
            self.root = self.root.children[0] #el primer hijo es la nueva raiz
            return deleted

    def _delete(self, x, k):
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]: # Encuentra la primera clave en el nodo x que es mayor o igual a k
            i += 1
        if x.leaf: # El nodo x es una hoja
            if i < len(x.keys) and x.keys[i][0] == k: # Si k está presente en el nodo hoja, se elimína
                del x.keys[i]
                return True 
            return False
        #El nodo x no es una hoja
        if i < len(x.keys) and x.keys[i][0] == k: #Si k esta presente en el nodo x, eliminarlo del nodo interno
            return self._delete_internal_node(x, k, i) 
        elif i < len(x.children): # Si k no esta en el nodo x, desciende al hijo apropiado
            if len(x.children[i].keys) >= t:  # Si el hijo tiene al menos t claves, lo elimina
                return self._delete(x.children[i], k)
        else:  # El nodo hijo tiene menos de t claves
            if i > 0 and len(x.children[i - 1].keys) >= t: # Si el hijo anterior (izquierda) tiene al menos t claves, toma prestado de el
                self._borrow_from_prev(x, i)
            elif i < len(x.children) - 1 and len(x.children[i + 1].keys) >= t:  # Si el hijo siguiente (derecha) tiene al menos t claves, toma prestado de el
                self._borrow_from_next(x, i)
            else:  # Si no se puede tomar prestado, fusiona con un hermano
                if i < len(x.children) - 1:
                    self._merge(x, i)
                else:
                    self._merge(x, i - 1)
            return self._delete(x.children[i], k) # Despues del prestamo o la fusion, intenta eliminar de nuevo en el nodo hijo
        return False

    def _delete_internal_node(self, x, k, i):
        t = self.t
        if x.leaf: # Si x es una hoja elimina la clave k si esta presente
            if x.keys[i][0] == k:
                del x.keys[i]
                return True
            return False
        if len(x.children[i].keys) >= t: # Si el hijo anterior a la clave tiene al menos t claves
            x.keys[i] = self._get_pred(x.children[i])  # Reemplaza la clave por su predecesor y elimina recursivamente en el predecesor
            return self._delete(x.children[i], x.keys[i][0])
        elif len(x.children[i + 1].keys) >= t: # Si el hijo siguiente a la clave tiene al menos t claves
            x.keys[i] = self._get_succ(x.children[i + 1]) # Reemplaza la clave por su sucesor y elimina recursivamente en el sucesor
            return self._delete(x.children[i + 1], x.keys[i][0])
        else:  # Si ninguno de los hijos tiene al menos t claves, fusiona los dos hijos
            self._merge(x, i)
            return self._delete(x.children[i], k)

    def _borrow_from_prev(self, x, i):
        child = x.children[i]
        sibling = x.children[i - 1]
        child.keys.insert(0, x.keys[i - 1]) # Inserta la clave de x en el inicio del hijo
        if not child.leaf:  # mueve el último hijo del hermano al inicio del hijo
            child.children.insert(0, sibling.children.pop())
        x.keys[i - 1] = sibling.keys.pop() # Mueve la última clave del hermano a x

    def _borrow_from_next(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        child.keys.append(x.keys[i]) # Añade la clave de x al final del hijo
        if not child.leaf:
            child.children.append(sibling.children.pop(0)) #mueve el primer hijo del hermano al final del hijo
        x.keys[i] = sibling.keys.pop(0) # Mueve la primera clave del hermano a x

    def _merge(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        child.keys.append(x.keys[i]) # Mueve la clave de x al hijo
        child.keys.extend(sibling.keys)
        if not child.leaf: #mueve todos los hijos del hermano al hijo
            child.children.extend(sibling.children)
        del x.keys[i] # Elimina la clave y el hermano de x
        del x.children[i + 1]

    def _get_pred(self, x): # Encuentra el predecesor de una clave en el arbol
        while not x.leaf: #Mientras 'x' no sea una hoja, sigue descendiendo al último hijo 
            x = x.children[-1]
        return x.keys[-1] #retorna la última clave de esa hoja

    def _get_succ(self, x): #Encuentra el sucesor de una clave en el arbol
        while not x.leaf: #Mientras 'x' no sea una hoja, sigue descendiendo al primer hijo 
            x = x.children[0]
        return x.keys[0] #retorna la primera clave de esa hoja

class BPlusNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.next = None  # Para enlazar nodos hoja

class BPlusTree:
    def __init__(self, t):
        self.root = BPlusNode(True)
        self.t = t  # Grado mínimo

    def insert(self, k, name):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1: # Si la raiz esta llena se divide
            temp = BPlusNode() # Crea un nuevo nodo temporal que sera la nueva raiz
            self.root = temp
            temp.children.insert(0, root) # Insertar la antigua raiz como primer hijo de la nueva raiz
            self.split_child(temp, 0) # Divide el hijo
            self.insert_non_full(temp, k, name) # Insertar en el arbol no lleno
        else:
            self.insert_non_full(root, k, name) # Insertar directamente si la raiz no esta llena


    def insert_non_full(self, x, k, name):
        i = len(x.keys) - 1
        if x.leaf: # Si es una hoja, se inserta la nueva clave en la posicion correcta
            x.keys.append((None, None)) # Añade un espacio para la nueva clave
            while i >= 0 and k < x.keys[i][0]:
                x.keys[i + 1] = x.keys[i] # Desplazar claves mayores hacia la derecha
                i -= 1
            x.keys[i + 1] = (k, name) # Insertar la nueva clave
        else: # Si no es una hoja, encontrar el hijo apropiado para insertar la clave
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self.split_child(x, i) # Divide el hijo si esta lleno
                if k > x.keys[i]:
                    i += 1
            self.insert_non_full(x.children[i], k, name) # Recursivamente insertar en el hijo apropiado

    def split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BPlusNode(y.leaf)  # Crear un nuevo nodo 'z' que sera el hermano de 'y'
        x.children.insert(i + 1, z) # Insertar z como hijo de x
        
        if y.leaf: # Si y es una hoja, divide las claves y actualiza los punteros
            z.keys = y.keys[t - 1:] # La mitad superior de las claves de 'y' van a 'z'
            y.keys = y.keys[:t - 1] # La mitad inferior de las claves de 'y' se queda en 'y'
            x.keys.insert(i, z.keys[0][0]) # La clave mínima de 'z' se inserta en 'x'
            z.next = y.next # Actualiza el puntero siguiente de 'z'
            y.next = z # Actualiza el puntero siguiente de y
        else:  # Si 'y' no es una hoja, divide las claves y los hijos
            z.keys = y.keys[t:] # La mitad superior de las claves de 'y' van a 'z'
            y.keys = y.keys[:t - 1]  # La mitad inferior de las claves de 'y' se queda en 'y'
            x.keys.insert(i, y.keys[-1])  # La clave mínima de 'z' se inserta en 'x'
            z.children = y.children[t:] # La mitad superior de los hijos de 'y' van a 'z'
            y.children = y.children[:t] # La mitad inferior de los hijos de 'y' se queda en 'y'

    def search(self, k, x=None):
        if x is None: # Empieza la busqueda desde la raiz si no se proporciona un nodo
            x = self.root
        while not x.leaf:
            i = 0
            while i < len(x.keys) and k >= x.keys[i]:  # Busca el hijo apropiado para descender
                i += 1
            x = x.children[i] # se mueve al hijo apropiado
        for i, key_value in enumerate(x.keys):  # Busca la clave en el nodo hoja
            if key_value[0] == k:
                return x, i # Retornar el nodo y la posicion de la clave si se encuentra
        return None # Retornar 'None' si no se encuentra la clave

    def delete(self, k):
        if not self.root.keys:
            return False # Si la raíz esta vacia no se elimina nada
        return self._delete(self.root, k) # Inicia la eliminacion desde la raiz


    def _delete(self, x, k):
        t = self.t
        i = 0
        if x.leaf: # Si es una hoja, busca y elimina la clave
            while i < len(x.keys) and k > x.keys[i][0]:
                i += 1
            if i < len(x.keys) and x.keys[i][0] == k:
                del x.keys[i]
                return True # Elimina la clave si se encuentra
            return False # Retornar 'False' sino se encuentra la clave
        else:  # Si no es una hoja, encuentra el hijo apropiado para descender
            while i < len(x.keys) and k > x.keys[i]:
                i += 1
            if i == len(x.keys):
                return self._delete(x.children[i], k) # Recursivamente elimina en el hijo apropiado
            if len(x.children[i].keys) < t:
                self._fill(x, i) # Llenar el hijo si tiene menos de t claves
            if i < len(x.keys) and k > x.keys[i]:
                return self._delete(x.children[i + 1], k) # Continuar la eliminacion en el hijo adecuado
            return self._delete(x.children[i], k) #Continuar la eliminacion en el hijo adecuado

    def _fill(self, x, i):
        if i != 0 and len(x.children[i - 1].keys) >= self.t: # Si el hijo izquierdo del nodo en la posicion 'i' tiene al menos 't' claves, toma prestado de el
            self._borrow_from_prev(x, i)
        elif i != len(x.children) - 1 and len(x.children[i + 1].keys) >= self.t:  # Si el hijo derecho del nodo en la posicion 'i' tiene al menos 't' claves, toma prestado de el
            self._borrow_from_next(x, i)
        else: # Si no se puede tomar prestado fusiona con un hermano
            if i != len(x.children) - 1: # Fusiona con el hermano derecho
                self._merge(x, i)
            else:  # Fusiona con el hermano izquierdo
                self._merge(x, i - 1) 

    def _borrow_from_prev(self, x, i):
        child = x.children[i]
        sibling = x.children[i - 1]
        
        if child.leaf:#Si el hijo es una hoja, toma prestada la última clave del hermano izquierdo
            child.keys.insert(0, sibling.keys[-1])
            x.keys[i - 1] = child.keys[0][0]
        else:  # Tomaa prestada la ultima clave del hermano izquierdo y ajusta sus hijos
            child.keys.insert(0, x.keys[i - 1])
            x.keys[i - 1] = sibling.keys[-1]
            if sibling.children:
                child.children.insert(0, sibling.children.pop())
        
        sibling.keys.pop()

    def _borrow_from_next(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        
        if child.leaf: # Si el hijo es una hoja, toma prestada la primera clave del hermano derecho
            child.keys.append(sibling.keys[0])
            x.keys[i] = sibling.keys[1][0] if len(sibling.keys) > 1 else sibling.keys[0][0]
        else: # Tomaa prestada la ultima clave del hermano derecho y ajusta sus hijos
            child.keys.append(x.keys[i])
            x.keys[i] = sibling.keys[0]
            if sibling.children:
                child.children.append(sibling.children.pop(0))
        
        sibling.keys.pop(0)

    def _merge(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]
        
        if not child.leaf:  # Fusiona una clave de 'x' con el hijo y el hermano derecho
            child.keys.append(x.keys[i])
        
        child.keys.extend(sibling.keys) # Fusiona las claves del hermano derecho en el hijo
        if not child.leaf:
            child.children.extend(sibling.children) # Fusiona los hijos del hermano derecho en el hijo
        
        if child.leaf:
            child.next = sibling.next # Ajusta el puntero siguiente si es una hoja
        
        del x.keys[i] # Elimina la clave fusionada de 'x'
        del x.children[i + 1] # Eliminar el hermano derecho de x
        
        if x == self.root and not x.keys: # Si 'x' es la raiz y ya no tiene claves, hace que el hijo sea la nueva raiz
            self.root = child

class BStarNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BStarTree:
    def __init__(self, t):
        self.root = BStarNode(True)
        self.t = t  # Grado mínimo

    def insert(self, k, name):
        root = self.root
        if len(root.keys) == (3 * self.t) - 1:  # Si la raiz esta llena, se crea un nuevo nodo temporal y se ajusta la raiz
            temp = BStarNode()
            self.root = temp
            temp.children.insert(0, root)
            self.split_child(temp, 0)
            self.insert_non_full(temp, k, name) 
        else:
            self.insert_non_full(root, k, name) # Insertar directamente si la raiz no esta llena

    def insert_non_full(self, x, k, name):
        i = len(x.keys) - 1
        if x.leaf: # Si el nodo es una hoja, se inserta la nueva clave en el lugar correcto
            x.keys.append((None, None))
            while i >= 0 and k < x.keys[i][0]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = (k, name)
        else: # Si el nodo no es una hoja, encuentra el hijo adecuado para la clave
            while i >= 0 and k < x.keys[i][0]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (3 * self.t) - 1: # Si el hijo esta lleno, se divide y ajusta el índice
                self.split_child(x, i)
                if k > x.keys[i][0]:
                    i += 1
            self.insert_non_full(x.children[i], k, name)

    def split_child(self, x, i):
        t = self.t
        y = x.children[i]
        
        if len(y.keys) < 3 * t - 1:  # Si el nodo hijo no esta completamente lleno, no se divide
            return
        
        if i > 0 and len(x.children[i-1].keys) < 2 * t - 1:  # Redistribuir claves a la izquierda si es posible
            self.redistribute_left(x, i)
        elif i < len(x.children) - 1 and len(x.children[i+1].keys) < 2 * t - 1:   # Redistribuir claves a la derecha si es posible
            self.redistribute_right(x, i)
        else:   # Si no se puede redistribuir, divide el nodo hijo
            z = BStarNode(y.leaf)
            x.children.insert(i + 1, z)
            
            mid = len(y.keys) // 2 #realiza una división entera, que encuentra el índice central de la lista.
            x.keys.insert(i, y.keys[mid]) #Inserta la clave central de 'y' en la lista de claves 'keys' del nodo padre 'x'
            z.keys = y.keys[mid + 1:]
            y.keys = y.keys[:mid]
            
            if not y.leaf:  # Si el nodo hijo no es una hoja, ajustar los hijos
                z.children = y.children[mid + 1:]
                y.children = y.children[:mid + 1]

    def redistribute_left(self, x, i):
        y = x.children[i]
        z = x.children[i-1]
         # Mover una clave del nodo padre y del nodo hijo al nodo izquierdo
        z.keys.append(x.keys[i-1])
        x.keys[i-1] = y.keys[0]
        
        if not y.leaf:  # Si el nodo no es una hoja, mover tambien el hijo correspondiente
            z.children.append(y.children[0])
            y.children.pop(0)
        
        y.keys.pop(0) #elimina el primer elemento de la lista keys

    def redistribute_right(self, x, i):
        y = x.children[i]
        z = x.children[i+1]
         # Mover una clave del nodo padre y del nodo hijo al nodo derecho
        y.keys.append(x.keys[i])
        x.keys[i] = z.keys[0]
        
        if not y.leaf:  # Si el nodo no es una hoja, mover tambien el hijo correspondiente
            y.children.append(z.children[0])
            z.children.pop(0)
        
        z.keys.pop(0) #elimina el primer elemento de la lista keys

    def search(self, k, x=None):
        if x is None:  # Si no se proporciona un nodo para comenzar la búsqueda, comienza en la raíz
            x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]:  # Recorre las claves del nodo hasta encontrar una clave mayor o igual a 'k'
            i += 1
        if i < len(x.keys) and k == x.keys[i][0]:  # Si encuentra la clave 'k' en el nodo actual, devuelve el nodo y el índice de la clave
            return x, i
        elif x.leaf:  # Si no encuentra la clave y el nodo actual es una hoja, la clave no está en el árbol
            return None
        else:   # Si no encuentra la clave y el nodo no es una hoja, busca en el hijo correspondiente
            return self.search(k, x.children[i])

    def delete(self, k):
        if not self.root.keys: # Si la raíz está vacía, no hay nada que eliminar
            return False
        self._delete(self.root, k)  # Llama al método interno para manejar la eliminación
        if len(self.root.keys) == 0 and not self.root.leaf:   # Si la raíz queda vacía y no es una hoja, el primer hijo queda como la nueva raiz
            self.root = self.root.children[0]
        return True

    def _delete(self, x, k):
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i][0]:  # Encuentra la posición de la clave 'k' en el nodo actual
            i += 1
        if x.leaf:
            if i < len(x.keys) and x.keys[i][0] == k:  # Si la clave se encuentra en el nodo, se elimina
                x.keys.pop(i)
                return
            return
        if i < len(x.keys) and x.keys[i][0] == k: # Si la clave está en el nodo actual
            return self._delete_internal_node(x, k, i)
        elif len(x.children[i].keys) >= t: # Si el hijo correspondiente tiene suficientes claves, se llama recursivamente
            self._delete(x.children[i], k)
        else:   # Si el hijo no tiene suficientes claves, se intenta redistribuir o fusionar
            if i > 0 and len(x.children[i - 1].keys) >= t:
                self._borrow_from_prev(x, i)
            elif i < len(x.children) - 1 and len(x.children[i + 1].keys) >= t:
                self._borrow_from_next(x, i)
            else:  # Fusionar con el hermano derecho o izquierdo según el índice
                if i < len(x.children) - 1:
                    self._merge(x, i)
                else:
                    self._merge(x, i - 1)
            self._delete(x.children[i], k)   # Después de la fusión o redistribución, eliminar recursivamente

    def _delete_internal_node(self, x, k, i):
        if x.leaf: # Si el nodo es una hoja, elimina la clave directamente
            if x.keys[i][0] == k:
                x.keys.pop(i)
            return
        if len(x.children[i].keys) >= self.t: # Si el hijo izquierdo tiene suficientes claves
            x.keys[i] = self._get_pred(x.children[i])
            self._delete(x.children[i], x.keys[i][0])
        elif len(x.children[i + 1].keys) >= self.t:  # Si el hijo derecho tiene suficientes claves
            x.keys[i] = self._get_succ(x.children[i + 1])
            self._delete(x.children[i + 1], x.keys[i][0])
        else:  # Si ninguno tiene suficientes claves, fusionar y eliminar recursivamente
            self._merge(x, i)
            self._delete(x.children[i], k)

    def _borrow_from_prev(self, x, i):  # Toma una clave del hermano izquierdo y ajusta el nodo actual
        child = x.children[i] 
        sibling = x.children[i - 1]
        
        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop()
        
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x, i):  # Toma una clave del hermano derecho y ajusta el nodo actual
        child = x.children[i]
        sibling = x.children[i + 1]
        
        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)
        
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge(self, x, i):  # Fusiona el nodo hijo actual con el hermano derecho
        child = x.children[i]
        sibling = x.children[i + 1]
        
        child.keys.append(x.keys[i])
        child.keys.extend(sibling.keys)
        
        if not child.leaf:
            child.children.extend(sibling.children)
        
        x.keys.pop(i)
        x.children.pop(i + 1)

    def _get_pred(self, x):  # Obtiene el predecesor (la clave más grande en el subárbol izquierdo)
        while not x.leaf:
            x = x.children[-1]
        return x.keys[-1]

    def _get_succ(self, x):   # Obtiene el sucesor (la clave más pequeña en el subárbol derecho)
        while not x.leaf:
            x = x.children[0]
        return x.keys[0]
    

def main_menu():
    while True:
        print("\nMenú Principal")
        print("1. Árbol AVL")
        print("2. Árbol B")
        print("3. Árbol B+")
        print("4. Árbol B*")
        print("5. Salir")
        choice = input("Seleccione una opción (1-5): ")

        if choice == '1':
            filename = input("Ingrese el nombre del archivo de comandos para AVL: ")
            process_file_avl(filename)
        elif choice == '2':
            t = int(input("Ingrese el grado mínimo del árbol B (t): "))
            filename = input("Ingrese el nombre del archivo de comandos para B-tree: ")
            process_file_b(filename, t)
        elif choice == '3':
            t = int(input("Ingrese el grado mínimo del árbol B+ (t): "))
            filename = input("Ingrese el nombre del archivo de comandos para B+ tree: ")
            process_file_bplus(filename, t)
        elif choice == '4':
            t = int(input("Ingrese el grado mínimo del árbol B* (t): "))
            filename = input("Ingrese el nombre del archivo de comandos para B* tree: ")
            process_file_bstar(filename, t)
        elif choice == '5':
            print("Gracias por usar el programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


def process_file_avl(filename):
    tree = AVLTree() #crea un instancia en el AVLTree
    root = None #inicializa la raiz del arbol como NONE

    with open(filename, 'r') as file: #abre el archivo especifico
        lines = file.readlines() #lee todas las lineas del archivo
    
    pattern_insert = re.compile(r'Insert:\{id:(\d+),nombre:"(.+?)"\}') #Para comandos de insercion
    pattern_search_delete = re.compile(r'(Search|Delete):\{id:(\d+)\}') #para comandos de busqueda y eliminacion
    #el diccionario "timings" se utiliza para almacenar los tiempos de insercion, busqueda y eliminacion
    timings = { 
        'Insert': [],
        'Search': [],
        'Delete': []
    }

    log_entries = [] #almacena las entradas del log de las operaciones realizadas

    for line in lines:
        line = line.strip()
        if match := pattern_insert.match(line): 
            key = int(match.group(1)) #id
            name = match.group(2) #nombre
            start_time = time.time() #midel el tiempo de la insercion y se guarda en el log
            start_dt = datetime.datetime.now()
            root = tree.insert(root, key, name)
            end_time = time.time()
            end_dt = datetime.datetime.now()
            elapsed_time = end_time - start_time #tiempo transcurrido en la operacion
            timings['Insert'].append((key, elapsed_time))
            log_entries.append(f'Insert: Inicio: {start_dt}, Fin: {end_dt}, Tiempo: {elapsed_time:.6f} segundos, Id: {key}, Nombre: {name}') #estructura insert en el log
        elif match := pattern_search_delete.match(line): #extrae el comando serach o delete y el id
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
                found = result is not None #indica si se encontro o no
                name = result.name if found else "" #devuelve el nombre si se encontro o no
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
               

    log_filename = f"log-AVLTree-{filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt" #estructura del nombre del archivo log
    with open(log_filename, 'w') as log_file:
        log_file.write('\n'.join(log_entries))

    with open('timing_results.txt', 'w') as f: 
        
        for operation in ["Insert", "Search", "Delete"]:
            f.write(f'\n{operation}:\n')
            #encuentras el top 10 de las operaciones mas rapidas y mas tardadas en realizarce
            sorted_timings = sorted(timings[operation], key=lambda x: x[1])
            top_10_max = sorted_timings[-10:]
            top_10_min = sorted_timings[:10]
            average_timing = sum(time for _, time in sorted_timings) / len(sorted_timings) if sorted_timings else 0 #tiempo promedio de las operaciones

            f.write('Top 10 maximos:\n')
            for key, elapsed_time in reversed(top_10_max):
                f.write(f'Id: {key}, Tiempo: {elapsed_time:.6f} segundos\n')
            
            f.write('Top 10 minimos:\n')
            for key, elapsed_time in top_10_min:
                f.write(f'Id: {key}, Tiempo: {elapsed_time:.6f} segundos\n')
            
            f.write(f'Promedio: {average_timing:.6f} segundos\n')
            f.write('\n')

        f.write('Tiempo total de todas las operaciones:\n') #tiempo total de cada tipo de operacion
        f.write(f'Insert: {sum(time for _, time in timings["Insert"]):.6f} segundos\n')
        f.write(f'Search: {sum(time for _, time in timings["Search"]):.6f} segundos\n')
        f.write(f'Delete: {sum(time for _, time in timings["Delete"]):.6f} segundos\n')

    with open('timing_results.txt', 'r') as f: 
        timing_results_content = f.read()
        print(timing_results_content)



def process_file_b(filename, t):
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


def process_file_bplus(filename, t):
    tree = BPlusTree(t)

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

    log_filename = f"log-BPlusTree-{filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(log_filename, 'w') as log_file:
        log_file.write('\n'.join(log_entries))

    with open('timing_resultsBPlus.txt', 'w') as f:
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

    with open('timing_resultsBPlus.txt', 'r') as f:
        timing_results_content = f.read()
        print(timing_results_content)

def process_file_bstar(filename, t):
    tree = BStarTree(t)

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

    log_filename = f"log-BStarTree-{filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(log_filename, 'w') as log_file:
        log_file.write('\n'.join(log_entries))

    with open('timing_resultsBStar.txt', 'w') as f:
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

    with open('timing_resultsBStar.txt', 'r') as f:
        timing_results_content = f.read()
        print(timing_results_content)


if __name__ == "__main__":
    main_menu()

