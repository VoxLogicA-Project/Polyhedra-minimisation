import sys
import json




# load maze file
with open(sys.argv[1]) as f:
  mazeData = json.load(f)


nodesData = mazeData["nodes"]
gridSizes = {
  "x": max( [ x["coord"]["x"]  for x in nodesData ] ) + 1,
  "y": max( [ y["coord"]["y"]  for y in nodesData ] ) + 1,
  "z": max( [ z["coord"]["z"]  for z in nodesData ] ) + 1
}
# print(gridSizes)

# auxiliary function to encode the coordinates
def encodeCoords( coords ):
  return coords["x"] * gridSizes["y"] * gridSizes["z"] + coords["y"] * gridSizes["z"] + coords["z"]


linksData = mazeData["links"]
numberOfLinks = len(linksData) + 1


# OLD
## some constants
#POINTS_IN_THE_GRID      = gridSizes["x"] * gridSizes["y"] * gridSizes["z"] 
#POINTS_IN_A_ROOM        = 32+ 1    # these are 8 + (4x6) + 1, n.l. 1 in the middle, 8 corners and four on each side to attach corridors
#EDGES_IN_A_ROOM         = 90+32    # 8+(4x6)=32 (edges to middle point) and 12 (outerroom) and 6x(5+8)=78 (corridor related) gives 32+90 (optimal triangulization)
#TRIANGLES_IN_A_ROOM     = 60+90    # similar reasoning, once triangles are fixed
#TETHRAEDRONS_IN_A_ROOM  = 0 +60    # similar reasoning, once triangles are fixed
#SIMPLEXES_IN_A_ROOM     = POINTS_IN_A_ROOM + EDGES_IN_A_ROOM + TRIANGLES_IN_A_ROOM + TETHRAEDRONS_IN_A_ROOM
## Total nr of cells for one single room: 32+32+90+90+60+60+1=365
## POINTS_IN_A_CORRIDOR = 0
# END OLD

# MKE: NEW on 02/01/2024
# some constants
POINTS_IN_THE_GRID      = gridSizes["x"] * gridSizes["y"] * gridSizes["z"] 
POINTS_IN_A_ROOM        = 8  + 1    # these are 8 + 1, n.l. 1 in the middle, 8 corners
EDGES_IN_A_ROOM         = 18 + 8    # 8 (edges to middle point), 6 external diagonals and (4+4+4=) 12 outside frame 
TRIANGLES_IN_A_ROOM     = 12 + 18    # 12 (2 for each side) and 18 (= 1/2 * ((2*6*4)-12) = 36/2)
TETHRAEDRONS_IN_A_ROOM  = 0 + 12    # 12 (2 for each side of cube)
SIMPLEXES_IN_A_ROOM     = POINTS_IN_A_ROOM + EDGES_IN_A_ROOM + TRIANGLES_IN_A_ROOM + TETHRAEDRONS_IN_A_ROOM
# Total nr of cells for one single room:  12 + 30 + 26 + 8 + 1 = 76 + 1 = 77
# POINTS_IN_A_CORRIDOR = 0

TRANSLATE_DISTANCE_ROOMS  = 60

NUMBER_OF_ROOMS = POINTS_IN_THE_GRID
NUMBER_OF_CORRIDORS = numberOfLinks

POINTS_IN_A_CORRIDOR        = 0
EDGES_IN_A_CORRIDOR         = 8  # I count only 8 ! without counting those of rooms WAS 12
TRIANGLES_IN_A_CORRIDOR     = 12  # 8 (sides of cube) + 4 (internal tetrahedron)
TETHRAEDRONS_IN_A_CORRIDOR  = 5   # that is correct
SIMPLEXES_IN_A_CORRIDOR     = POINTS_IN_A_CORRIDOR + EDGES_IN_A_CORRIDOR + TRIANGLES_IN_A_CORRIDOR + TETHRAEDRONS_IN_A_CORRIDOR

INDEX_ROOM_SIMPLEXES = 0
INDEX_CORRIDOR_SIMPLEXES = NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM




