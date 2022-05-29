import pygad
import sacrebleu
from numpy.random import randint
from numpy.random import rand
import random
import nltk
def fitness (solution):
#    print(' '.join(solution))
    s=sacrebleu.sentence_bleu(' '.join(solution).strip() , ["Jedná se o zkušební větu, abychom získali slovo překlad asdfg."], smooth_method='exp')
    #s=sacrebleu.sentence_chrf(' '.join(solution).strip() , ["Toto je asfs test."])

    return s.score
def load_pop(f):
    with open("{}.trans".format(f)) as sent, open("{}.scores".format(f)) as scores:
        return([nltk.word_tokenize(s) for s in sent.readlines()])
pop=load_pop("out")
#possible_tgt=["Toto", "je", "test","asfs",""]
possible_tgt=list(set([tok for sent in pop for tok in sent]))+['','asdfg']
max_len=19
# PAD
pop=[(p + max_len*[''])[:max_len] for p in pop]*3


def mutation(bitstring, r_mut):
    for i in range(len(bitstring)):
        # check for a mutation
        if rand() < r_mut:
            # flip the bit
            bitstring[i] = random.choice(possible_tgt)

# tournament selection
def selection(pop, scores, k=3):
    # first random selection
    selection_ix = randint(len(pop))
    for ix in randint(0, len(pop), k-1):
        # check if better (e.g. perform a tournament)
        if scores[ix] > scores[selection_ix]:
            selection_ix = ix
    return pop[selection_ix]
# crossover two parents to create two children
def crossover(p1, p2, r_cross):
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()
    # check for recombination
    if rand() < r_cross:
#        print("Crossing over")
 #       print(c1)
  #      print(c2)
        # select crossover point that is not on the end of the string
        pt = randint(1, len(p1)-2)
#        pt=2
        # perform crossover
        c1 = p1[:pt] + p2[pt:]
        c2 = p2[:pt] + p1[pt:]
   #     print("new crossover:")
    #    print(c1)
     #   print(c2)
    return [c1, c2]

# genetic algorithm
def genetic_algorithm(objective, init_pop, n_bits, n_iter, n_pop, r_cross, r_mut):
    # initial population of random bitstring
    # keep track of best solution
    pop=init_pop
    print(pop)
    best, best_eval = 0, objective(pop[0])
    # enumerate generations
    for gen in range(n_iter):
        # evaluate all candidates in the population
        scores = [objective(c) for c in pop]
        # check for new best solution
        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]
                print("Iteration %d: >%d, new best f(%s) = %.3f" % (gen, gen,  pop[i], scores[i]))
        # select parents
        #print ("before:")
        #print(pop)
        selected = [selection(pop, scores) for _ in range(n_pop)]
        #print("after:")
        #print(selected)
        # create the next generation
        children = list()
        for i in range(0, n_pop, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for c in crossover(p1, p2, r_cross):
                # mutation
                mutation(c, r_mut)
                # store for next generation
#                print(c)
                children.append(c)
        # replace population
        pop = children
    return [best, best_eval]
print(genetic_algorithm(fitness,pop,max_len,10000,len(pop),0.5,0.1))

