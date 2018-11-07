import re
import random
import time
import numpy as np
from reader import read_file, files

def select_node(node, tour, size, M, pheromones):
	alpha = 1 #can be tweaked
	beta = 4
	index = size * node #start index in flattened matrix
	P_row = pheromones[index:index + size] #take relevant row out of matrix
	distances = M[index:index + size]
	weights = [0] * (size)
	total = 0
	prev = 0
	largest = 0
	for i in range(size):
		if i == node or i in tour:
			weights[i] = 0
		else:
			weight = P_row[i]**alpha * (1/distances[i])**beta
			total += weight
			weights[i] = weight + prev
			prev = weight + prev
			if prev > largest:
				largest = prev
	pheromones[index:index + size] = P_row #update portion of flattened matrix
	M[index:index + size] = distances
	for weight in weights:
		weight = weight / total
	choice = random.random() * largest
	for i, weight in enumerate(weights):
		if choice - weight < 0:
			return i


def update_pheromones(tours, tour_lengths, size, pheromones):
	rho = 0.001 #evaporation coefficient
	q = size * 20 #constant
	for i in range(size):
		for j in range(size):
			pheromones[i * size + j] *= (1 - rho)
	for i, tour in enumerate(tours):
		for j in range(0, len(tour) - 1):
			pher = q / tour_lengths[i]
			pheromones[tour[j] * size + tour[j + 1]] += pher
			pheromones[tour[j + 1] * size + tour[j]] += pher

def update_tours(tours, tour_lengths, size, M, pheromones):
	for _ in range(size - 1):
		for j, tour in enumerate(tours):
			new_node = select_node(tour[-1], tour, size, M, pheromones)
			tour.append(new_node)
			tour_lengths[j] += M[tour[-1] * size + tour[-2]] #add edge length to current tour length

def aco(filename):
	start = time.time()
	name, size, M = read_file(filename)
	M = flatten(M)
	ants = int((size * 0.5) // 1) #number of ants
	P = [[0.1] * size for _ in range(size)] #initialise pheromones matrix
	P = flatten(P)
	for _ in range(1000):
		tours = [[0] for _ in range(ants)]
		tour_lengths = [0] * ants
		update_tours(tours, tour_lengths, size, M, P)
		update_pheromones(tours, tour_lengths, size, P)
	end = time.time()
	print("1000 iterations completed in " + str(end - start))
	print(tour_lengths)

def flatten(mat):
	flattened = []
	for a in mat:
		for e in a:
			flattened.append(e)
	return flattened


if __name__ == "__main__":
	for i in range(10):
		aco(files[i])

'''
NOTES:
	> Wikipedia mentions alpha (for node selection) as >= 0 and beta >= 1. Higher beta initially seemed to give best, but still bad results, indicating that pheromones not working well.
	Looking to improve pheromone update function.
	> 0.4 * size ant number seems good - paper uses 20 ants for 50 nodes
'''