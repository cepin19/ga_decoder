import pygad
import sacrebleu
from numpy.random import randint
from numpy.random import rand
import random
import nltk
nltk.download('punkt')

import logging
from nltk.tokenize.treebank import TreebankWordDetokenizer, TreebankWordTokenizer
from comet import download_model, load_from_checkpoint

model_path = download_model("wmt20-comet-da")

model = load_from_checkpoint(model_path)



detok=TreebankWordDetokenizer()
tok=TreebankWordTokenizer()
n_best=20
def fitness(src,solution,ref):
#    print(' '.join(solution))
    s=sacrebleu.sentence_bleu(detok.detokenize(solution).strip() , [ref], smooth_method='exp')

#s=sacrebleu.sentence_chrf(' '.join(solution).strip() , ["Toto je asfs test."])

    return s.score
def fitness_comet_single(src,solution,ref):
    data=[
        {
                "src": src,
                "mt": detok.detokenize(solution).strip(),
                "ref": ref
        }]
    seg_scores, sys_score = model.predict(data, batch_size=1, gpus=1)
    return sys_score

def fitness_comet_multi(src,solutions,ref):
    solutions=[ list(filter(lambda t: t != '', solution)) for solution in solutions]
    data=[
            {
            "src": src,
             "mt": detok.detokenize(solution).strip(),
            "ref": ref
           } for solution in solutions]
    seg_scores, sys_score = model.predict(data, batch_size=len(solutions), gpus=4, progress_bar=False)
    return seg_scores



def mutation(bitstring, r_mut):
    #TODO: solve for multi-token expressions
    #It should be more probable to replace existing word rather than an emtpy ony
    empty_repl=0.1
    for i in range(len(bitstring)):
        # check for a mutation
        if rand() < r_mut:
            # flip the bit
            if bitstring[i]=='':
                if rand() > empty_repl:
                    continue
            tgt=random.choice(possible_tgt)#.split(' ')
            l=len(tgt)
            if l>1:
                #find empty places in the gene
                space_i=[a for a, x in enumerate(bitstring) if x == '']
                if l>len(space_i):#wait, thats illegal (we cant make the gene longer)
                   continue
    #            for x in range(l):
    #print(bitstring)
     #               print(space_i)
      #              print(x)
       #             print(space_i[-x-1])
#
 #                   del bitstring[space_i[-x-1]]  #we need to iterate backwards to not mess up the order
  #              print(i)
   #             print(bitstring)
#                logging.warning("inserting {} instead of {}".format(tgt, bitstring[i]))
                bitstring[i]=tgt[0]
                for x in range(1,l):
                    
                    bitstring.insert(i+x,tgt[x])
                    space_i=[a for a, t in enumerate(bitstring) if t == '']
                    #logging.warning(space_i)
                    #logging.warning(x)
                    #logging.warning(bitstring)
                    del bitstring[space_i[-1]]
            else:
                x=0
                bitstring[i] = tgt[x]

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
def genetic_algorithm(objective, init_pop, n_bits, n_iter, n_pop, r_cross, r_mut,src,ref):
    # initial population of random bitstring
    # keep track of best solution
    pop=init_pop
    best, best_eval = pop[0], objective(src,pop,ref)[0]
    logging.warning("initial best: {}".format(best))
    logging.warning("initial best fitness: {}".format(best_eval))
    logging.warning("tgt words: {}".format(possible_tgt))
    # enumerate generations
    for gen in range(n_iter):
        # evaluate all candidates in the population
#        scores = [objective(src,c,ref) for c in pop]
        scores=objective(src,pop,ref)
        logging.warning("avg fitness: {}".format(sum(scores)/len(scores)))

        #for p, s in zip(pop,scores):
        #    logging.warning("{} = {}".format(detok.detokenize(p).strip(),s))
        # check for new best solution
        if gen%10==0:
            logging.warning("gen: {}".format(gen))
        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]
                logging.warning("Iteration %d: >%d, new best f(%s) = %.3f" % (gen, gen,  pop[i], scores[i]))
        # select parents
#        print ("before:")
 #       print(pop)
        selected = [selection(pop, scores) for _ in range(n_pop)]
   #     print("after:")
  #      print(selected)
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
f="news19.en.snt_trans_n20"
with open("{}.trans".format(f)) as trans, open("{}.scores".format(f)) as scores, open("{}.ref".format(f)) as refs, open("{}.src".format(f)) as srcs, open("{}.tgt_words_not_exp_multi".format(f)) as dict_tgts:
    translations=trans.readlines()
    i=0
    for dict_tgt,src,ref in zip(dict_tgts,srcs,refs):
        translations_sent=translations[i*n_best:(i+1)*n_best]
        init_pop=([nltk.word_tokenize(s) for s in translations_sent])
        #print(init_pop)
        pop=[]
        #refactor
        for s in init_pop:
            news=[]
            for tok in s:
                news.append(tok)
                news.append('')
            pop.append(news)
        #possible_tgt=["Toto", "je", "test","asfs",""]
        tgt_toks=list(set([tok for sent in init_pop for tok in sent]))
        tgt_toks=[[tok] for tok in tgt_toks]
        dict_toks=[t.split(' ') for t in dict_tgt.strip().split(';')]
        possible_tgt=tgt_toks+[['']]+dict_toks
        max_len=int(max([len(s) for s in pop])*1.0)
        # PAD
        pop=[(p + max_len*[''])[:max_len] for p in pop]*40
        #print(pop)
#        print(pop
        out=genetic_algorithm(fitness_comet_multi,pop,max_len,500,len(pop),0.3,0.05,src,ref)[0]
        out=list(filter(lambda t: t != '', out))

        print(detok.detokenize(out))
        i+=1
#        if i>1:
           # break

