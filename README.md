# node-islands

Dennis Zethof - April-2017

Problem that the code tries to solve: there is a group of islands,
with each a certain populationsize and one main island. Determine the
most efficient way of connecting all islands to the main one. Then
determine the average time it will take for each inhabitant to be
connected to the main island. It will take one day to build one
kilometer of cable.

This is a "capacitated minimum spanning tree" problem and this code
employs the "Esau-Williams" algorithm to solve it. On average this
algorithm is found to give the best solution for this problem.
