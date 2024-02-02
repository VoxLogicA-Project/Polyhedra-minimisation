module Poly.PoSet // was: VoxLogicA.TriaGraph

open System.Collections.Generic
//open Truth
open FSharp.Json

exception MyError of string

// Loading data format
type IntSimplex = { id : string; points : int list; atoms : string list }
type IntFileTriaGraph = { numberOfPoints : int; coordinatesOfPoints : int list list; atomNames : string list; simplexes : IntSimplex list }
// IntPoints format is used for the generation of a poset model
type IntPoints = { id : string  ; atoms : string list ; up : string list }

let loadFileTriaGraph filename = 
    Json.deserialize<IntFileTriaGraph>(System.IO.File.ReadAllText(filename))
 
//MM: Structure of PoSet for json
type PoSet = 
//MM: Here we would need "points" but that creates errors! Apparently it clashes with "points"
// used in the TriaGraph type.
    { pnts : IntPoints list                     // points : IntPoints list    
    }

//MM: structure of json input file of a polyhedron for PolyLogicA
type TriaGraph =
    {   NumPoints : int                         // Number of 0-dimensional simplexes
        NumSimplexes : int                      // Number of simplexes
        NumAtoms : int                          // Number of atoms in the structure
        Points : array<int>                     // The 0-dimensional simplexes
        CoordinatesOfPoint : int[,]             // A 2-dimensional array containing the <x,y,z> coordinates of the points
        ParentsNext : array<Set<int>>           // Given a simplex s of dim d, the (d+1)-simplexes with s as a face
        FacesNext: array<Set<int>>              // Given a simplex s of dim d, the (d-1)-dimensional faces of s
        Parents : array<Set<int>>               // Given a simplex s, the simplexes with s as a face (s included)
        Faces : array<Set<int>>                 // Given a simplex s, the faces of s (s included)
        PointsOfSimplex : array<Set<int>>       // Given a simplex s, the vertices of s
        AtomsOfSimplex : array<Set<int>>        // Given a simplex s, the set of atomic propositions true in s
        SimplexesOfAtom : array<Set<int>>       // Given an atomic proposition ap, the set of simplexes where ap is true
        NameOfAtom : array<string>              // Given an atomic proposition ap, the unique id associated to ap
        AtomOfName : string -> int              // Given the id of an atomic proposition, the corresponding atomic proposition
        SimplexId : array<string>  }            // Given a simplex s, the unique id associated to s


// MM: mkPosetTriaGraph generates the json structure for a poset file
// "pnts" should be "points" but this creates clashes 

let mkPosetTriaGraph triaGraph =   
    {  pnts = [
            for s in 0 .. triaGraph.NumSimplexes - 1 -> {
                id = s.ToString()
                atoms = [ for atom in triaGraph.AtomsOfSimplex.[s] -> triaGraph.NameOfAtom.[atom] ]
                up = [ for p in triaGraph.ParentsNext.[s] -> p.ToString() ]
            }
        ]   
    }
    

// MM: The following saves the poset in a json file with the desired structure
let savePoset triaGraph (filename :string) =
    let extension =
        let x = filename.Split(".")
        x.[x.Length - 1]
    match extension with
    | "json" ->
        let poset = mkPosetTriaGraph triaGraph
        System.IO.File.WriteAllText(filename,Json.serialize poset)
    | _ -> raise <| (MyError("Error: No .json file provided as output")) 


