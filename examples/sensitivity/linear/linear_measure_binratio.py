# Copyright (C) 2014-2016 The BET Development Team

"""
This example generates uniform random samples in the unit hypercube and
corresponding QoIs (data) generated by a linear map Q.  We then calculate the
gradients using an RBF scheme and use the gradient information to choose the
optimal set of 2 (3, 4, ... input_dim) QoIs to use in the inverse problem.

Every real world problem requires special attention regarding how we choose
*optimal QoIs*.  This set of examples (examples/sensitivity/linear) covers
some of the more common scenarios using easy to understand linear maps.

In this *measure_binratio* example we choose *optimal QoIs* to be the set of
QoIs of size input_dim that produces the smallest support of the inverse
solution, assuming we define the uncertainty in our data relative to the range
of data measured in each QoI (bin_ratio).
"""

import numpy as np
import bet.sensitivity.gradients as grad
import bet.sensitivity.chooseQoIs as cqoi
import bet.calculateP.simpleFunP as simpleFunP
import bet.calculateP.calculateP as calculateP
import bet.postProcess.postTools as postTools
import bet.Comm as comm
import bet.sample as sample

# Let Lambda be a 5 dimensional hypercube
input_dim = 5
output_dim = 10
num_samples = 1E5
num_centers = 10

# Let the map Q be a random matrix of size (output_dim, input_dim)
np.random.seed(0)
Q = np.random.random([output_dim, input_dim])

# Initialize some sample objects we will need
input_samples = sample.sample_set(input_dim)
output_samples = sample.sample_set(output_dim)

# Choose random samples in parameter space to solve the model
input_samples.set_values(np.random.uniform(0, 1, [num_samples, input_dim]))

# Make the MC assumption and compute the volumes of each voronoi cell
input_samples.estimate_volume_mc()


# Compute the output values with the map Q
output_samples.set_values(Q.dot(input_samples.get_values().transpose()).\
        transpose())

# Calculate the gradient vectors at some subset of the samples.  Here the
# *normalize* argument is set to *True* because we are using *bin_ratio* to
# determine the uncertainty in our data.
cluster_discretization = sample.discretization(input_samples, output_samples)
# We will approximate the jacobian at each of the centers
center_discretization = grad.calculate_gradients_rbf(cluster_discretization,
        num_centers, normalize=True)

# With these gradient vectors, we are now ready to choose an optimal set of
# QoIs to use in the inverse problem, based on minimizing the support of the
# inverse solution (measure).  The most robust method for this is
# :meth:~bet.sensitivity.chooseQoIs.chooseOptQoIs_large which returns the
# best set of 2, 3, 4 ... until input_dim.  This method returns a list of
# matrices.  Each matrix has 10 rows, the first column representing the
# expected inverse measure ratio, and the rest of the columns the corresponding
# QoI indices.
input_samples_center = center_discretization.get_input_sample_set()
best_sets = cqoi.chooseOptQoIs_large(input_samples_center, measure=True)

###############################################################################

# At this point we have determined the optimal set of QoIs to use in the inverse
# problem.  Now we compare the support of the inverse solution using
# different sets of these QoIs.  We set Q_ref to correspond to the center of
# the parameter space.  We choose the set of QoIs to consider.

QoI_indices = [3, 6] # choose up to input_dim
#QoI_indices = [3, 4]
#QoI_indices = [8, 9]
#QoI_indices = [3, 5, 6, 8, 9]
#QoI_indices = [3, 4, 5, 8, 9]
#QoI_indices = [2, 3, 6, 8, 9]
#QoI_indices = [3, 5, 6, 7, 8]
#QoI_indices = [0, 1, 2, 3, 4]

'''
In this linear case we expect our ordering of sets of QoIs to be very good.  But
we see in this example that the set [3, 4, 5, 8, 9] (set 1) has a smaller
expected measure ratio than the set [2, 3, 6, 8, 9] (set 2), however the inverse 
solution yields larger measure of support for set 1 than set 2.  This is likely
due to the fact that we restrict ourselves to the parameter space [0, 1]^5, and 
the actual support of the inverse solution may extend out of this space.  The 
expected measure ratio is computed assuming an unbounded parameter space.
'''

# Choose some QoI indices to solve the inverse problem with
output_samples._dim = len(QoI_indices)
output_samples.set_values(output_samples.get_values()[:, QoI_indices])

# Define the reference point in the output space to correspond to the center of
# the input space.
Q_ref = Q[QoI_indices, :].dot(0.5 * np.ones(input_dim))

# bin_ratio defines the uncertainty in our data
bin_ratio = 0.25

# Create discretization object
my_discretization = sample.discretization(input_sample_set=input_samples,
                                        output_sample_set=output_samples)


# Find the simple function approximation
simpleFunP.regular_partition_uniform_distribution_rectangle_scaled(
    data_set=my_discretization, Q_ref=Q_ref, rect_scale=bin_ratio,
    center_pts_per_edge=1)

# Calculate probablities making the Monte Carlo assumption
calculateP.prob(my_discretization)

percentile = 1.0
# Sort samples by highest probability density and find how many samples lie in
# the support of the inverse solution.  With the Monte Carlo assumption, this
# also tells us the approximate volume of this support.
(num_samples, _, indices_in_inverse) =\
    postTools.sample_highest_prob(top_percentile=percentile,
    sample_set=input_samples, sort=True)

# Print the number of samples that make up the highest percentile percent
# samples and ratio of the volume of the parameter domain they take up
if comm.rank == 0:
    print (num_samples, np.sum(input_samples.get_volumes()[indices_in_inverse]))
