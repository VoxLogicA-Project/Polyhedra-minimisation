import sys
import json


# load polyhedral model file
import json
with open(sys.argv[1]) as f:
    modelData = json.load(f)

# load atoms file
with open(sys.argv[2]) as g:
  atomsData = json.load(g)

for atomName in atomsData:
   print(atomName)
   index = 0
   # Optional: below select which atoms to insert
   if atomName in ["b2","b3","b4","b5","b6","b7","b8","b9","b10"]:
      for ap in atomsData[atomName]:
          if ap:
             print(ap)
             #print(modelData['simplexes'][index]['atoms'])
             modelData['simplexes'][index]['atoms'] = modelData['simplexes'][index]['atoms'] + [atomName]
             #print(modelData['simplexes'][index]['atoms'])
          print(index)
          index = index +1

#def replc (ap):
#    ap.replace("blue","orange")

# for item in modelData['simplexes']:
#     if 'blue' in item['atoms']:
#        item['atoms'][item['atoms'].index('blue')] = "orange"

with open('updated_model.json', 'w') as f:
    json.dump(modelData, f, indent=4, separators=(',',': ')) #separators=(',',':')




#atomicPropName = atomsData["b0"]

# Write the result on the file mazeModel.json
# with open('mazeModel.json', "w") as outputFileModel:
#     # prepare output of mazeModel.json
#     print("Encoding of the model in the output string...")
#     outputFileModel.write('{\n')
#     outputFileModel.write('"numberOfPoints": ' + str( NUMBER_OF_ROOMS * POINTS_IN_A_ROOM ) + ',\n')
#     outputFileModel.write('"coordinatesOfPoints": [\n')
#     print("Saving the coordinates of points.")
#     for coords in coordinatesOfPoints[:-1]:
#         outputFileModel.write('  ' + stringOfList(coords) + ',\n')
#     outputFileModel.write('  ' + stringOfList(coordinatesOfPoints[-1]) + '\n')
#     outputFileModel.write('],\n')
#     print("Saving the atom names.")
#     outputFileModel.write('"atomNames": ' + stringOfNames( atomNames + ["corridor"] ) + ',\n')
#     outputFileModel.write('"simplexes": [\n')
#     print("Saving the simplexes:")
#     for id, simplex in enumerate(listOfSimplexes[:-1]):
#         # print("=> Saving simplex number " + str(id))
#         outputFileModel.write('  {\n')
#         outputFileModel.write('    "id": "s' + str(id) + '",\n')
#         outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
#         if id < NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM:
#             outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_ROOM] ] ) + '\n')
#         else:
#             outputFileModel.write('    "atoms": [ "corridor" ]\n')
#         outputFileModel.write('  },\n')
#     id = len(listOfSimplexes)
#     simplex = listOfSimplexes[-1]
#     outputFileModel.write('  {\n')
#     outputFileModel.write('    "id": "s' + str(id) + '",\n')
#     outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
#     if id < NUMBER_OF_ROOMS * SIMPLEXES_IN_A_ROOM:
#         outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_ROOM] ] ) + '\n')
#     else:
#         outputFileModel.write('    "atoms": [ "corridor" ]\n')
#     # for atom in atomNames:
#     #   if atomEval[atom][id]:
#     #     outModel += '      "' + atom + '",\n'
#     #   outModel = outModel[:-2] + '\n'
#     # outModel += '      ]\n'
#     outputFileModel.write('  }\n')

#     outputFileModel.write(']\n')
#     outputFileModel.write('}')
#     print("Model encoded successfully!")