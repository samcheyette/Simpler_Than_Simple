from model_boolean import *
from boolean_helpers import *
from LOTlib.TopN import TopN
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.Miscellaneous import logsumexp, qq
from math import exp, log

def run(concept, STEPS, TOP,f_data, data, alpha):
    tn = TopN(N=TOP)

    h0 = MyHypothesis()


    for h in MHSampler(h0, f_data, steps=STEPS):
    	tn.add(h)


    z = logsumexp([h.posterior_score for h in tn])
    pp = [(h, exp(h.posterior_score - z)) for h in tn.get_all()]
    sort_post_probs = sorted(pp, key=lambda tup: 1 - tup[1])

    return sort_post_probs

if __name__ == "__main__":

	#dims = [is_shape_, is_color_]
	STEPS = 2000
	TOP = 25
	alpha = 0.995
	conn = [and_,  or_]
	out_file = "time_beta_av.csv"
	funcs = make_rules()

	func1a = funcs[0]
	func1b = funcs[1]
	func2a = funcs[2]
	func2b = funcs[3]
	func3 = funcs[4]
	func4a = funcs[5]
	func4b = funcs[6]



	concepts = []
	all_data = make_data()
	all_objs = copy.deepcopy(all_data)
	all_objs_unf = [(i.color, i.shape) for i in all_objs]
	s = 0
	for shape in SHAPES:
		#concepts.append(func1b(shape))
		#concepts.append(func2b(shape))
		for color in COLORS:
			#if s == 0:
				#concepts.append(func1a(color))
				#concepts.append(func2a(shape))
			for c in conn:
				concepts.append(func3(shape, color, c))
				concepts.append(func4a(shape,color, c))
				#concepts.append(func4b(shape,color, c))
		
		s += 1


	data_beta = {}
	dbs = []
	gens = []
	comps = []
	for conc in concepts:
		d_so_far = []

		print [(i.shape, i.color, conc(i)) for i in all_data]

		for d in all_data:
			d_so_far.append(d)
			f_data_so_far = [FunctionData(input=d_so_far, 
			output = [conc(d) for d in d_so_far], alpha=alpha)]
			r = run(conc, STEPS, TOP, f_data_so_far, d_so_far, alpha)
			
			betas = [1.0, 5.0, 10.0]
			data_beta = copy.deepcopy(vary_beta(r, betas,
							d_so_far,
							f_data_so_far,
							all_objs, alpha, conc))
			keys = copy.deepcopy(data_beta.keys())
			gen_comp = make_generalization(data_beta, all_objs)
			gen = copy.deepcopy(gen_comp[0])
			comp = copy.deepcopy(gen_comp[1])

			gens.append(gen)
			comps.append(comp)
			dbs.append(copy.deepcopy(data_beta))

	over_time_cm = complexity_time(comps)
	over_time_acc = accuracy_time(gens)

	output1(over_time_cm, over_time_acc, out_file)



	#run()