# OLD
## generate grid of points of a default room
#roomPointCoords = [ [0,0,0],
#    [-6,-6,-6], [-6,-6, 6], [-6, 6,-6], [-6, 6, 6], # cube corners
#    [ 6,-6,-6], [ 6,-6, 6], [ 6, 6,-6], [ 6, 6, 6],
#    [-6,-2,-2], [-6,-2, 2], [-6, 2,-2], [-6, 2, 2], # square x-
#    [ 6,-2,-2], [ 6,-2, 2], [ 6, 2,-2], [ 6, 2, 2], # square x+
#    [-2,-6,-2], [-2,-6, 2], [ 2,-6,-2], [ 2,-6, 2], # square y-
#    [-2, 6,-2], [-2, 6, 2], [ 2, 6,-2], [ 2, 6, 2], # square y+
#    [-2,-2,-6], [-2, 2,-6], [ 2,-2,-6], [ 2, 2,-6], # square z-
#    [-2,-2, 6], [-2, 2, 6], [ 2,-2, 6], [ 2, 2, 6]  # square z+
#]
# END OLD

# MKE : NEW on 02/01/2024
# generate grid of points of a default room
roomPointCoords = [ [0,0,0],    # Point in the middle of the room
    [-6,-6,-6], [-6,-6, 6], [-6, 6,-6], [-6, 6, 6], # cube corners
    [ 6,-6,-6], [ 6,-6, 6], [ 6, 6,-6], [ 6, 6, 6],
#    [-6,-2,-2], [-6,-2, 2], [-6, 2,-2], [-6, 2, 2], # square x-
#    [ 6,-2,-2], [ 6,-2, 2], [ 6, 2,-2], [ 6, 2, 2], # square x+
#    [-2,-6,-2], [-2,-6, 2], [ 2,-6,-2], [ 2,-6, 2], # square y-
#    [-2, 6,-2], [-2, 6, 2], [ 2, 6,-2], [ 2, 6, 2], # square y+
#    [-2,-2,-6], [-2, 2,-6], [ 2,-2,-6], [ 2, 2,-6], # square z-
#    [-2,-2, 6], [-2, 2, 6], [ 2,-2, 6], [ 2, 2, 6]  # square z+
]
# END NEW



# MKE: OLD
## generate the simplexes of a default room
# outsidePoints       = [ [i] for i in range(1,len(roomPointCoords)) ]
# roomZeroSimplexes   = [ [0] ] + outsidePoints

# outsideEdges = [
#     [ 1, 2], [ 2, 6], [ 6, 5], [ 5, 1], # cube edges
#     [ 1, 3], [ 2, 4], [ 5, 7], [ 6, 8],
#     [ 3, 4], [ 4, 8], [ 8, 7], [ 7, 3],
#     [ 9,10], [10,12], [12,11], [11, 9], [ 9,12], # square faces x-
#     [13,14], [14,16], [16,15], [15,13], [14,15], # x+
#     [17,18], [18,20], [20,19], [19,17], [17,20], # y-
#     [21,22], [22,24], [24,23], [23,21], [22,23], # y+
#     [25,26], [26,28], [28,27], [27,25], [25,28], # z-
#     [29,30], [30,32], [32,31], [31,29], [30,31], # z+
#     [ 1, 9], [ 2,10], [ 4,12], [ 3,11], # other connections x-
#     [ 1,10], [ 2,12], [ 4,11], [ 3, 9],
#     [ 5,13], [ 6,14], [ 7,15], [ 8,16], # x+
#     [ 5,14], [ 6,16], [ 8,15], [ 7,13],
#     [ 1,17], [ 2,18], [ 6,20], [ 5,19], # y-
#     [ 1,18], [ 2,20], [ 6,19], [ 5,17],
#     [ 3,21], [ 4,22], [ 8,24], [ 7,23], # y+
#     [ 3,22], [ 4,24], [ 8,23], [ 7,21],
#     [ 1,25], [ 3,26], [ 7,28], [ 5,27], # z-
#     [ 1,26], [ 3,28], [ 7,27], [ 5,25],
#     [ 2,29], [ 4,30], [ 8,32], [ 6,31], # z+
#     [ 2,30], [ 4,32], [ 8,31], [ 6,29]
# ]
# END OLD

# MKE: NEW on 02/01/2024
# generate the simplexes of a default room
outsidePoints       = [ [i] for i in range(1,len(roomPointCoords)) ]
roomZeroSimplexes   = [ [0] ] + outsidePoints

