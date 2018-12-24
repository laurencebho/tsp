import re
#REQUIRES TOUR FILES IN DATA/
files = ["data/NEWAISearchfile012.txt", "data/NEWAISearchfile017.txt",
 "data/NEWAISearchfile021.txt", "data/NEWAISearchfile026.txt", 
 "data/NEWAISearchfile042.txt", "data/NEWAISearchfile048.txt", 
 "data/NEWAISearchfile058.txt", "data/NEWAISearchfile175.txt", 
 "data/NEWAISearchfile180.txt", "data/NEWAISearchfile535.txt"]

def read_file(filename):
	with open(filename, 'r') as f:
		name = re.findall(r'\w+', f.readline())[1] # NAME = name -> name
		size = re.findall(r'[0-9]+', f.readline())[0]
		numbers = []
		for line in f.readlines():
			for n in re.findall(r'[0-9]+', line):
				numbers.append(n)

	size = int(size)
	numbers = [int(n) for n in numbers]

	M = [[0] * size for _ in range(size)]
	k = 0
	for i in range(size):
		for j in range(i+1, size):
			d = numbers[k]
			M[i][j] = d
			M[j][i] = d
			k += 1

	print(name)
	print(str(size))
	#print(str(M))
	return name, size, M