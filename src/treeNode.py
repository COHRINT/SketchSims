#from queue import Queue
import numpy as np; 
import time

class Node: 

	def __init__(self,parent=None,ident=None):
		self.children = []; 
		self.data = []; 
		self.parent = parent; 
		self.id = ident
		self.Q = 0; 
		self.N = 0; 


	def __str__(self):
		a = "Node: {}\n".format(self.id) + "Children: {}\n".format(len(self.children)) + "Data Points: {}\n".format(len(self.data))
		return a; 


	def __getitem__(self,key):
		return self.children[key]; 

	def getChildByID(self,ident):
		for n in self.children:
			if(n.id == ident):
				return n; 
		return -1; 

	def getChildrenIDs(self):
		allID = [a.id for a in self]; 
		return allID; 

	def makeRoot(self):
		self.parent = None; 


	def addChild(self,n):
		n.parent = self; 
		self.children.append(n); 
		return n; 

	def addChildID(self,ident):
		n = Node(); 
		n.parent = self; 
		n.id = ident; 
		self.children.append(n); 
		return n; 



	def traverse(self):
		res = []; 
		res.append(self.id)
		#do a thing
		for child in self:
			res.extend(child.traverse())
		return res

	def gatherAllNodes(self):
		res = []; 
		res.append(self)
		#do a thing
		for child in self:
			res.extend(child.gatherAllNodes())
		return res

	def BFS(self,goal):
		q = Queue(); 
		q.put(self); 
		disc = []; 

		while(not q.empty()):
			v = q.get(); 
			if(v.id == goal):
				return v; 
			for a in v.children:
				if(a not in disc):
					disc.append(a); 
					q.put(a); 


	def DFS(self,goal):
		stack = []; 
		disc = []; 
		stack.append(self); 

		while(len(stack) > 0):
			v = stack.pop(); 
			if(v.id == goal):
				return v; 
			if(v not in disc):
				disc.append(v); 
				for a in v.children:
					stack.append(a); 
				

	def hasChildren(self):
		if(not self.children):
			return False; 
		return True; 

def testNodes():
	root = Node(ident=0); 

	a = time.clock(); 
	root.addChild(Node(ident=1)); 
	b = time.clock(); 
	print("Adding Time: {0:.2f} seconds".format(b-a))

	root.addChild(Node(ident=2)); 
	root.addChild(Node(ident=3)); 
	root.addChild(Node(ident=4)); 

	root.children[1].addChild(Node(ident=5)); 

	ans = root.traverse(); 
	print(ans); 

	ans = root.BFS(2); 
	print(ans); 

	ans = root.BFS(2)
	print(ans); 



buildCount = 0; 

def buildTree(root,branch=2,depth = 10):
	global buildCount; 

	if(depth == 0):
		return; 

	for i in range(0,branch):
		a = root.addChild(Node(ident=buildCount));
		buildCount+=1;  
		buildTree(a,branch,depth-1); 



def timingTest():

	global buildCount; 
	buildCount = 0; 
	root = Node(ident=0); 
	buildCount += 1; 

	buildTree(root,branch=2,depth=10);

	a = time.clock(); 
	ans = root.traverse(); 
	b = time.clock(); 
	print("Traversal: {0:.3f} seconds".format(b-a)); 

	a = time.clock(); 
	ans = root.BFS(11); 
	b = time.clock(); 
	print("BFS: {0:.3f} seconds".format(b-a)); 

	a = time.clock(); 
	ans = root.DFS(11); 
	b = time.clock(); 
	print("DFS: {0:.3f} seconds".format(b-a)); 





if __name__ == '__main__':
	#testNodes(); 

	timingTest(); 

	#t = Node(); 