outsideEdges = [
    [ 1, 2], [ 2, 6], [ 6, 5], [ 5, 1], # cube edges
    [ 1, 3], [ 2, 4], [ 5, 7], [ 6, 8],
    [ 3, 4], [ 4, 8], [ 8, 7], [ 7, 3],
    # [ 9,10], [10,12], [12,11], [11, 9], [ 9,12], # square faces x-
    # [13,14], [14,16], [16,15], [15,13], [14,15], # x+
    # [17,18], [18,20], [20,19], [19,17], [17,20], # y-
    # [21,22], [22,24], [24,23], [23,21], [22,23], # y+
    # [25,26], [26,28], [28,27], [27,25], [25,28], # z-
    # [29,30], [30,32], [32,31], [31,29], [30,31], # z+
    # [ 1, 9], [ 2,10], [ 4,12], [ 3,11], # other connections x-
    # [ 1,10], [ 2,12], [ 4,11], [ 3, 9],
    # [ 5,13], [ 6,14], [ 7,15], [ 8,16], # x+
    # [ 5,14], [ 6,16], [ 8,15], [ 7,13],
    # [ 1,17], [ 2,18], [ 6,20], [ 5,19], # y-
    # [ 1,18], [ 2,20], [ 6,19], [ 5,17],
    # [ 3,21], [ 4,22], [ 8,24], [ 7,23], # y+
    # [ 3,22], [ 4,24], [ 8,23], [ 7,21],
    # [ 1,25], [ 3,26], [ 7,28], [ 5,27], # z-
    # [ 1,26], [ 3,28], [ 7,27], [ 5,25],
    # [ 2,29], [ 4,30], [ 8,32], [ 6,31], # z+
    # [ 2,30], [ 4,32], [ 8,31], [ 6,29]
#    [1,7],[5,8],[6,4],[2,3],[4,7],[1,6] # diagonal edges outside (hopefully the right ones)
    [1,7],[6,7],[6,4],[1,4],[4,7],[1,6] # diagonal edges outside (hopefully the right ones)
]
# END NEW
roomOneSimplexes    = [ [0]+p for p in  outsidePoints ] + outsideEdges

# OLD
# outsideTriangles    = [
#     [ 9,10,12], [ 9,11,12], # from in to out, face x-
#     [ 1, 2,10], [ 1, 9,10], [ 2, 4,12], [ 2,10,12],
#     [ 4, 3,11], [ 4,12,11], [ 3, 1, 9], [ 3,11, 9],
#     [13,14,15], [14,15,16], # from in to out, face x+
#     [ 5, 6,14], [ 5,13,14], [ 6, 8,16], [ 6,14,16],
#     [ 8, 7,15], [ 8,15,16], [ 7, 5,13], [ 7,13,15],
#     [17,18,20], [17,19,20], # from in to out, face y-
#     [ 1, 2,18], [ 1,17,18], [ 2, 6,20], [ 2,18,20],
#     [ 6, 5,19], [ 6,19,20], [ 5, 1,17], [ 5,17,19],
#     [21,22,23], [22,23,24], # from in to out, face y+
#     [ 3, 4,22], [ 3,21,22], [ 4, 8,24], [ 4,22,24],
#     [ 8, 7,23], [ 8,23,24], [ 7, 3,21], [ 7,21,23],
#     [25,26,28], [25,27,28], # from in to out, face z-
#     [ 1, 3,26], [ 1,25,26], [ 3, 7,28], [ 3,26,28],
#     [ 7, 5,27], [ 7,27,28], [ 5, 1,25], [ 5,25,27],
#     [29,30,31], [30,31,32], # from in to out, face z+
#     [ 2, 4,30], [ 2,29,30], [ 4, 8,32], [ 4,30,32],
#     [ 8, 6,31], [ 8,31,32], [ 6, 2,29], [ 6,29,31]
# ]
# END OLD

# NEW
outsideTriangles    = [
    [1,7,3],[1,5,7],
#    [5,8,7],[5,6,8],
    [5,6,7],[6,7,8],
    [6,2,4],[6,8,4],
#    [1,2,3],[2,3,4],
    [1,2,4],[1,3,4],
    [3,7,4],[7,4,8],
    [1,6,5],[1,2,6]
]
# END NEW
roomTwoSimplexes    = [ [0]+p for p in outsideEdges ] + outsideTriangles

roomThreeSimplexes  = [ [0]+p for p in outsideTriangles ]


# auxiliary function to translate the coordinates
def translateCoordinates( listOfCoordinates, shiftX, shiftY, shiftZ ):
  result = [  [ c[0] + shiftX, c[1] + shiftY, c[2] + shiftZ ] for c in listOfCoordinates  ]
  return result

# auxiliary function to translate the simplex indices
def translateSimplexIndices( listOfSimplexIndices, shift ):
  result = [  [ x + shift for x in s ]  for s in listOfSimplexIndices  ]
  return result


