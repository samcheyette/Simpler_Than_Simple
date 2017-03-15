from model_boolean import *
from LOTlib.Miscellaneous import logsumexp, qq
from math import exp, log
from LOTlib.DataAndObjects import FunctionData
import copy

def make_data():
	objs = []
	for c in COLORS:
		for s in SHAPES:
			o = Obj()
			o.color = c
			o.shape = s
			objs.append(o)

	return objs

def make_rules():

	def func1a(col):
		def func(o):
			return is_shape_(o,  col)
		return func

	def func1b(shp):
		def func(o):
			return is_shape_(o,  shp)
		return func

	def func2a(col):
		def func(o):
			return not_(is_color_(o, col))
		return func

	def func2b(col):
		def func(o):
			return not_(is_shape_(o, col))
		return func

	def func3(shp, col, c):
		def func(o):
			return c(is_shape_(o,  shp), is_color_(o, col))
		return func

	def func4a(shp, col, c):
		def func(o):
			return c(not_(is_shape_(o,  shp)), is_color_(o, col))
		return func

	def func4b(shp, col, c):
		def func(o):
			return c((is_shape_(o,  shp)), not_(is_color_(o, col)))
		return func

	return [func1a,func1b, func2a, func2b, func3, func4a, func4b]


def make_generalization(data, all_objs):
	gen_dct = {}
	comp_dct = {}
	for key in data:
		ps = {}
		av_complexity = 0.0

		for o in all_objs:
			ps[(o.color, o.shape)] = 0.0
		hyps = data[key]
		for hyp_p in hyps:
			hyp = hyp_p[0]
			p = hyp_p[1]
			gen = hyp(all_objs)
			assert(len(ps.keys()) == len(gen))
			for i in xrange(len(all_objs)):
				obj = (all_objs[i].color, all_objs[i].shape)
				assert(obj in ps)
				ps[obj] += (gen[i] * 1.0) * p
			av_complexity += hyp.value.count_subnodes() * p

		#av_complexity /= len(hyps)
		gen_dct[key] = copy.deepcopy(ps)
		comp_dct[key] = av_complexity


	return gen_dct, comp_dct

def complexity_time(cmps):
	dct = {}
	for cm in cmps:
		for k in cm:
			tup = (list(k[0])[0][4], k[1])
			if tup not in dct:
				dct[tup] = []
			dct[tup].append(cm[k])


	return dct

def accuracy_time(gens):
	dct = {}
	for g in gens:
		for k in g:
			dct_gen = g[k]
			beta =k[1]
			lst = list(k[0])
			for l in lst:
				col = l[1]
				shp = l[0]
				data_amount = l[4]

				in_conc = 1.0 * l[2]
				pred =  g[k][(col, shp)]
				dif = 1.0 - abs(pred - in_conc)

				tup = (data_amount, beta)
				if tup not in dct:
					dct[tup] = []
				dct[tup].append(dif)

	return dct





def vary_beta(hyps, betas, seen_data, seen_f_data, all_objs, alpha, conc):
	#upto=n means 1 increment
	#per is a single integer
	#data = [FunctionData(input=unf_data, 
    	#	output=[conc(d) for d in unf_data], alpha=alpha)]
	#incr = (upto)/float(n)
	d = {}
	#b =1.0

	seen = {}
	seen_obj_feats = []
	for o in seen_data:
		seen_obj_feats.append((o.color, o.shape))

	num_seen = 0
	for k in all_objs:
		if (k.color, k.shape) in seen_obj_feats:
			seen[(k.color, k.shape)] = True
			num_seen += 1
		else:
			seen[(k.color, k.shape)] = False


	for b in betas:
		re_compute = []
		for k in hyps:
			k[0].priorconst = b
			new_post = k[0].compute_prior() + k[0].compute_likelihood(seen_f_data)
			re_compute.append((k[0], new_post))

		z = logsumexp([r[1] for r in copy.deepcopy(re_compute)])
		pp = [(r[0], exp(r[1] - z)) for r in copy.deepcopy(re_compute)]
		sort_post_probs = sorted(copy.deepcopy(pp), key=lambda tup: 1 - tup[1])
		
		d[(tuple([(i.shape, i.color, conc(i), seen[(i.color, i.shape)], num_seen) for i in all_objs]), b)] = copy.deepcopy(sort_post_probs)
		
		#b += incr
	#for k in d.keys()[:1]:
		#all_objs here NEEDS to be the same as 
		#all_objs in d[tuple(,...,all_objs))]


	return d


def obj_eq(o1, o2):
	return (o1.shape == o2.shape) and (o1.color == o2.color)

def output1(over_time_cm, over_time_acc, file):
	out = "beta, dat_amount, av_acc, av_complex\n"
	for k in over_time_cm:
		assert(k in over_time_acc)
		beta = k[1]
		data_amount = k[0]
		av_acc = sum(over_time_acc[k])/len(over_time_acc[k])
		av_comp = sum(over_time_cm[k])

		out += ("%f, %f, %f, %f\n" % (beta, data_amount, 
										av_acc, av_comp))

	o = open(file, "w+")
	o.write(out)
	o.close()





"""
def make_generalization(hyp, data):
	#for k in data:
	overall_resp = {}
	for h in hyp:

		resp = h[0](data)
		for r in xrange(len(resp)):
			print data[r], resp[r]

		print


def vary_beta(hyps, upto, n, unf_data, data, alpha, conc):
	#upto=n means 1 increment
	#per is a single integer
	#data = [FunctionData(input=unf_data, 
    	#	output=[conc(d) for d in unf_data], alpha=alpha)]
	incr = (upto)/float(n)
	d = {}
	b =1.0
	for i in xrange(n):
		re_compute = []
		for k in hyps:
			k[0].priorconst = b
			new_post = k[0].compute_prior() + k[0].compute_likelihood(data)
			re_compute.append((k[0], new_post))

		z = logsumexp([r[1] for r in copy.deepcopy(re_compute)])
		pp = [(r, exp(r[1] - z)) for r in copy.deepcopy(re_compute)]
		sort_post_probs = sorted(copy.deepcopy(pp), key=lambda tup: 1 - tup[1])
		d[(tuple([(i.shape, i.color, conc(i)) for i in unf_data]), b)] = copy.deepcopy(sort_post_probs)
		b += incr

	return d

"""