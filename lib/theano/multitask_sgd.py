"""
**************************************************************************
Multitask Logistic Regression
**************************************************************************

@author: Jason Feriante <feriante@cs.wisc.edu>
@date: 11 Aug 2015
"""
import cPickle, gzip, os, sys, timeit, numpy, theano
import theano.tensor as T
global shared_input

class MultitaskLogReg(object):
    
    def __init__(self, input, n_in, n_out, num_tasks):
        """ 
        :type input: theano.tensor.TensorType
        :param input: symbolic variable that describes the input of the
                                    architecture (one minibatch)

        :type n_in: int
        :param n_in: number of input units, the dimension of the space in
                                 which the datapoints lie

        :type n_out: int
        :param n_out: number of output units, the dimension of the space in
                                    which the labels lie
        """
        global shared_input
        shared_input = input

        # init one LogLayer per task
        self.multi = {};
        for i in range(num_tasks):
            # keep track of the tasks in numeric order
            self.multi['LogLayer' + str(i)] = LogisticRegressionMulti(n_in=n_in, n_out=n_out)


    def negative_log_likelihood(self, y, num_tasks):
        results = {}
        for i in range(num_tasks):
            results['x' + str(i)] = T.dscalar('x' + str(i))

        for i in range(num_tasks):
            # slice the label matrix & only send the relevant column to the 
            # subclass
            results['x' + str(i)] = self.multi['LogLayer' + str(i)].negative_log_likelihood(y[T.arange(y.shape[0]), i])

        rsList = []
        for i in range(num_tasks):
            rsList.append(results['x' + str(i)])
            
        return T.mean(T.stacklists(rsList))


    def errors(self, y, num_tasks): 
        results = {}
        for i in range(num_tasks):
            results['x' + str(i)] = T.dscalar('x' + str(i))

        for i in range(num_tasks):
            # slice the label matrix & only send the relevant column to the 
            # subclass
            results['x' + str(i)] = self.multi['LogLayer' + str(i)].errors(y[T.arange(y.shape[0]), i])

        rsList = []
        for i in range(num_tasks):
            rsList.append(results['x' + str(i)])

        return T.mean(T.stacklists(rsList))



class LogisticRegressionMulti(object):
    """Multi-class Logistic Regression Class

    The logistic regression is fully described by a weight matrix :math:`W`
    and bias vector :math:`b`. Classification is done by projecting data
    points onto a set of hyperplanes, the distance to which is used to
    determine a class membership probability.
    """

    def __init__(self, n_in, n_out):
        """ Initialize the parameters of the logistic regression

        :type input: theano.tensor.TensorType
        :param input: symbolic variable that describes the input of the
                      architecture (one minibatch)

        :type n_in: int
        :param n_in: number of input units, the dimension of the space in
                     which the datapoints lie

        :type n_out: int
        :param n_out: number of output units, the dimension of the space in
                      which the labels lie

        """
        # initialize with 0 the weights W as a matrix of shape (n_in, n_out)
        self.W = theano.shared(
            value=numpy.zeros(
                (n_in, n_out),
                dtype=theano.config.floatX
            ),
            name='W',
            borrow=True
        )

        # initialize the baises b as a vector of n_out 0s
        self.b = theano.shared(
            value=numpy.zeros(
                (n_out,),
                dtype=theano.config.floatX
            ),
            name='b',
            borrow=True
        )

        # symbolic expression for computing the matrix of class-membership
        # probabilities
        # Where:
        # W is a matrix where column-k represent the separation hyperplane for
        # class-k
        # x is a matrix where row-j  represents input training sample-j
        # b is a vector where element-k represent the free parameter of
        # hyperplane-k
        global shared_input
        self.p_y_given_x = T.nnet.softmax(T.dot(shared_input, self.W) + self.b)

        # symbolic description of how to compute prediction as class whose
        # probability is maximal
        self.y_pred = T.argmax(self.p_y_given_x, axis=1)
        # end-snippet-1

        # parameters of the model
        self.params = [self.W, self.b]

        # keep track of model input
        # self.input = input #@todo: do we need this?


    def negative_log_likelihood(self, y):
        """Return the mean of the negative log-likelihood of the prediction
        of this model under a given target distribution.

        .. math::

            \frac{1}{|\mathcal{D}|} \mathcal{L} (\theta=\{W,b\}, \mathcal{D}) =
            \frac{1}{|\mathcal{D}|} \sum_{i=0}^{|\mathcal{D}|}
                \log(P(Y=y^{(i)}|x^{(i)}, W,b)) \\
            \ell (\theta=\{W,b\}, \mathcal{D})

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label

        Note: we use the mean instead of the sum so that
              the learning rate is less dependent on the batch size
        """

        return -T.mean(T.log(self.p_y_given_x)[T.arange(y.shape[0]), y])

    def errors(self, y):
        """Return a float representing the number of errors in the minibatch
        over the total number of examples of the minibatch ; zero one
        loss over the size of the minibatch

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label
        """

        if y.ndim != self.y_pred.ndim:
            raise TypeError(
                'y should have the same shape as self.y_pred',
                ('y', y.type, 'y_pred', self.y_pred.type)
            )

        if y.dtype.startswith('int'):
            return T.mean(T.neq(self.y_pred, y))
        else:
            raise NotImplementedError()













