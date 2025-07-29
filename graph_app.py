import sys
import random
import os
import matplotlib.pyplot as plot
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from sage.all import Graph
from sage.groups.perm_gps.permgroup_named import SymmetricGroup
from sage.graphs.graph_generators import graphs

def is_rigid(G):
    vertices = list(G.vertices())
    n = len(vertices)
    verTo = {}
    for i in range(n):
        verTo[vertices[i]] = i

    edges = set()
    for u, v in  G.edges(labels=False):
        ui = verTo[u]
        vi = verTo[v]
        if ui < vi:
            edges.add((ui, vi))
        else:
            edges.add((vi, ui))


    mapping = [0] * n

    while True:
        isIdentity = True
        for i in range(n):
            if mapping[i] != i:
                isIdentity = False
                break

        if not isIdentity:
            valid = True
            for (ui, vi) in edges:
                ei = mapping[ui]
                ej = mapping[vi]

                if ei < ej:
                    edg = (ei, ej)
                else:
                    edg = (ej, ei)
                if edg not in edges:
                    valid = False
                    break


            if valid:
                return False

        pos = n - 1
        while pos >= 0:
            mapping[pos] += 1
            if mapping[pos] < n:
                break
            mapping[pos] = 0
            pos =- 1

        if pos < 0:
            break

    return True


def is_asymmetric(G):
    return G.automorphism_group().is_trivial()



def is_bipartite(G):
    return G.is_bipartite()



def is_strongly_asymmetric(G):

	vertices = list(G.vertices())
	visited = {}

	subsets = [[]]
	for ver in vertices:
		newSubs = []
		for sub in subsets:
			newSub = sub + [ver]
			newSubs.append(newSub)
		subsets.extend(newSubs)

	for subset in subsets:
		size = len(subset)

		subgraph = G.subgraph(subset)

		if size not in visited:
			visited[size] = []

		for i in visited[size]:
			if subgraph.is_isomorphic(i):
				return False

		visited[size].append(subgraph)

	return True



def is_minimal_asymmetric(G):
	if not is_asymmetric(G):
		return False
	vertices = list(G.vertices())

	subsets = [[]]
	for ver in vertices:
		newSubs = []
		for sub in subsets:
			newSub = sub + [ver]
			newSubs.append(newSub)
		subsets.extend(newSubs)

	for sub in subsets:
		if 2 <= len(sub) < len(vertices):
			subset = G.subgraph(sub)
			if subset.automorphism_group().is_trivial():
				return False

	return True



def createKgraph(G):
	X = G.vertices()

	M = []
	edges = G.edges(labels = False)
	for edge in edges:
		u = edge[0]
		v = edge[1]
		M.append([u,v])
	return X, M



def asym_hypergraph(X, M):
	n = len(X)

	verToInd = {}
	for i in range(len(X)):
		verToInd[X[i]]  = i

	edges = []
	for edge in M:
		newEdge = []
		for v in edge:
			newEdge.append(verToInd[v])
		newEdge.sort()
		edges.append(newEdge)

	G = SymmetricGroup(n)

	for p in G:
		if p.is_one():
			continue

		transEdges = []
		for edge in edges:
			newEdge =  []
			for i in edge:
				newEdge.append(p(i))
			newEdge.sort()
			transEdges.append(newEdge)

		if sorted(transEdges) == sorted(edges):
			return False
	return True



def is_strongly_minimal_asymmetric(X, M, k):
	if not asym_hypergraph(X, M):
		return False

	subsets = [[]]

	for edge in M:
		newSubs = []
		for i in subsets:
			newSub = i + [edge]
			newSubs.append(newSub)
		subsets.extend(newSubs)

	for sub in subsets:
		if len(sub) == 0 or len(sub) == len(M):
			continue

		visited_ver =  []
		for edge in sub:
			for ver in edge:
				if ver not in visited_ver:
					visited_ver.append(ver)

		if len(visited_ver) < 2:
			continue

		if asym_hypergraph(visited_ver, sub):
			return False

	return True



