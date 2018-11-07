import re
import random
import time
from reader import read_file, files

def select_node(node, tour, size, M, pheromones):
	k = 0.02 #constant to determine how often weighted vs greedy choice is made - higher => more greedy choices
	beta = 2
	P_row = pheromones[node] #take relevant row out of matrix
	distances = M[node]
	selection_choice = random.random()
	if selection_choice <= k:
		return select_greedy(node, P_row, distances, size, beta, tour)
	else:
		return select_weighted(node, P_row, distances, size, beta, tour)


def select_greedy(node, P_row, distances, size, beta, tour):
	largest = 0
	for i in range(size):
		if i == node or i in tour: #skip if same node or already in tour
			continue
		weight = P_row[i] * (1/distances[i])**beta
		if weight > largest:
			largest = weight
			largest_i = i
	return largest_i

def select_weighted(node, P_row, distances, size, beta, tour):
	weights = [0] * (size)
	total = 0
	prev = 0
	largest = 0
	for i in range(size):
		if i == node or i in tour:
			weights[i] = 0
		else:
			weight = P_row[i] * (1/distances[i])**beta
			total += weight
			weights[i] = weight + prev
			prev = weight + prev
			if prev > largest:
				largest = prev
	for weight in weights:
		weight = weight / total
	choice = random.random() * largest
	for i, weight in enumerate(weights):
		if choice - weight < 0:
			return i

def update_pheromones(tours, tour_lengths, size, pheromones):
	rho = 0.0002 #evaporation coefficient
	q = size * 20 #constant
	for i in range(size):
		for j in range(size):
			pheromones[i][j] *= (1 - rho)
	for i, tour in enumerate(tours):
		pher = q / tour_lengths[i]
		for j in range(0, len(tour) - 1):
			a = tour[j]
			b = tour[j + 1]
			pheromones[a][b] += pher
			pheromones[b][a] += pher

def update_tours(tours, tour_lengths, size, M, pheromones):
	for _ in range(size - 1):
		for j, tour in enumerate(tours):
			new_node = select_node(tour[-1], tour, size, M, pheromones)
			tour.append(new_node)
			tour_lengths[j] += M[tour[-1]][tour[-2]] #add edge length to current tour length

def aco(filename):
	start = time.time()
	name, size, M = read_file(filename)
	ants = int((size * 0.4) // 1) #number of ants
	P = [[0.1] * size for _ in range(size)] #initialise pheromones matrix
	for _ in range(10000):
		tours = [[0] for _ in range(ants)]
		tour_lengths = [0] * ants
		update_tours(tours, tour_lengths, size, M, P)
		update_pheromones(tours, tour_lengths, size, P)
	end = time.time()
	print("10000 iterations completed in " + str(end - start))
	print(tour_lengths)

if __name__ == "__main__":
	for i in range(10):
		aco(files[i])

'''
NOTES:
	> Wikipedia mentions alpha (for node selection) as >= 0 and beta >= 1. Lower beta (close to 1) gives more diversity, but requires more iterations to converge towards good values
	> 0.4 * size ant number seems good - paper uses 20 ants for 50 nodes
'''