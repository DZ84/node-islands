import matplotlib.pyplot as plt

#########################################################################
# Dennis Zethof - April-2017
# Problem that the code tries to solve: there is a group of islands,
# with each a certain populationsize and one main island. Determine the
# most efficient way of connecting all islands to the main one. Then
# determine the average time it will take for each inhabitant to be
# connected to the main island. It will take one day to build one
# kilometer of cable.
#
# This is a "capacitated minimum spanning tree" problem and this code
# employs the "Esau-Williams" algorithm to solve it. On average this
# algorithm is found to give the best solution for this problem.

def main():
    """
    Will open file with name "info_isles.txt" and search for island groups
    to run through the algorithm. Will give results per group. Default file
    consists of 9 examplecases of which the results will be printed and
    plotted consecutively.
    """
    import os

    # Open the file
    file_path = os.path.dirname(__file__) + "\\info_isles.txt"
    list_allgroups = parse_file(file_path)

    # Start the proces per found group
    array_islands = []
    for index, list_group in enumerate(list_allgroups, start=1):

        # Create classes per island in group and put them in an array
        array_islands = set_array_islands(list_group)

        # Run algorithm that determins how the cables should be put
        set_cables(array_islands)

        # Calculate the average time each island inhabitant should wait
        # for their internetconnection
        time = det_time(array_islands)

        # Print result in determined format
        parse_output(index, time)

        ##################################################################
        # Following code within this loop generates a plot of the solution

        # Retrieve previously calculated coordinates
        island_edges, island_coords = get_coordinates(array_islands)

        # Use retrieved values for constructing the plot
        plot_islands(island_edges, island_coords)

        # Retrieve population sizes of each island within the group
        pop_info = get_population(array_islands)

        # Use the population sizes to specify nodesizes in plot
        plot_areas(island_coords, pop_info)

        # Actual rendering of the plot
        plt.show()


class Island:
    """
    Holds relevant details of a specific island.

    -Coordinates of island (in meters)
    -Number of inhabitants
    -Distance to next island. By default it is set to the main island
    """
    dist_i = None
    connection = 0

    def __init__(self, xi, yi, mi, xm, ym):
        self.coord = (xi, yi)
        self.m = mi
        self.dist_i = det_dist(self.coord, (xm, ym))


def det_dist(coord, coord_2):
    """
    Determine the euclidean distance between two points.
    """
    d_x = coord_2[0] - coord[0]
    d_y = coord_2[1] - coord[1]
    return (d_x**2 + d_y**2)**(0.5)


def set_array_islands(list_islands):
    """
    Converts list to array of initialised island classes.
    """
    _array_islands = []
    for c in range(len(list_islands)):
        _array_islands.append(Island(*list_islands[c][:], *list_islands[0][:2]))

    return _array_islands


def set_cables(array_islands):
    """
    Determine and set the most efficient way of connecting all the islands
    to the main island. This uses the Esau-Williams algorithm. No maximum
    groupsize (treesize) can be specified.
    """
    # distance from main island to main island is 0
    array_islands[0].dist_i = 0

    # main island is where the connection stops
    array_islands[0].connection = -1

    # amount of islands in array
    island_number = len(array_islands)

    while True:
        isle_maxs = []

        # loop through islands and determine which can gain most (t_max) from switching link
        for i in range(1, island_number):

            # if connection to main island is already removed isle is already processed
            # this restriction is specific for the Esau-Williams algorithm
            if array_islands[i].connection != 0:
                continue

            # loop through each other islands and determine their tradeoff functions
            isle_calcs = []
            for i2 in range(1, island_number):

                # avoid connecting with itself
                if i2 == i:
                    continue

                # check if connecting to island would cause it to disconnect from the main island
                if find_island(array_islands, i2, i) == -2:
                    continue

                # calculate distance to other island
                dist = det_dist(array_islands[i].coord, array_islands[i2].coord)

                # the tradeoff function
                diff = array_islands[i].dist_i - dist

                # collect results
                isle_calcs.append((diff, dist, i, i2))

            # select and collect best option to reconnect for this specific island(i)
            isle_maxs.append(get_max(isle_calcs))

        # select best option to reconnect between all islands
        t_max = get_max(isle_maxs)

        # if no improvement could be made, stop while loop
        # don't have to worry about infinite loops now, because
        # if an island is still directly attached to the main island
        # and an improvement can be made, it will be made
        # in part because groupsize is no factor and "illigal" switches
        # are already prevented and can not end up as t_max.
        if t_max[0] <= 0:
            break

        # assign improvement to relevant island
        array_islands[t_max[2]].dist_i = t_max[1]
        array_islands[t_max[2]].connection = t_max[3]


def get_max(list_tuples):
    """
    Returns from a list a tuple which has the highest value as first element.
    If empty, it returns -2's
    """
    if len(list_tuples) == 0:
        return (-2, -2, -2, -2)

    # evaluate the max result
    found = max(tup[0] for tup in list_tuples)
    for result in list_tuples:
        if result[0] == found:
            return result


