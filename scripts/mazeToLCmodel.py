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

# auxiliary function to encode the coordinates
def encodeCoords( coords ):
  return coords["x"] * gridSizes["y"] * gridSizes["z"] + coords["y"] * gridSizes["z"] + coords["z"]


linksData = mazeData["links"]
numberOfLinks = len(linksData) 


POINTS_IN_THE_GRID      = gridSizes["x"] * gridSizes["y"] * gridSizes["z"] 
POINTS_IN_A_ROOM        = 8      # 8 corners points of the room
EDGES_IN_A_ROOM         = 18     # 12 ribs and 6 diagonals 
TRIANGLES_IN_A_ROOM     = 12 + 4 # 12 on the sides of the room and 4 inside
TETHRAEDRONS_IN_A_ROOM  = 5      # 5 tetrahedra inside the room
SIMPLEXES_IN_A_ROOM     = POINTS_IN_A_ROOM + EDGES_IN_A_ROOM + TRIANGLES_IN_A_ROOM + TETHRAEDRONS_IN_A_ROOM
# Total nr of cells for one single room:   8 + 18 + 12 + 4 + 5 = 47
# POINTS_IN_A_CORRIDOR = 0

TRANSLATE_DISTANCE_ROOMS  = 60

NUMBER_OF_ROOMS = POINTS_IN_THE_GRID
NUMBER_OF_CORRIDORS = numberOfLinks

POINTS_IN_A_CORRIDOR        = 0
EDGES_IN_A_CORRIDOR         = 8   # 4 edges outside and 4 inside
TRIANGLES_IN_A_CORRIDOR     = 12  # 8 on the sides of the corridor and 4 inside
TETHRAEDRONS_IN_A_CORRIDOR  = 5   # 5 tetrahedra inside the corridor
SIMPLEXES_IN_A_CORRIDOR     = POINTS_IN_A_CORRIDOR + EDGES_IN_A_CORRIDOR + TRIANGLES_IN_A_CORRIDOR + TETHRAEDRONS_IN_A_CORRIDOR

INDEX_ROOM_SIMPLEXES = 0
INDEX_CORRIDOR_SIMPLEXES = NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM

# generate grid of points of a default room
roomPointCoords = [ #[0,0,0],    # Point in the middle of the room
    [-6,-6,-6], [-6,-6, 6], [-6, 6,-6], [-6, 6, 6], # cube corners
    [ 6,-6,-6], [ 6,-6, 6], [ 6, 6,-6], [ 6, 6, 6]
]

# generate the simplexes of a default room
outsidePoints       = [ [i] for i in range(1,len(roomPointCoords)) ]
roomZeroSimplexes   = [ [0] ] + outsidePoints 

outsideEdges = [
    [ 0, 1], [ 1, 5], [ 5, 4], [ 4, 0], # cube edges
    [ 0, 2], [ 1, 3], [ 4, 6], [ 5, 7],
    [ 2, 3], [ 3, 7], [ 7, 6], [ 6, 2],
    [0,6],[5,6],[5,3],[0,3],[3,6],[0,5] # diagonal edges outside 
]

roomOneSimplexes    =  outsideEdges 

outsideTriangles    = [ 
    [0,6,2],[0,4,6],
    [4,5,6],[5,6,7],
    [5,1,3],[5,7,3],
    [0,1,3],[0,2,3],
    [2,6,3],[6,3,7],
    [0,5,4],[0,1,5]
]

roomTwoSimplexes    = outsideTriangles + [p for p in [[0,6,5],[0,3,5],[0,6,3],[6,3,5]]]

roomThreeSimplexes  = [p for p in [[0,5,4,6],[0,1,5,3],[0,2,3,6],[5,6,7,3],[0,5,3,6]]]

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
            0: sAdd+4,
            1: sAdd+5,
            2: sAdd+6,
            3: sAdd+7,
            4: tAdd+0,
            5: tAdd+1,
            6: tAdd+2,
            7: tAdd+3
        }
    elif corridor["target"]["y"] - corridor["source"]["y"] == 1:  # case y-corridor
        pointsMap = {
            0: sAdd+2,
            1: sAdd+3,
            2: sAdd+6,
            3: sAdd+7,
            4: tAdd+0,
            5: tAdd+1,
            6: tAdd+4,
            7: tAdd+5
        }
    elif corridor["target"]["z"] - corridor["source"]["z"] == 1:  # case z-corridor
        pointsMap = {
            0: sAdd+1,
            1: sAdd+3,
            2: sAdd+5,
            3: sAdd+7,
            4: tAdd+0,
            5: tAdd+2,
            6: tAdd+4,
            7: tAdd+6
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
# add 1-simplexes of corridors
for corridor in linksData:
  listOfSimplexes.extend( simplexesOfCorridor(corridor) )

  

# Collect names of atoms data
atomNames = []
for node in nodesData:
  for atom in node["atoms"]:
    if atom not in atomNames:
      atomNames.append(atom)


# atoms assigned to the rooms
atomEval = {}
for atom in atomNames:
  atomEval[atom] = [False for _ in range(NUMBER_OF_ROOMS)]
for node in nodesData:
  roomIndex = encodeCoords( node["coord"] )
  for atom in node["atoms"]:
    atomEval[atom][roomIndex] = True



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
        outputFileModel.write('  },\n')
    id = len(listOfSimplexes)
    simplex = listOfSimplexes[-1]
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
        outputFileModel.write('  "' + atom + '": [\n')
        for val in atomEval[atom]:
            if val:
                outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_ROOM)
            else:
                outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_ROOM)
        outputFileModel.write('    false,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR -1) + 'false\n')
        outputFileModel.write('  ],\n')
    atom = atomNames[-1]
    outputFileModel.write('  "' + atom + '": [\n')
    for val in atomEval[atom]:
        if val:
            outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_ROOM)
        else:
            outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_ROOM)
    outputFileModel.write('    false,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR -1) + 'false\n')
    outputFileModel.write('  ],\n')

    # Added line for "corridor" atom
    outputFileModel.write('  "' + "corridor" + '": [\n')
    outputFileModel.write('    false,\n' * (NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM))
    outputFileModel.write('    true,\n' * (NUMBER_OF_CORRIDORS * SIMPLEXES_IN_A_CORRIDOR -1) + 'true\n')
    outputFileModel.write('  ]\n')
    outputFileModel.write('}')





