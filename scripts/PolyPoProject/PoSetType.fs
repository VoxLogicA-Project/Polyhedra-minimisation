module Poly.PoSetType

open FSharp.Json
open SimplexGraph

//MM: Define basic error message mechanism
exception MyError of string

//MM: IntPoints format is used for the generation of a poset model
type IntPoints = { id : string  ; atoms : string list ; up : string list }

//MM: Structure of PoSet for json
type PoSet = 
    { points : IntPoints list    
    }

// MM: mkPosetTriaGraph generates the json structure for a poset file
let mkPosetTriaGraph triaGraph =   
    {  points = [
            for s in 0 .. triaGraph.NumSimplexes - 1 -> {
                id = s.ToString()
                atoms = [ for atom in triaGraph.AtomsOfSimplex.[s] -> triaGraph.NameOfAtom.[atom] ]
                up = [ for p in triaGraph.ParentsNext.[s] -> p.ToString() ]
            }
        ]   
    }
    

// MM: The following saves the poset in a json file with the desired structure
let savePoset triaGraph (filename :string) =
    // MM next four lines added to see what parentsNext does
    printfn("ParentsNext of 0: ")
    let tmp = [for p in triaGraph.ParentsNext.[0] -> p.ToString()]
    for i in tmp do
         printfn "%s" i
    let extension =
        let x = filename.Split(".")
        x.[x.Length - 1]
    match extension with
    | "json" ->
        let poset = mkPosetTriaGraph triaGraph
        System.IO.File.WriteAllText(filename,Json.serialize poset)
    | _ -> raise <| (MyError("Error: No .json file provided as output")) 