# function that returns the simplexes of a corridor
def simplexesOfCorridor( corridor ):
    # ACHTUNG!!! This code assumes that the source of a corridor has lower indexes compared to the target
    sAdd = encodeCoords(corridor["source"]) * (POINTS_IN_A_ROOM) 
    tAdd = encodeCoords(corridor["target"]) * (POINTS_IN_A_ROOM) 
    simplexesPrototype = [
        [0,4], [1,5], [2,6], [3,7],           # edges (8)
        [1,4], [1,7], [2,4], [2,7],
        [0,1,4], [1,4,5], [1,5,7], [1,3,7],   # triangles (12)
        [2,3,7], [2,6,7], [0,2,4], [2,4,6],
        [1,2,4], [1,2,7], [1,4,7], [2,4,7],
        [0,1,2,4], [1,2,3,7], [2,4,6,7], [1,4,5,7], [1,2,4,7]  # tetrahedra (5)
    ]
    pointsMap = {}
    if corridor["target"]["x"] - corridor["source"]["x"] == 1:  # case x-corridor
        pointsMap = {
            # 0: sAdd+13,
            # 1: sAdd+14,
            # 2: sAdd+15,
            # 3: sAdd+16,
            # 4: tAdd+ 9,
            # 5: tAdd+10,
            # 6: tAdd+11,
            # 7: tAdd+12
            0: sAdd+5,
            1: sAdd+6,
            2: sAdd+7,
            3: sAdd+8,
            4: tAdd+1,
            5: tAdd+2,
            6: tAdd+3,
            7: tAdd+4
        }
    elif corridor["target"]["y"] - corridor["source"]["y"] == 1:  # case y-corridor
        pointsMap = {
            # 0: sAdd+21,
            # 1: sAdd+22,
            # 2: sAdd+23,
            # 3: sAdd+24,
            # 4: tAdd+17,
            # 5: tAdd+18,
            # 6: tAdd+19,
            # 7: tAdd+20
            0: sAdd+3,
            1: sAdd+4,
            2: sAdd+7,
            3: sAdd+8,
            4: tAdd+1,
            5: tAdd+2,
            6: tAdd+5,
            7: tAdd+6
        }
    elif corridor["target"]["z"] - corridor["source"]["z"] == 1:  # case z-corridor
        pointsMap = {
            # 0: sAdd+29,
            # 1: sAdd+30,
            # 2: sAdd+31,
            # 3: sAdd+32,
            # 4: tAdd+25,
            # 5: tAdd+26,
            # 6: tAdd+27,
            # 7: tAdd+28
            0: sAdd+2,
            1: sAdd+4,
            2: sAdd+6,
            3: sAdd+8,
            4: tAdd+1,
            5: tAdd+3,
            6: tAdd+5,
            7: tAdd+7
        }
    else:
        print("PROBLEM! " + str(corridor["target"]) + ", " + str(corridor["source"]))
    
    def mapSimplex( vertices ):
        return [ pointsMap[v] for v in vertices ]

    return [ mapSimplex(simp) for simp in simplexesPrototype ]




# Fill the coordinates of points
coordinatesOfPoints = []
for x in range(gridSizes["x"]):
  for y in range(gridSizes["y"]):
    for z in range(gridSizes["z"]):
      resTranslation = translateCoordinates( roomPointCoords, x * TRANSLATE_DISTANCE_ROOMS, y * TRANSLATE_DISTANCE_ROOMS, z * TRANSLATE_DISTANCE_ROOMS )
      coordinatesOfPoints.extend(resTranslation)


# Fill the list of simplexes with the room and corridor data
listOfSimplexes = []
# add simplexes of rooms
for roomIndex in range( NUMBER_OF_ROOMS ):
    listOfSimplexes.extend( translateSimplexIndices( roomZeroSimplexes , roomIndex * POINTS_IN_A_ROOM ) )
    listOfSimplexes.extend( translateSimplexIndices( roomOneSimplexes  , roomIndex * POINTS_IN_A_ROOM ) )
    listOfSimplexes.extend( translateSimplexIndices( roomTwoSimplexes  , roomIndex * POINTS_IN_A_ROOM ) )
    listOfSimplexes.extend( translateSimplexIndices( roomThreeSimplexes, roomIndex * POINTS_IN_A_ROOM ) )
# # add 1-simplexes of corridors
for corridor in linksData:
  listOfSimplexes.extend( simplexesOfCorridor(corridor) )
  






# Collect names of atoms data
atomNames = []
for node in nodesData:
  for atom in node["atoms"]:
    if atom not in atomNames:
      atomNames.append(atom)