def find_island(array_islands, index, node):
    """
    Tracks the islands along the connections that are made in a
    recursive matter. It stops when specific nodes are found along
    the path.

    Codes:
     0 = connected to the main island
    -1 = island is itself the main island
    -2 = the node was located in de path

    Error:
        will not stop traversing when loop is recalled more often than
        there are actual islands
    """
    # function will stop traversing when these conditions are met
    if array_islands[index].connection == 0:
        return 0
    elif array_islands[index].connection == -1:
        return -1
    elif array_islands[index].connection == node:
        return -2

    # function calls itself with island that it is connected to
    result = find_island(array_islands, array_islands[index].connection, node)

    # if function found itself somewhere along the path, it will have returned -2
    if result == -2:
        return -2

    # arbitrary value is returned
    return array_islands[index].connection


def distance_main_island(array_islands, index):
    """
    Calculates the distance of specific island to main island
    in a recursive matter.

    Codes:
     0 = connected to the main island
    -1 = island is itself the main island
    """
    # function will stop traversing when these conditions are met
    if array_islands[index].connection == -1:
        return 0
    elif array_islands[index].connection == 0:
        return array_islands[index].dist_i

    # function calls itself with island that it is connected to
    result = distance_main_island(array_islands, array_islands[index].connection)

    # return added distances of current island with distances of
    # islands found closer to the main land
    return result + array_islands[index].dist_i


def det_time(array_islands):
    """
    Perform calculation of average time per inhabitant.
    """
    sum_num = 0
    sum_den = 0

    # first lines of code here are for printing details per island
    for i, isle in enumerate(array_islands):

        # print("Island number: " + str(i) + "\n connection: " + str(isle.connection) +
        #       "\n distance to next island: " + str(isle.dist_i) + "\n distance to main island: " +
        #       str(distance_main_island(array_islands, i)) + "\n population: " + str(isle.m))

        # calculate distance of specific island to main island, multiply this times
        # the number of inhabitants, and add result for all islands
        sum_num += distance_main_island(array_islands, i) * isle.m

        # calculate total amount of inhabitants
        sum_den += isle.m

    # return the average
    return sum_num/sum_den


def parse_file(path_file):
    """
    Read file according to specified format.
    """
    file = open(path_file)
    _list_allgroups = []

    # Loop through file lines is started
    while True:

        # read in line of code
        # seperate variable is assigned for stripped version
        # in order to stay able to evaluate "line" for == ""
        line = file.readline()
        s_line = line.strip()

        # skips through rows that do not contain information fitting the specified format
        # continues until number with 1 or 2 digits is reached.
        # returns when end of file is reached
        while len(s_line) > 2 or len(s_line) == 0 or any(not d.isdigit() for d in s_line):

            # if at end of file, log and break loop
            if line == "":
                return _list_allgroups

            line = file.readline()
            s_line = line.strip()

        # should not be more than 50 islands per group
        if int(s_line) > 50:
            raise NotImplementedError("Too many islands in group.")

        # load found group in file to list
        _list_allgroups.append(read_group(file))

def read_group(file):
    """
    When a group was found in file, this will read it
    in accordance with the format.
    """
    _list_group = []

    line = None
    s_line = None

    # loop until end of group is reached
    while s_line != 0:
        line = file.readline()
        s_line = line.split()

        # splits line of islanddetails (coordinates
        # and number of inhabitants)
        info_isle = line.split()

        # raise error if format is unexpected, or stop loop
        # when end of group is found as expected
        if len(info_isle) > 3:
            raise NotImplementedError("Not correct format.")
        elif line == "":
            raise NotImplementedError("Not correct format.")
        elif len(info_isle) == 1 and int(info_isle[0]) != 0:
            raise NotImplementedError("Not correct format.")
        elif len(info_isle) == 1:
            break

        # collect islanddetails in list as integers
        _list_group.append([int(element) for element in info_isle])

    return _list_group

def parse_output(index, time):
    """
    Coordinates are in kilometers, average time in days
    """
    print("Island Group: " + str(index) + " Average " + str(round(time, 2)))

def get_coordinates(array_islands):
    """
    First extract the connection (edge) that every island connects to, then
    extract the coordinate of that island. Edges are returned in an array of
    tuples, coordinates in a dictionary of arrays.
    """
    # retrieve the connection
    edges = []
    for index, isle in enumerate(array_islands[1:], start=1):
        edges.append((index, isle.connection))

    # retrieve the coordinates
    pos = dict((index, [*isle.coord]) for index, isle in enumerate(array_islands))

    return edges, pos

def plot_islands(edges, coords):
    """
    For all edges in islandgroup, the coordinates are extracted, start and end.
    Those are then directly set as parameters for plotting.
    """
    for edge in edges:
        plt.plot([coords[edge[0]][0], coords[edge[1]][0]],
                 [coords[edge[0]][1], coords[edge[1]][1]],
                 c="black")

def get_population(array_islands):
    """
    Extract the population size for every island within the island group. Return
    those as an array.
    """
    pops = []
    for index, isle in enumerate(array_islands):
        pops.append(isle.m)

    return pops

def plot_areas(coords, pops):
    """
    Extract populationsizes for each island, these are then added to the
    plot as circles for each island as an illustration of populationsize.
    """
    areas = []
    for pop in pops:
        areas.append(pop)

    for index in range(len(coords)):
        plt.scatter(coords[index][0], coords[index][1],
                    s=areas[index], c="lightsteelblue")
