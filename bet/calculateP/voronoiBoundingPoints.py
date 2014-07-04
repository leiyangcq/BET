# -*- coding: utf-8 -*-
import numpy as np

def center_and_layer1_points(center_pts_per_edge, center, r_ratio, sur_domain):
    """
    Generates a regular grid of center points that define the voronoi
    tesselation of exactly the interior of a hyperrectangle centered at
    ``center`` with sides of length ``r_ratio*sur_width`` and the layers
    of voronoi cells that bound these interior cells. The resulting voronoi
    tesselation exactly represents the hyperrectangle.

    This method can also be used to tile ``sur_domain`` with points to define
    voronoi regions if the user sets ``r_ratio = 1``.

    :param list() center_pts_per_edge: number of center points per edge and
        additional two points will be added to create the bounding layer
    :param center: location of the center of the hyperrectangle
    :type center: :class:`numpy.ndarray` of shape (mdim,)
    :param double r_ratio: ratio of the length of the sides of the hyperrectangle to
        the surrounding domain
    :param sur_domain: minima and maxima of each dimension defining the
        surrounding domain
    :type sur_domain: :class:`numpy.ndarray` of shape (mdim, 2)

    :rtype: tuple
    :returns (points, interior_and_layer1) where where points is an
        :class:`numpy.ndarray` of shape (num_points, dim), interior_and_layer1
        is a list() of dim :class:`numpy.ndarray`s of shape
        (center_pts_per_edge+2,).

    """
    if r_ratio > 1:
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    # determine the width of the surrounding domain
    sur_width = sur_domain[:,1]-sur_domain[:,0]
    # determine the hyperrectangle defined by center and r_ratio
    rect_width = r_ratio*sur_width
    rect_domain = np.empty(sur_domain.shape)
    rect_domain[:,0] = center - .5*rect_width
    rect_domain[:,1] = center + .5*rect_width
    
    if np.all(np.greater_equal(sur_domain[:,0], rect_domain[:,0])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    elif np.all(np.less_equal(sur_domain[:,1], rect_domain[:,1])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None

    # determine the locations of the points for the 1st bounding layer
    layer1_left = rect_domain[:,0]-rect_width/(2*center_pts_per_edge)
    layer1_right = rect_domain[:,1]+rect_width/(2*center_pts_per_edge)

    interior_and_layer1 = list()
    for dim in xrange(sur_domain.shape[0]):
        # create interior points and 1st layer
        int_l1 = np.linspace(layer1_left[dim],
            layer1_right[dim], center_pts_per_edge[dim]+2)
        interior_and_layer1.append(int_l1)

    # use meshgrid to make the hyperrectangle shells
    # TODO: add a nice mdimensional implementation
    if sur_domain.shape[0] == 1:
        points = interior_and_layer1[0]
    elif sur_domain.shape[0] == 2:
        x, y = np.meshgrid(interior_and_layer1[0],
                interior_and_layer1[1], indexing='ij')
        points = np.vstack((x.ravel(), y.ravel()))
    elif sur_domain.shape[0] == 3:
        x, y, z = np.meshgrid(interior_and_layer1[0],
                interior_and_layer1[1], interior_and_layer1[2],
                indexing='ij') 
        points = np.vstack((x.ravel(), y.ravel(), z.ravel()))
    elif sur_domain.shape[0] == 4:
         x, y, z, u = np.meshgrid(interior_and_layer1[0],
                interior_and_layer1[1], interior_and_layer1[2],
                interior_and_layer1[3], indexing='ij')
        points = np.vstack((x.ravel(), y.ravel(), z.ravel(), u.ravel()))
    else:
        points = None
        print "There is no current implementation for dimension > 4."

    return (points, interior_and_layer1)

def center_and_layer2_points(center_pts_per_edge, center, r_ratio, sur_domain):
    """
    Generates a regular grid of center points that define the voronoi
    tesselation of exactly the interior of a hyperrectangle centered at
    ``center`` with sides of length ``r_ratio*sur_width`` and the layers
    of voronoi cells that bound these interior cells. The resulting voronoi
    tesselation exactly represents the hyperrectangle. The bounding voronoi
    cells are made finite by bounding them with an  additional layer to
    represent ``sur_domain``.
    
    This method can also be used to tile ``sur_domain`` with points to define
    voronoi regions if the user sets ``r_ratio = 1``.

    :param list() center_pts_per_edge: number of center points per edge and
        additional two points will be added to create the bounding layer
    :param center: location of the center of the hyperrectangle
    :type center: :class:`numpy.ndarray` of shape (mdim,)
    :param double r_ratio: ratio of the length of the sides of the hyperrectangle to
        the surrounding domain
    :param sur_domain: minima and maxima of each dimension defining the
        surrounding domain
    :type sur_domain: :class:`numpy.ndarray` of shape (mdim, 2)

    :rtype: tuple
    :returns (points, interior_and_layer1, interior_and_doublelayer) where
        where points is an :class:`numpy.ndarray` of shape (num_points, dim),
        interior_and_layer1 and interior_and_layer2 are lists of dim
        :class:`numpy.ndarray`s of shape (center_pts_per_edge+2,) and
        (center_pts_per_edge+4,) respectively.

    """
    if r_ratio > 1:
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    # determine the width of the surrounding domain
    sur_width = sur_domain[:,1]-sur_domain[:,0]
    # determine the hyperrectangle defined by center and r_ratio
    rect_width = r_ratio*sur_width
    rect_domain = np.empty(sur_domain.shape)
    rect_domain[:,0] = center - .5*rect_width
    rect_domain[:,1] = center + .5*rect_width
    
    if np.all(np.greater_equal(sur_domain[:,0], rect_domain[:,0])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    elif np.all(np.less_equal(sur_domain[:,1], rect_domain[:,1])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None

    # determine the locations of the points for the 1st bounding layer
    layer1_left = rect_domain[:,0]-rect_width/(2*center_pts_per_edge)
    layer1_right = rect_domain[:,1]+rect_width/(2*center_pts_per_edge)

    if r_ratio < 1:
        # determine the distance from the 1st layer to the boundary of the
        # surrounding domain
        dist2sur_left = sur_domain[:,0]-layer1_left
        dist2sur_right = sur_domain[:,1]-layer1_right

        # detemine the locations of the points for the 2nd boundary layer
        layer2_left = layer1_left + 2*dist2sur_left
        layer2_right = layer2_right + 2*dist2sur_right

    interior_and_layer1 = list()
    interior_and_doublelayer = list()
    for dim in xrange(sur_domain.shape[0]):
        # create interior points and 1st layer
        int_l1 = np.linspace(layer1_left[dim],
            layer1_right[dim], center_pts_per_edge[dim]+2)
        interior_and_layer1.append(int_l1)
        if r_ratio < 1:
            # add layers together using indexing fu
            int_l2 = np.zeros((int_l1.shape[0]+2,))
            int_l2[1:-1] = int_l1
            int_l2[0] = layer2_left[dim]
            int_l2[-1] = layer2_right[dim]
            interior_and_doublelayer.append(int_l2)
        else:
            interior_and_doublelayer.append(int_l1)

    # use meshgrid to make the hyperrectangle shells
    # TODO: add a nice mdimensional implementation
    if sur_domain.shape[0] == 1:
        points = interior_and_doublelayer[0]
    elif sur_domain.shape[0] == 2:
        x, y = np.meshgrid(interior_and_doublelayer[0],
                interior_and_doublelayer[1], indexing='ij')
        points = np.vstack((x.ravel(), y.ravel()))
    elif sur_domain.shape[0] == 3:
        x, y, z = np.meshgrid(interior_and_doublelayer[0],
                interior_and_doublelayer[1], interior_and_doublelayer[2],
                indexing='ij') 
        points = np.vstack((x.ravel(), y.ravel(), z.ravel()))
    elif sur_domain.shape[0] == 4:
         x, y, z, u = np.meshgrid(interior_and_doublelayer[0],
                interior_and_doublelayer[1], interior_and_doublelayer[2],
                interior_and_doublelayer[3], indexing='ij')
        points = np.vstack((x.ravel(), y.ravel(), z.ravel(), u.ravel()))
    else:
        points = None
        print "There is no current implementation for dimension > 4."

    return (points, interior_and_layer1, interior_and_doublelayer)

def edges_regular(center_pts_per_edge, center, r_ratio, sur_domain):
    """
    Generates a sequence of arrays describing the edges of the finite voronoi
    cells in each direction. The voronoi tesselation is defined by regular grid
    of center points that define the voronoi tesselation of exactly the
    interior of a hyperrectangle centered at ``center`` with sides of length
    ``r_ratio*sur_width`` and the layers of voronoi cells that bound these
    interior cells. The resulting voronoi tesselation exactly represents the
    hyperrectangle. The bounding voronoi cells are made finite by bounding them
    with an  additional layer to represent ``sur_domain``.
    
    This method can also be used to tile ``sur_domain`` with points to define
    voronoi regions if the user sets ``r_ratio = 1``.

    :param list() center_pts_per_edge: number of center points per edge and
        additional two points will be added to create the bounding layer
    :param center: location of the center of the hyperrectangle
    :type center: :class:`numpy.ndarray` of shape (mdim,)
    :param double r_ratio: ratio of the length of the sides of the hyperrectangle to
        the surrounding domain
    :param sur_domain: minima and maxima of each dimension defining the
        surrounding domain
    :type sur_domain: :class:`numpy.ndarray` of shape (mdim, 2)

    :rtype: tuple
    :returns (points, interior_and_layer1, interior_and_doublelayer) where
        where points is an :class:`numpy.ndarray` of shape (num_points, dim),
        interior_and_layer1 and interior_and_layer2 are lists of dim
        :class:`numpy.ndarray`s of shape (center_pts_per_edge+2,) and
        (center_pts_per_edge+4,) respectively.

    """
    if r_ratio > 1:
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    # determine the width of the surrounding domain
    sur_width = sur_domain[:,1]-sur_domain[:,0]
    # determine the hyperrectangle defined by center and r_ratio
    rect_width = r_ratio*sur_width
    rect_domain = np.empty(sur_domain.shape)
    rect_domain[:,0] = center - .5*rect_width
    rect_domain[:,1] = center + .5*rect_width
    
    if np.all(np.greater_equal(sur_domain[:,0], rect_domain[:,0])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None
    elif np.all(np.less_equal(sur_domain[:,1], rect_domain[:,1])):
        msg = "The hyperrectangle defined by this ratio is larger than the"
        msg += "original domain."
        return None

    rect_edges = list()
    rect_and_sur_edges = list()
    for dim in xrange(sur_domain.shape[0]):
        # create interior points and 1st layer
        int_l1 = np.linspace(rect[dim,0],
            rect[dim,1], center_pts_per_edge[dim]+1)
        rect_edges.append(int_l1)
        if r_ratio < 1:
            # add layers together using indexing fu
            int_l2 = np.zeros((int_l1.shape[0]+2,))
            int_l2[1:-1] = int_l1
            int_l2[0] = sur_domain[dim,0]
            int_l2[-1] = sur_domain[dim,1]
            rect_and_sur_edges.append(int_l2)
        else:
            rect_and_sur_edges.append(int_l1)
    return rect_and_sur_edges

def edges_from_points(points):
    """
    Given a sequence of arrays describing the voronoi points in each dimension
    that define a set of bounded hyperrectangular bins returns the edges of bins
    formed by voronoi cells along each dimensions.
    
    :param points: the coordindates of voronoi points that would generate
        these bins in each dimensions
    :type points: list of dim :class:`numpy.ndarray`s of shape (nbins+2,)

    :returns: edges, A sequence of arrays describing the edges of bins along each
        dimension.
    :rtype edges: A list() containing mdim :class:`numpy.ndarray`s of shape
        (nbins_per_dim+1,)

    """
    edges = list()
    for points_dim in points:
        edges.append((points_dim[1:]+points_dim[:-1])/2)
    return edges

def points_from_edges(edges):
    """
    Given a sequence of arrays describing the edges of bins formed by voronoi
    cells along each dimensions returns the voronoi points that would generate
    these cells.

    ..todo:: This method only creates points in the center of the bins. Needs
        Needs to be adjusted so that it creates points in the voronoi cell
        locations. 

    :param edges: A sequence of arrays describing the edges of bins along each
        dimension.
    :type edges: A list() containing mdim :class:`numpy.ndarray`s of shape
        (nbins_per_dim+1,)

    :returns: points, the coordindates of voronoi points that would generate
        these bins
    :rtype: :class:`numpy.ndarray` of shape (num_points, dim) where num_points
        = product(nbins_per_dim)

    """
    # create a point inside each of the bins defined by the edges
    centers = list()
    for e in edges:
        centers.append((e[1:]+e[:-1])/2)
    points = np.empty(dimensions)

def histogramdd_volumes(edges, points):
    """
    Given a sequence of arrays describing the edges of voronoi cells (bins)
    along each dimension and an 'ij' ordered sequence of points (1 per voronoi
    cell) returns a list of the volumes associated with these voronoic cells.

    :param edges: 
    :type edges:
    :param points: points used to define the voronoi tesselation (only the
        points that define regions of finite volumes)
    :type points: :class:`numpy.ndarrray` of shape (num_points, mdim)

    :returns: finite volumes associated with ``points``
    :rtype: :class:`numpy.ndarray` of shape (len(points),)

    """
    H, bins = np.histogramdd(points, edges, normed=False)
    volume = 1/(H*points.shape[0])
    # works as long as points are created with 'ij' indexing in meshgrid
    volume = volume.ravel()
    return volume

def simple_fun_approximation_uniform(points, volumes, rect_domain):
    """
    Given a set of points, the volumes associated with these points, and
    ``rect_domain`` creates a simple function approximation of a uniform
    distribution over the hyperrectangle defined by ``rect_domain``.

    :param points: points used to define the voronoi tesselation (only the
        points that define regions of finite volumes)
    :type points: :class:`numpy.ndarrray` of shape (num_points, mdim)
    :param list() volumes: finite volumes associated with ``points``
    :type points: :class:`numpy.ndarray` of shape (num_points,)
    :param rect_domain: minima and maxima of each dimension defining the
        hyperrectangle of uniform probability
    :type rect_domain: :class:`numpy.ndarray` of shape (mdim, 2)

    :rtype: tuple
    :returns: (rho_D_M, points, d_Tree) where ``rho_D_M`` and
        ``points`` are (mdim, M) :class:`~numpy.ndarray` and
        `d_Tree` is the :class:`~scipy.spatial.KDTree` for points

    """

    rect_left = np.repeat([rect_domain[:,0]], points.shape[0], 0)
    rect_right = np.repeat([rect_domain[:1,]], points.shape[0], 0)
    rect_left = np.all(np.greater_equal(points, rect_left), axis=1)
    rect_right = np.all(np.less_equal(points, rect_right), axis=1)
    inside = np.logical_and(rect_left, rect_right)
    rho_D_M = np.zeros(volumes.shape)
    rho_D_M[inside] = volumes[inside]/np.sum(volumes[inside])
    d_Tree = spatial.KDTree(points)
    return (rho_D_M, points, d_Tree)