def is_delta_asymmetric(G, delta=0.3):
	n = G.order()
	m = G.size()
	V = G.vertices()

	setOfEdges = []
	edges = G.edges(labels=False)

	for u, v in edges:
		if u < v:
			setOfEdges.append((u,v))
		else:
			setOfEdges.append((v,u))

	fractions = [0.2, 0.4, 0.6]
	kVal = []
	
	for f in fractions:
		k = int(f * n)
		if k < 1:
			k = 1
		kVal.append(k)
	for k in kVal:
		for i in range(5):
			selected = []
			used = []
			
			while len(selected) < k:
				index = random.randint(0, len(V) - 1)
				if index not in used:
					selected.append(V[index])
					used.append(index)
			
			shuffled = selected[:]
			n = len(shuffled)
			
			for j in range(n - 1, 0, -1):
				q = random.randint(0, j)
				temp = shuffled[j]
				shuffled[j] = shuffled[q]
				shuffled[q] = temp

			map = {}
			
			for q in range(len(selected)):
				map[selected[q]] = shuffled[q]

			for v in V:
				if v not in map:
					map[v] = v

			permEdges = []
			for u, v in edges:
				newU = map[u]
				newV = map[v]
				if newU < newV:
					permEdges.append((newU, newV))
				else:
					permEdges.append((newV, newU))

			difference = 0
			for edge in permEdges:
				if edge not in setOfEdges:
					difference += 1

			for edge in setOfEdges:
				if edge not in permEdges:
					difference +=1

			lowerBound = delta * (k / n) * m
			if difference < lowerBound:
				return False
	return True



def degree_of_asymmetry(G):
    n = G.order()
    V = list(G.vertices())
    if not is_asymmetric(G):
        return 0

    edges = set()
    for u, v in G.edges(labels = False):
        if u < v:
            edges.add((u, v))
        else:
            edges.add((v, u))

    changes = None

    for H in graphs(n):
        if H.automorphism_group().is_trivial():
            continue
        symEdges = set()
        for u, v in H.edges(labels = False):
            if u < v:
                symEdges.add((u, v))
            else:
                symEdges.add((v, u))

        deleted = 0
        for e in edges:
            if e not in symEdges:
                deleted += 1

        added = 0
        for e in symEdges:
            if e not in edges:
                added +=1

        res = deleted + added
        if changes is None or res < changes:
            changes = res

    if changes is None:
        return len(edges)
    return changes 



def all_subsets(lst, k):
    if k == 0:
        return [[]]
    if not lst:
        return []
    first = lst[0]
    rest = lst[1:]
    include = []
    subs = all_subsets(rest, k - 1)
    for i in subs:
        include.append([first] + i)
    exclude = all_subsets(rest, k)
    return include + exclude


def A_G(G):
    n = G.order()
    V = G.vertices()
    edges = G.edges(labels = False)
    edgs = []

    for u, v in edges:
        if u < v:
            edgs.append((u,v))
        else:
            edgs.append((v, u))

    allEdges = []
    for i in range(n):
        for j in range(i+1, n):
            allEdges.append((V[i], V[j]))

    nEdges = []
    for i in allEdges:
        if i not in edgs:
            nEdges.append(i)

    sum = len(allEdges)
    for i in range(1, sum+1):
        for j in range(0, min(i, len(edgs))+1):
            remList =  all_subsets(edgs, j)
            addList = all_subsets(nEdges, i - j)
            for k in range(len(remList)):
                remove = remList[k]
                for l in range(len(addList)):
                    add = addList[l]
                    newEdges = []
                    for e in edges:
                        if e not in remove:
                            newEdges.append(e)
                    for e in add:
                        if e not in newEdges:
                            newEdges.append(e)
                    H = Graph(newEdges)
                    if not H.automorphism_group().is_trivial():
                        return i
    return sum + 1

def is_maximally_asymmetric(G):
    if not is_asymmetric(G):
        return False

    n = G.order()
    ag = A_G(G)
    maxAG = 0

    for H in graphs(n):
        if is_asymmetric(H):
            val = A_G(H)
            if val > maxAG:
                maxAG = val

    return ag == maxAG


