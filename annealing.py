import random
import time
from reader import read_file, files

def P(e, e_prime, T):
	if e >= e_prime:
		return 1
	return 3 ** ((e - e_prime) / T) #e replaced with 3

def E(s, M):
	e = 0
	for i in range(len(s) - 1):
		e += M[s[i]][s[i + 1]]
	e += M[s[-1]][s[0]] #edge back to beginning
	return e

def get_random_neighbour(s):
	size = len(s)
	a = int(random.random() * size // 1)
	while True:
		b = int(random.random() * size // 1)
		if a != b:
			break
	s_prime = s[:] #create hard copy of s
	s_prime[a], s_prime[b] = s_prime[b], s_prime[a] #swap 2 nodes
	return s_prime

def temperature(r, size):
	return (1 - r) * size * 10


def annealing(filename):
	start = time.time()
	name, size, M = read_file(filename)
	s = [i for i in range(size)]
	kmax = 100000
	for k in range(kmax):
		T = temperature(k / kmax, size)
		s_prime = get_random_neighbour(s)
		if P(E(s, M), E(s_prime, M), T) >= random.random():
			s = s_prime
	end = time.time()
	print(E(s, M))
	print(s)
	print("Time taken: " + str(end - start))
	return s

for i in range(10):
	annealing(files[i])
