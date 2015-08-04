# Copyright (C) 2014-2015 The BET Development Team

"""
This examples generates uniform random samples in the unit hypercube and
corresponding QoIs (data) generated by a linear map Q.  It then calculates the
gradients using an RBF scheme and uses the gradient information to choose the
optimal set of 2 (3, 4, ... Lambda_dim) QoIs to use in the inverse problem.

In this example, we explore the use the *inner_prod_tol* and *cond_tol* arguments
in :meth:~bet.sensitivity.chooseQoIs.chooseOptQoIs_large.  These areguments can
be used to reduce the computational cost of choosing optimal QoIs when we have
either a high dimensional parameter space, high dimensional data space, or both.
"""

import bet.sensitivity.gradients as grad
import bet.sensitivity.chooseQoIs as cQoI
import bet.Comm as comm
import numpy as np

import bet.calculateP.simpleFunP as simpleFunP
import bet.calculateP.calculateP as calculateP
import bet.postProcess.postTools as postTools

Lambda_dim = 10
Data_dim = 100
num_samples = 1E5
num_centers = 10

# Let the map Q be a random matrix
np.random.seed(0)
Q = np.random.random([Data_dim, Lambda_dim])

# Choose random samples in parameter space to solve the model
samples = np.random.random([num_samples, Lambda_dim])
data = Q.dot(samples.transpose()).transpose()

# Calculate the gradient vectors at some subset of the samples.  At this point
# you must decide if you will be using *bin_ratio* or *bin_size* to define the
# uncertainty in your data, and decide if you will use the expected average
# volume or the expected average condition number to choose an optimal set of
# QoIs.  For this example, we use *bin_ratio* and *volume*.
G = grad.calculate_gradients_rbf(samples, data, centers=samples[:num_centers, :],
    normalize=True)

# With these gradient vectors, we are now ready to choose an optimal set of
# QoIs to use in the inverse problem, based on minimizing the support of the
# inverse solution (the volume choice).  The most robust method for this is
# :meth:~bet.sensitivity.chooseQoIs.chooseOptQoIs_large which will return the
# best set of 2, 3, 4 ... until Lambda_dim.  This method will return a list
# of matrices.  Each matrix has an average volume calculate and a corresponding
# set of QoIs.
best_sets = cQoI.chooseOptQoIs_large(G, max_qois_return=5,
    num_optsets_return=1, inner_prod_tol=0.9, cond_tol=1E4, volume=True)


###############################################################################
# Now we can compare the support of the inverse solution using different sets of
# these QoIs.  We set Q_ref to correspond to the center of the parameter space.
# We choose the set of QoIs to consider.
#QoI_indices = [0, 39, 41, 90]
QoI_indices = [6, 7, 17, 39, 70]


data = data[:, QoI_indices]
Q_ref = Q[QoI_indices, :].dot(0.5 * np.ones(Lambda_dim))
bin_ratio = 0.25

# Find the simple function approximation
(d_distr_prob, d_distr_samples, d_Tree) = simpleFunP.uniform_hyperrectangle(\
    data=data, Q_ref=Q_ref, bin_ratio=bin_ratio, center_pts_per_edge = 1)

# Calculate probablities making Monte Carlo assumption
(P,  lam_vol, io_ptr) = calculateP.prob(samples=samples, data=data,
    rho_D_M=d_distr_prob, d_distr_samples=d_distr_samples)

percentile = 1.0
# Sort samples by highest probability density and sample highest percentile
# percent samples
(num_samples, P_high, samples_high, lam_vol_high, data_high) =\
    postTools.sample_highest_prob(top_percentile=percentile, P_samples=P,
    samples=samples, lam_vol=lam_vol,data = data,sort=True)

# print the number of samples that make up the highest percentile percent
# samples and ratio of the volume of the parameter domain they take up
if comm.rank == 0:
    print (num_samples, np.sum(lam_vol_high))