def gen_combinations(arr, k):
    res = []
    def backtrack(start, path):
        if len (path) == k:
            res.append(path[:])
            return
        for i in range(start, len(arr)):
            path.append(arr[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return res


def gen_permut(arr):
    res = []
    def permute(path, used):
        if len(path) == len(arr):
            res.append(path[:])
            return
        for i in range(len(arr)):
            if not used[i]:
                used[i] = True
                path.append(arr[i])
                permute(path, used)
                path.pop()
                used[i] = False
    permute([], [False] * len(arr))
    return res


def asymmetric_depth(G):
    n = G.order()
    V = list(G.vertices())
    if n < 2:
        return 0


    for k in range(n, 1, -1):
        aSubs = gen_combinations(V, k)
        for i in range(len(aSubs)):
            A = aSubs[i]
            for j in range(len(aSubs)):
                B = aSubs[j]
                if set(A) == set(B):
                    continue
                permutations = gen_permut(B)
                for perm in permutations:
                    isIdentity = True
                    for idx in range(k):
                        if A[idx] != perm[idx]:
                            isIdentity = False
                            break
                    if isIdentity:
                        continue
                    bijection = {}
                    for idx in range(k):
                        bijection[A[idx]] = perm[idx]
                    partAut = True
                    for p1 in range(k):
                        for p2 in range(k):
                            if p1 == p2:
                                continue
                            u1, v1 = A[p1], A[p2]
                            u2, v2 = bijection[u1], bijection[v1]
                            if G.has_edge(u1, v1) != G.has_edge(u2, v2):
                                partAut = False
                                break
                        if not partAut:
                            break
                    if partAut:
                        return n - k
    return n - 1


def negative_degree_of_asymmetry(G):
    if not is_asymmetric(G):
        return 0

    edges = G.edges(labels = False)
    n = len(edges)
    if n == 0:
        return 0

    for i in range (1, n + 1):
        edgeSubs = gen_combinations(edges,i)
        for set in edgeSubs:
            newEdges = []
            for e in edges:
                if e not in set:
                    newEdges.append(e)
            H = Graph(newEdges)
            if not H.automorphism_group().is_trivial():
                return i
    return n


def positive_degree_of_asymmetry(G):
    if not is_asymmetric(G):
        return 0

    V = list(G.vertices())
    edges = set()
    for u, v in G.edges(labels = False):
        if u < v:
            edges.add((u, v))
        else:
            edges.add((v, u))

    nEdges = []
    n = len(V)
    for i in range(n):
        for j in range(i + 1, n):
            if (V[i], V[j]) not in edges:
                nEdges.append((V[i], V[j]))
    m = len(nEdges)
    if m == 0:
        return 0

    for i in range(1, m + 1):
        addSets = gen_combinations(nEdges, i)
        for set in addSets:
            newEdges = list(G.edges(labels = False))
            for e in set:
                if e not in set:
                    newEdges.append(e)
            H = Graph(newEdges)
            if not H.automorphism_group().is_trivial():
                return i
    return m



class GraphApp(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Graph Checker")
		self.setGeometry(100, 100, 600, 300)

		self.main_layout = QHBoxLayout()
		self.layout = QVBoxLayout()

		self.label = QLabel("Enter graph6 string:")
		self.layout.addWidget(self.label)

		self.graph_input = QLineEdit()
		self.layout.addWidget(self.graph_input)

		self.check_button = QPushButton("Check Graph")
		self.check_button.clicked.connect(self.check_graph)
		self.layout.addWidget(self.check_button)

		self.table = QTableWidget()
		self.table.setColumnCount(2)
		self.table.setHorizontalHeaderLabels(["Definition", "Result"])
		self.layout.addWidget(self.table)

		self.graph_img = QLabel()
		self.graph_img.setFixedSize(300, 300)
		self.graph_img.setStyleSheet("border: 1px solid gray")

		self.main_layout.addLayout(self.layout)
		self.main_layout.addWidget(self.graph_img)

		self.setLayout(self.main_layout)

	def check_graph(self):
		graph_str = self.graph_input.text().strip()
		try:
			G = Graph(graph_str, format='graph6')
		except Exception:
			return

		X, M = createKgraph(G)

		results = [
    			("Rigid", is_rigid(G)),
    			("Asymmetric", is_asymmetric(G)),
    			("Bipartite", is_bipartite(G)),
    			("Strongly Asymmetric", is_strongly_asymmetric(G)),
    			("Minimal Asymmetric", is_minimal_asymmetric(G)),
    			("Strongly Minimal Asymmetric", is_strongly_minimal_asymmetric(X, M, 2)),
    			("Robustly Asymmetric", is_delta_asymmetric(G, delta = 0.3)),
    			("Maximally Asymmetric", is_maximally_asymmetric(G)),
    			("The degree of asymmetry", degree_of_asymmetry(G)),
    			("Asymmetric depth", asymmetric_depth(G)),
    			("Negative degree of asymmetry", negative_degree_of_asymmetry(G)),
    			("Positive degree of asymmetry", positive_degree_of_asymmetry(G))
       		]

		self.table.setRowCount(len(results))
		for i, (definition, passed) in enumerate(results):
			self.table.setItem(i, 0, QTableWidgetItem(definition))
			if isinstance(passed, bool):
				item = QTableWidgetItem("\u2713" if passed else "\u2717")
				item.setTextAlignment(Qt.AlignCenter)
			else:
				item = QTableWidgetItem(str(passed))

			self.table.setItem(i, 1, item)

		plot = G.plot()
		img = "/tmp/graph_img.png"
		plot.save(img)

		if os.path.exists(img):
			pixmap = QPixmap(img)
			pixmap = pixmap.scaled(self.graph_img.width(), self.graph_img.height())
			self.graph_img.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
