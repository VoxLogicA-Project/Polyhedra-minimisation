// For more information see https://aka.ms/fsharp-console-apps

// Mieke Massink
// Based on PolyLogicA code by Gianluca Grilletti and Vincenzo Ciancia
// Date: 2023/11/24

// Usage instructions:
// Go to directory where source code is present
// From command line type: 
// > dotnet run <path_to_input_file.json> <path_to_output_file.json>
// where input file is a .json polyhedron model in the format for PolyLogicA
// and the output file is a .json poset model in the format for encoding to 
// an LTS in the mCRL2-format using the encoders written in python.

// NOTE!!: in the output poset .json replace the word "pnts" by "points"
// before applying an encoder

// SOLUTION: suggested by VC is to create a separate module for the poset related structures
// and then open that module in the right place. TBD!!!

module Poly.Main
open SimplexGraph
open PoSetType

[<EntryPoint>]
let main (argv : string array) = 
// Read two arguments: 
// filename of input .json (polyhedron model) and 
// filename of output .json (poset model)
    printfn "Start loading input file ..."
    let modelFileInput = loadTriaGraph argv[0]
    printfn "File loaded."
    let posetFileOutput = argv[1]
    //printfn "maze: %A " modelFileInput
    printfn "Filename input: %s" argv[0]
    printfn "Filename output: %s" posetFileOutput
    printfn "Starting to generate poset ...."
    savePoset modelFileInput posetFileOutput
    printfn "Poset generated."
    0