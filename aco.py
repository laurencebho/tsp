import random
import time
from reader import read_file, files

def select_node(node, tour, size, M, pheromones):
	k = 0 #constant to determine how often weighted vs greedy choice is made - higher => more greedy choices
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
	weights = [0] * size
	total = 0
	prev = 0
	for i in range(size):
		if i in tour:
			weights[i] = 0
		else:
			weight = P_row[i] * (1/distances[i])**beta
			total += weight
			weights[i] = weight
	for i, _ in enumerate(weights):
		weights[i] /= total
	choice = random.random()
	for i, weight in enumerate(weights):
		choice -= weight
		if choice < 0:
			return i

def update_pheromones(tours, tour_lengths, size, pheromones):
	rho = 0.02 #evaporation coefficient
	q = size ** 2 #constant
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

def local_update(tours, size, pheromones):
	rho = 0.001 #evaporation coefficient
	for i in range(size):
		for j in range(size):
			pheromones[i][j] *= (1 - rho)
	if len(tours[0]) == size: #if at end
		for tour in tours:
			pheromones[tour[0]][tour[-1]] += rho
			pheromones[tour[-1]][tour[0]] += rho
	else:
		for tour in tours:
			pheromones[tour[-2]][tour[-1]] += rho
			pheromones[tour[-1]][tour[-2]] += rho

def local_tours(tours, tour_lengths, size, M, pheromones):
	if len(tours[0]) == size: #if at end, make edge to start
		for j, tour in enumerate(tours):
			new_node = tour[0]
			tour_lengths[j] += M[tour[-1]][tour[0]]
	else:
		for j, tour in enumerate(tours):
			new_node = select_node(tour[-1], tour, size, M, pheromones)
			tour.append(new_node)
			tour_lengths[j] += M[tour[-1]][tour[-2]] #add edge length to current tour length


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
	P = [[1] * size for _ in range(size)] #initialise pheromones matrix
	best = 0
	for _ in range(3000):
		tours = [[0] for _ in range(ants)]
		tour_lengths = [0] * ants
		update_tours(tours, tour_lengths, size, M, P)
		update_pheromones(tours, tour_lengths, size, P)
		#print(tour_lengths)
		for l in tour_lengths:
			if l < best or best == 0:
				best = l
		'''
	for i, _ in enumerate(tour_lengths): #add edge to beginning
		tour_lengths[i] += M[tours[i][-1]][tours[i][0]]
		'''
	end = time.time()
	print("3000 iterations completed in " + str(end - start))
	print(str(tour_lengths) + ", " + str(best))

def local_aco(filename):
	start = time.time()
	name, size, M = read_file(filename)
	ants = int((size * 0.4) // 1)
	P = [[1] * size for _ in range(size)] #initialise pheromones matrix
	best = 0
	for _ in range(1000):
		tours = [[0] for _ in range(ants)]
		tour_lengths = [0] * ants
		for _ in range(size):
			local_tours(tours, tour_lengths, size, M, P)
			local_update(tours, size, P)
		#print(tour_lengths)
		for l in tour_lengths:
			if l < best or best == 0:
				best = l
	end = time.time()
	print("300 iterations completed in " + str(end - start))
	print(str(tour_lengths) + ", " + str(best))

if __name__ == "__main__":
	for i in range(10):
		#aco(files[i])
		local_aco(files[i])

