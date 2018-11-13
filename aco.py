import random
import time
from reader import read_file, files

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
	choice = random.random() * total
	for i, weight in enumerate(weights):
		choice -= weight
		if choice < 0:
			return i


def update_best(tours, tour_lengths, size, pheromones, global_best, global_best_tour):
	rho = 0.1 #evaporation coefficient
	q = 1
	best = 0
	best_i = 0
	if len(tours[0]) % 2 == 0: #sometimes use global best
		best_tour = global_best_tour
		best = global_best
	else:
		for i, l in enumerate(tour_lengths):
			if l < best or best == 0:
				best = l
				best_i = i
		best_tour = tours[best_i]

	pher = q / best
	for i in range(-1, len(best_tour) - 1):
		a = best_tour[i]
		b = best_tour[i + 1]
		pheromones[a][b] *= (1 - rho)
		pheromones[b][a] *= (1 - rho)
		pheromones[a][b] += rho * pher
		pheromones[b][a] += rho * pher

def local_update(tours, tour_lengths, size, M, pheromones):
	rho = 0.1 #evaporation coefficient
	p_start = size ** -3

	if len(tours[0]) == size: #if at end, make edge to start
		for j, tour in enumerate(tours):
			tour_lengths[j] += M[tour[-1]][tour[0]]
		for tour in tours:
			pheromones[tour[0]][tour[-1]] *= (1 - rho)
			pheromones[tour[-1]][tour[0]] *= (1 - rho)
			pheromones[tour[0]][tour[-1]] += rho * p_start
			pheromones[tour[-1]][tour[0]] += rho * p_start
	else:
		for j, tour in enumerate(tours):
			new_node = select_node(tour[-1], tour, size, M, pheromones)
			tour.append(new_node)
			tour_lengths[j] += M[tour[-1]][tour[-2]] #add edge length to current tour length
		for tour in tours:
			pheromones[tour[-2]][tour[-1]] *= (1 - rho)
			pheromones[tour[-1]][tour[-2]] *= (1 - rho)
			pheromones[tour[-2]][tour[-1]] += rho * p_start
			pheromones[tour[-1]][tour[-2]] += rho * p_start

def aco(filename):
	start = time.time()
	name, size, M = read_file(filename)
	ants = 20#int((size * 0.4) // 1)
	P = [[size ** -3] * size for _ in range(size)] #initialise pheromones matrix
	best = 0
	best_tour = []
	best_ant = 0
	for _ in range(300):
		tours = [[random.randint(0, size - 1)] for _ in range(ants)] #or random.randint(0, size - 1)
		tour_lengths = [0] * ants
		for _ in range(size):
			local_update(tours, tour_lengths, size, M, P)

		for i, l in enumerate(tour_lengths):
			if l < best or best == 0:
				best = l
				best_tour = tours[i]
				best_ant = i

		update_best(tours, tour_lengths, size, P, best, best_tour) #can tidy this
		#print(str(tour_lengths) + ", " + str(sum(tour_lengths) / float(len(tour_lengths))))
	end = time.time()
	print("1000 iterations completed in " + str(end - start))
	print(str(tour_lengths) + ", " + str(best))
	print(best_tour)

if __name__ == "__main__":
	for i in range(10):
		aco(files[4])
		#aco(files[i])


'''
NOTES:
	> Wikipedia mentions alpha (for node selection) as >= 0 and beta >= 1.
	> 0.4 * size ant number seems good - paper uses 20 ants for 50 nodes
	> Keeping track of the best tour helps
	> starting pheromone level suggested as 1 / (n * Lnn) where Lnn is another method's tour length
	> When  ant  system  is applied to symmetric instances of the TSP Tau(r, s) = Tau(s, r), so pheromones matrix should be symmetrically updated
	> Paper suggests that ants start in random positions
	> Paper suggests in pseudocode that local updating should occur after each ant has made a step

'''