let private mkTriaGraph (fg : IntFileTriaGraph) =
    
    let numPoints = fg.numberOfPoints
    let numSimplexes = fg.simplexes.Length
    // let numAtoms = List.sumBy (fun simplex -> List.length simplex.atoms) fg.simplexes

    let points = Array.create fg.numberOfPoints 0
    let coordinatesOfPoint = Array2D.create numPoints 3 0 

    let parentsNext = Array.create numSimplexes Set.empty
    let facesNext = Array.create numSimplexes Set.empty

    let Parents = Array.create numSimplexes Set.empty
    let Faces = Array.create numSimplexes Set.empty
    let pointsOfSimplex = Array.create numSimplexes Set.empty

    let atomsOfSimplex = Array.create numSimplexes Set.empty
    let simplexesOfAtom = Array.create numSimplexes Set.empty
    
    let simplexId = Array.create numSimplexes ""


    // let pointDict = Dictionary<string,int>(numPoints)
    let simplexDict = Dictionary<string,int>(numSimplexes)
    // TODO: the following is an enormous upper bound
    // let apDict = Dictionary<string,int>(List.sumBy (fun simplex -> List.length simplex.atoms) fg.simplexes)
    let nameOfAtom = Array.ofList fg.atomNames
    let atomOfName = fun s -> Array.findIndex (fun x -> x = s) nameOfAtom
    let mutable atomsSet = Set.empty



    // This builds the simplexId, simplexDict, atomsOfSimplex, simplexesOfAtom and atomsSet
    // Moreover, it fills an auxiliary dictionary (hashConstructor) with keys the set of 
    // vertices and values the index of the simplex in the array
    let hashConstructor = new Dictionary<int list,int>()
    List.iteri
        (fun idx simplex ->
            hashConstructor.[List.sort simplex.points] <- idx
            simplexId.[idx] <- simplex.id
            simplexDict.[simplex.id] <- idx
            // Subiteration to build atomsOfSimplex, simplexesOfAtom and atomsSet
            List.iter
                (fun atom ->
                    let atomId = atomOfName atom
                    //     try apDict.[atom]
                    //     with :? KeyNotFoundException ->
                    //         let res = newAtomId()
                    //         apDict.[atom] <- res
                    //         res
                    atomsOfSimplex.[idx] <- Set.add atomId atomsOfSimplex.[idx]
                    simplexesOfAtom.[atomId] <- Set.add idx simplexesOfAtom.[atomId]
                    atomsSet <- atomsSet.Add(atomId)                 
                )
                simplex.atoms
        )
        fg.simplexes
    // This builds points and coordinatesOfPoint
    List.iteri
        (fun idx simplex ->
            points.[idx] <- simplex.points.[0]
            List.iteri
                (fun i c ->
                    coordinatesOfPoint.[idx, i] <- c
                    )
                fg.coordinatesOfPoints.[idx]
        )
        (List.filter
            (fun simplex -> (List.length simplex.points) = 1 )
            fg.simplexes
        )
    // This builds pointsOfSimplex
    List.iteri
        (fun idx simplex ->
            let mutable res = Set.empty
            List.iter
                (fun p ->
                    res <- Set.add p res
                    ()
                )
                simplex.points
            pointsOfSimplex.[idx] <- res
        )
        fg.simplexes
    
    // This builds the Parents, Faces, parentsNext and facesNext
    let rec remove i l =
        match i, l with
        | 0, x::xs -> xs
        | i, x::xs -> x::remove (i - 1) xs
        | i, [] -> failwith "index out of range"
    List.iteri
        (fun idx simplex ->
            // first add the faces
            let pts = List.sort simplex.points
            if List.length pts > 1 then 
                for i in 0 .. (List.length pts - 1) do
                    let pointsOfFace = remove i pts
                    let indexOfFace = hashConstructor.[pointsOfFace]
                    Faces.[idx] <- Set.union Faces.[idx] Faces.[indexOfFace]
                    facesNext.[idx] <- Set.add indexOfFace facesNext.[idx]
            Faces.[idx] <- Set.add idx Faces.[idx]
            // then add the parents
            Parents.[idx] <- Set.add idx Parents.[idx]
            for face in Faces.[idx] do
                Parents.[face] <- Set.add idx Parents.[face]
            for face in facesNext.[idx] do
                parentsNext.[face] <- Set.add idx parentsNext.[face]
        )
        fg.simplexes
            
    
    {   NumPoints = numPoints
        NumSimplexes = numSimplexes
        NumAtoms = Set.count atomsSet
        Points = points
        CoordinatesOfPoint = coordinatesOfPoint
        ParentsNext = parentsNext
        FacesNext = facesNext
        Parents = Parents
        Faces = Faces
        PointsOfSimplex = pointsOfSimplex
        AtomsOfSimplex = atomsOfSimplex
        SimplexesOfAtom = simplexesOfAtom
        NameOfAtom = nameOfAtom
        AtomOfName = atomOfName
        SimplexId = simplexId  }    


//MM: The following is used for poset generation
//MM: ErrorMsg.Logger.Debug is not working for me
let loadTriaGraph filename = 
    //ErrorMsg.Logger.Debug "Importing json file..."
    let tmp = loadFileTriaGraph filename
    //ErrorMsg.Logger.Debug "Processing json file..."
    let res = mkTriaGraph tmp
    //ErrorMsg.Logger.Debug "File loaded"
    res



    