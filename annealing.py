import random
import time
from reader import read_file, files
from math import log, exp, tanh

def P(e, e_prime, T):
	if e >= e_prime:
		return 1
	return exp((e - e_prime) / T) #e replaced with 3

def E(s, M):
	e = 0
	for i in range(len(s) - 1):
		e += M[s[i]][s[i + 1]]
	e += M[s[-1]][s[0]] #edge back to beginning
	return e

def get_random_neighbour2(s):
	size = len(s)
	a = int(random.random() * size // 1)
	while True:
		b = int(random.random() * size // 1)
		if a != b:
			break
	s_prime = s[:] #create hard copy of s
	s_prime[a], s_prime[b] = s_prime[b], s_prime[a] #swap 2 nodes
	return s_prime

def get_random_neighbour(s): #essentially 2-opt
	size = len(s)
	a = random.randint(1, size-1)
	while True:
		b = random.randint(1, size-1)
		if a != b:
			break
	if b < a:
		a, b = b, a
	s_prime = s[:] #create hard copy of s
	s_prime[a:b + 1] = reversed(s_prime[a:b + 1])
	return s_prime

def get_random_neighbour3(s):
	size = len(s)
	s_prime = s[:] #create hard copy of s
	for i in range(1, size):
		b = int(random.random() * (size - 1)  // 1) + 1
		s_prime[i], s_prime[b] = s_prime[b], s_prime[i]
	return s_prime

def temperature(k, t, t_start):
	eps = 0.0004
	return t_start / (1 + exp(k * eps))
	
	if t < 5:
		return t - eps
	#return t / (1 + 0.00001 * t)
	#return t_start * (1 + 1/1500) ** -k
	#return t_start / (1 + k * eps)
	#return t_start / (1 + eps * k * log(1 + k))
	#t_start / (1 + log(1+k))

def choose_start_temp(s, M): #given arbitrary start state, tries to find an acceptable start temperature
#this is computed as the max energy difference between s and 1000 other randomly chosen neighbours
	largest = 0
	for _ in range(1000):
		s_prime = get_random_neighbour2(s)
		diff = abs(E(s_prime, M) - E(s, M))
		if diff > largest:
			largest = diff
	return largest

def opt_2(tour, size, M):
	length = get_tour_length(tour, M)
	best = length
	best_tour = tour
	for i in range(size - 2):
		for j in range(i + 1, size - 1):
			neighbour = tour[:] #create hard copy of tour
			neighbour[i:j + 1] = reversed(neighbour[i:j + 1])
			neighbour_length = length - M[tour[i - 1]][tour[i]] - M[tour[j]][tour[-1 * (size - j - 1)]] + M[tour[i - 1]][tour[j]] + M[tour[i]][tour[-1 * (size - j - 1)]]
			#print(neighbour_length - get_tour_length(neighbour, M))
			#print(str(i) + ", " + str(j) + ", " + str(-1 * (size - j - 1)))
			if  neighbour_length < best:
				best  = neighbour_length
				best_tour = neighbour
	return best_tour, best

def get_tour_length(tour, M):
	dist = 0
	for i in range(-1, len(tour) - 1):
		dist += M[tour[i]][tour[i + 1]]
	return dist


def annealing(filename):
	start = time.time()
	name, size, M = read_file(filename)
	s = [i for i in range(size)]
	s_best = s[:]
	curr_length = E(s, M)
	best_length = E(s_best, M)
	T_start = choose_start_temp(s, M)
	T = T_start
	print("Start temperature: " + str(T_start))
	k = 0
	while T > 0.001:
		print(str(best_length) + " " + str(T))
		T = temperature(k, T, T_start)
		s_prime = get_random_neighbour(s)
		s_prime, new_length = opt_2(s_prime, size, M) #perform local search to find best neighbour
		#new_length = E(s_prime, M)
		if P(curr_length, new_length, T) >= random.random():
			s = s_prime
			curr_length = new_length
			if new_length < best_length:
				s_best = s[:]
				best_length = E(s_best, M)
				#print(str(E(s_best, M)) + ", " + str(T))
		k += 1
	end = time.time()
	print(best_length)
	print(s_best)
	print("Time taken: " + str(end - start))
	save_tour(size, best_length, s_best)
	return best_length, s_best

def save_tour(size, dist, tour):
	with open("./annealing" + str(size) + "_" + str(dist) + ".txt", "w+") as f:
		f.write("dist: " + str(dist) + "\n")
		for i, _ in enumerate(tour):
			tour[i] += 1
		f.write(str(tour))

if __name__ == "__main__":
	for i in range(10):
		annealing(files[i])