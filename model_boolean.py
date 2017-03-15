
from LOTlib.Grammar import Grammar
import copy
from LOTlib.Primitives import primitive


SHAPES = ['square', 'triangle', 'rectangle']
COLORS = ['blue', 'red', 'green']

ALL_BUILD = [SHAPES, COLORS]


class Obj():
    def __init__(self):
        self.color = None
        self.shape = None

@primitive
def is_shape_(x, y):
    assert(x.shape != None)
    return x.shape == str(y)
@primitive
def is_color_(x, y):
    assert(x.color != None)
    return x.color == str(y)

@primitive
def and_(x, y):
    return x and y
@primitive
def or_(x, y):
    return x or y
@primitive
def not_(x):
    return not(x)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


grammar = Grammar(start='BOOL')

#for color in COLORS:
   # grammar.add_rule('COLOR', '%s', [color], 1.0)

for shape in SHAPES:

    grammar.add_rule('SHAPE', shape, None, 1.0)

for color in COLORS:

    grammar.add_rule('COLOR', color, None, 1.0)

# Define some operations
grammar.add_rule('BOOL', 'is_shape_(%s, "%s")', ['x', 'SHAPE'], 1.0)
grammar.add_rule('BOOL', 'is_color_(%s, "%s")', ['x', 'COLOR'], 1.0)

grammar.add_rule('BOOL', 'and_', ['BOOL', 'BOOL'], 0.5)
grammar.add_rule('BOOL', 'or_', ['BOOL', 'BOOL'], 0.5)
grammar.add_rule('BOOL', 'not_', ['BOOL'], 0.5)

#grammar.add_rule('BOOL', 'xor_', ['BOOL', 'BOOL'], 1.0)

from math import log
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Miscellaneous import Infinity, beta, attrmem

# define a 
class MyHypothesis(LOTHypothesis):
    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar,
                     display="lambda x: %s", **kwargs)

        #this corresponds to beta, resource penalty
        self.priorconst = 1.0

    def __call__(self, x):  # , max_length=4):
        out = []
        for k in x:
            out.append(LOTHypothesis.__call__(self, k))

        return copy.copy(out)

    @attrmem('prior')
    def compute_prior(self, sm=1e-20):
        """Compute the log of the prior probability.
        """
        # If we exceed the maximum number of nodes, give -Infinity prior
        
        if self.value.count_subnodes() > getattr(self, 'maxnodes', Infinity):
            return -Infinity


        #this corresponds to beta, resource penalty

        priorconst = ((self.value.count_subnodes()) * 
                        log(self.priorconst))

        # Compute the grammar's probability
        return ((self.grammar.log_probability(self.value)-priorconst)
                 / self.prior_temperature) 



    def compute_single_likelihood(self, datum):
        inp = self(datum.input)
        assert(len(inp) == len(datum.output))
        p = 0.0
        for k in xrange(len(inp)):
            if inp[k] == datum.output[k]:
                p += log(datum.alpha)
            else:
                p += log(1.0-datum.alpha)   

        return p


if __name__ == "__main__":
    from LOTlib.SampleStream import *
    from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
    from LOTlib.DataAndObjects import FunctionData
    from math import log, exp


    o = Obj()
    o.shape = "square"
    o.color = "green"

    o2 = Obj() 
    o2.shape ="triangle"
    o2.color = "red"

    o3 = Obj() 
    o3.shape ="rectangle"
    o3.color = "blue"

    o4 = Obj() 
    o4.shape ="triangle"
    o4.color = "blue"
    obs = [o, o2, o3]
    #print [(o.shape, o.color) for i in obs]
    conc = lambda o: and_(is_shape_(o, "square"), is_color_(o, "blue"))
    #conc = lambda o: or_(and_(is_shape_(o, "square"), is_color_(o, "blue")), is_shape_(o, "rectangle"))
    data = [FunctionData(input=obs, output=[conc(ob) for ob in obs], alpha=0.99)]
    h0 = MyHypothesis()
    #print data
    print is_color_(o, 'blue')
    print is_shape_(o, 'square')

    for h in SampleStream(MHSampler(h0, data, steps=100)):
        print h, h(obs), [conc(ob) for ob in obs]
        print exp(h.likelihood), exp(h.posterior_score)