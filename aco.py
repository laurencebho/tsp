import random
import time
from reader import read_file, files
from annealing import annealing

def select_node(node, tour, size, M, pheromones):
	k = 0.9 #constant to determine how often weighted vs greedy choice is made - higher => more greedy choices
	beta = 2 #higher beta places more importance on a short distance over pheromone value
	P_row = pheromones[node] #take relevant row out of matrix
	distances = M[node]
	selection_choice = random.random()
	if selection_choice <= k:
		return select_greedy(node, P_row, distances, size, beta, tour)
	return select_weighted(node, P_row, distances, size, beta, tour)

def select_greedy(node, P_row, distances, size, beta, tour):
	largest = 0
	for i in range(size):
		if i in tour: #skip if already in tour
			continue
		weight = P_row[i] * (1/distances[i])**beta if distances[i] != 0 else P_row[i] * (1/0.00001)**beta
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
			weight = P_row[i] / distances[i]**beta if distances[i] != 0 else P_row[i] / 0.00001**beta
			total += weight
			weights[i] = weight
	choice = random.random() * total
	for i, weight in enumerate(weights):
		choice -= weight
		if choice < 0:
			return i

def update_best(tours, tour_lengths, size, pheromones, global_best, global_best_tour):
	rho = 0.2 #evaporation coefficient
	best = 0
	best_i = 0
	if len(tours[0]) % 10 == 0: #sometimes use global best
		best_tour = global_best_tour
		best = global_best
	else:
		for i, l in enumerate(tour_lengths):
			if l < best or best == 0:
				best = l
				best_i = i
		best_tour = tours[best_i]

	for i in range(-1, len(best_tour) - 1):
		a = best_tour[i]
		b = best_tour[i + 1]
		pher = pheromones[a][b] * (1 - rho) + rho / best
		pheromones[a][b] = pher
		pheromones[b][a] = pher

def choose_start_pheromone(size, M):
	t = [0]
	dist = 0
	for _ in range(size - 1):
		shortest = -1
		shortest_i = 0
		for i in range(size - 1):
			if i in t:
				continue
			edge = M[t[-1]][i]
			if edge < shortest or shortest == -1:
				shortest = edge
				shortest_i = i
		dist += shortest
		t.append(shortest_i)
	dist += M[t[-1]][t[0]]
	return 1 / (size * size * dist)

def local_update(tours, tour_lengths, size, M, pheromones, p_start):
	rho = 0.3 #evaporation coefficient

	if len(tours[0]) == size: #if at end, make edge to start
		for j, tour in enumerate(tours):
			tour_lengths[j] += M[tour[-1]][tour[0]]

		for tour in tours:
			pher = pheromones[tour[-1]][tour[0]] * (1 - rho) + rho * p_start
			pheromones[tour[-1]][tour[0]] = pher
			pheromones[tour[0]][tour[-1]] = pher

	else:
		for j, tour in enumerate(tours):
			new_node = select_node(tour[-1], tour, size, M, pheromones)
			tour.append(new_node)
			tour_lengths[j] += M[tour[-2]][tour[-1]] #add edge length to current tour length
		
		for tour in tours:
			pher = pheromones[tour[-2]][tour[-1]] * (1 - rho) + rho * p_start
			pheromones[tour[-2]][tour[-1]] = pher
			pheromones[tour[-1]][tour[-2]] = pher

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

def aco(filename):
	start = time.time()
	name, size, M = read_file(filename)
	#print(M)
	ants = 10#int((size * 0.4) // 1)
	p_start = choose_start_pheromone(size, M)
	print("Starting pheromone level: " + str(p_start))
	P = [[p_start] * size for _ in range(size)] #initialise pheromones matrix
	best = 0
	best_tour = []
	for _ in range(500):
		tours = [[random.randint(0, size - 1)] for _ in range(ants)] #or random.randint(0, size - 1)
		tour_lengths = [0] * ants
		for _ in range(size):
			local_update(tours, tour_lengths, size, M, P, p_start)
		for i, tour in enumerate(tours):
			tours[i], tour_lengths[i] = opt_2(tour, size, M) #local optimisation of each tour
		for i, l in enumerate(tour_lengths):
			if l < best or best == 0:
				best = l
				best_tour = tours[i]

		update_best(tours, tour_lengths, size, P, best, best_tour) #can tidy this
		print(str(tour_lengths) + ", " + str(sum(tour_lengths) / float(len(tour_lengths))))
	end = time.time()
	print("500 iterations completed in " + str(end - start))
	print(str(tour_lengths) + ", " + str(best))
	print(best_tour)
	save_tour(size, best, best_tour)
	return best, best_tour

def save_tour(size, dist, tour):
	with open("./" + str(size) + "_" + str(dist) + ".txt", "w+") as f:
		f.write("dist: " + str(dist) + "\n")
		for i, _ in enumerate(tour):
			tour[i] += 1
		f.write(str(tour))

if __name__ == "__main__":
	for i in range(10):
		aco(files[i])