# print(atomNames)


# atoms assigned to the rooms
atomEval = {}
for atom in atomNames:
  atomEval[atom] = [False for _ in range(NUMBER_OF_ROOMS)]
# print(atomEval)
for node in nodesData:
  roomIndex = encodeCoords( node["coord"] )
  for atom in node["atoms"]:
    atomEval[atom][roomIndex] = True
# print(atomEval)






# auxiliary function to append lists of values to a string
def stringOfList(vals):
  if len(vals) == 0:
    return '[]'
  result = '['
  for val in vals[:-1]:
    result += str(val) + ','
  result += str(vals[-1])
  result += ']'
  return result

def stringOfNames(vals):
  if len(vals) == 0:
    return '[]'
  result = '['
  for val in vals[:-1]:
    result += '"' + val + '",'
  result += '"' + str(vals[-1]) + '"'
  result += ']'
  return result



# Write the result on the file mazeModel.json
with open('mazeModel.json', "w") as outputFileModel:
    # prepare output of mazeModel.json
    print("Encoding of the model in the output string...")
    outputFileModel.write('{\n')
    outputFileModel.write('"numberOfPoints": ' + str( NUMBER_OF_ROOMS * POINTS_IN_A_ROOM ) + ',\n')
    outputFileModel.write('"coordinatesOfPoints": [\n')
    print("Saving the coordinates of points.")
    for coords in coordinatesOfPoints[:-1]:
        outputFileModel.write('  ' + stringOfList(coords) + ',\n')
    outputFileModel.write('  ' + stringOfList(coordinatesOfPoints[-1]) + '\n')
    outputFileModel.write('],\n')
    print("Saving the atom names.")
    outputFileModel.write('"atomNames": ' + stringOfNames( atomNames + ["corridor"] ) + ',\n')
    outputFileModel.write('"simplexes": [\n')
    print("Saving the simplexes:")
    for id, simplex in enumerate(listOfSimplexes[:-1]):
        # print("=> Saving simplex number " + str(id))
        outputFileModel.write('  {\n')
        outputFileModel.write('    "id": "s' + str(id) + '",\n')
        outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
        if id < NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM:
            outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_ROOM] ] ) + '\n')
        else:
            outputFileModel.write('    "atoms": [ "corridor" ]\n')
        # for atom in atomNames:
        #   if atomEval[atom][id]:
        #     outModel += '      "' + atom + '",\n'
        #   outModel = outModel[:-2] + '\n'
        # outModel += '      ]\n'
        outputFileModel.write('  },\n')
    id = len(listOfSimplexes)
    simplex = listOfSimplexes[-1]
    # print("=> Saving simplex number " + str(id))
    outputFileModel.write('  {\n')
    outputFileModel.write('    "id": "s' + str(id) + '",\n')
    outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
    if id < NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM:
        outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_ROOM] ] ) + '\n')
    else:
        outputFileModel.write('    "atoms": [ "corridor" ]\n')
    # for atom in atomNames:
    #   if atomEval[atom][id]:
    #     outModel += '      "' + atom + '",\n'
    #   outModel = outModel[:-2] + '\n'
    # outModel += '      ]\n'
    outputFileModel.write('  }\n')

    outputFileModel.write(']\n')
    outputFileModel.write('}')
    print("Model encoded successfully!")







# prepare the result for mazeAtoms.json
with open('mazeAtoms.json', "w") as outputFileModel:
    outputFileModel.write('{\n')
    for atom in atomNames[:-1]:
        # MKE
        print("Atom: " + atom)
        outputFileModel.write('  "' + atom + '": [\n')
        for val in atomEval[atom]:
            if val:
                outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_ROOM)
            else:
                outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_ROOM)
        outputFileModel.write('    false,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR - 1) + 'false\n')
        outputFileModel.write('  ],\n')
    atom = atomNames[-1]
    # MKE
    print("Last atom: " + atom)
    outputFileModel.write('  "' + atom + '": [\n')
    for val in atomEval[atom]:
        if val:
            outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_ROOM)
        else:
            outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_ROOM)
    outputFileModel.write('    false,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR - 1) + 'false\n')
    outputFileModel.write('  ],\n')
    # MKE
    # Added line for "corridor" atom
    outputFileModel.write('  "' + "corridor" + '": [\n')
    outputFileModel.write('    false,\n' * (NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM))
    outputFileModel.write('    true,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR - 1) + 'true\n')
    outputFileModel.write('  ]\n')
    outputFileModel.write('}')





