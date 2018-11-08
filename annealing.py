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

def get_random_neighbour2(s):
	size = len(s)
	a = int(random.random() * (size - 1) // 1) + 1
	while True:
		b = int(random.random() * (size - 1)  // 1) + 1
		if a != b:
			break
	if b < a:
		a, b = b, a
	s_prime = s[:] #create hard copy of s
	r = int((b-a) // 2)
	for i in range(r):
		s_prime[a + i] , s_prime[b-i] = s_prime[b - i], s_prime[a + i]
	return s_prime

def get_random_neighbour3(s):
	size = len(s)
	s_prime = s[:] #create hard copy of s
	for i in range(1, size):
		b = int(random.random() * (size - 1)  // 1) + 1
		s_prime[i], s_prime[b] = s_prime[b], s_prime[i]
	return s_prime

def temperature(k, t, t_start):
	eps = 0.000001
	#return (t_start / (1 + eps * k ** 2))
	#if t < t_start * 0.7:
	return t_start / (exp(1 + k * eps))
	#return t - t_start * 0.0000005
	#return t_start / (1 + log(1 + k))

def choose_start_temp(s, M): #given arbitrary start state, tries to find an acceptable start temperature
#this is computed as the max energy difference between s and 20 other randomly chosen neighbours
	largest = 0
	for _ in range(20):
		s_prime = get_random_neighbour2(s)
		diff = abs(E(s_prime, M) - E(s, M))
		if diff > largest:
			largest = diff
	return largest

def choose_start_temp_2(state, M): #picks temp to match an acceptance ratio
	s = state[:]
	chi = 0.8
	successes = 0
	failures = 0
	for _ in range(1000):
		s_prime = get_random_neighbour(s)
		if P(E(s, M), E(s_prime, M), T) >= random.random():
			s = s_prime
			successes += 1
		else:
			failures += 1

def annealing(filename):
	start = time.time()
	name, size, M = read_file(filename)
	s = [i for i in range(size)]
	s_best = [i for i in range(size)]
	curr_length = E(s, M)
	best_length = E(s_best, M)
	T_start = choose_start_temp(s, M)
	T = T_start
	print("Start temperature: " + str(T_start))
	k = 0
	while T > 0.0001:
		T = temperature(k, T, T_start)
		s_prime = get_random_neighbour2(s)
		new_length = E(s_prime, M)
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
	return s_best

for i in range(10):
	annealing(files[i])


'''
NOTES:
	> Kirkpatrick paper suggests largest abs(E' - E) as the starting temperature. Currently trying a simplified version of this
'''
