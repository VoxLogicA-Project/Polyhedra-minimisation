// For more information see https://aka.ms/fsharp-console-apps
//
// This is a copy of the Amazer code by Vincenzo 
// It is used as one of the steps to generate a maze in json format from a maze in .maze format
//
// It runs as follows:
// Go to the directory of this file in a terminal/command line
// > dotnet run <input.maze> > <output.json>
// 
// The result is an intermediate json file for further transformation into input for PolyLogica
// using the python script mazeToModel.py
// One of the outputs of the above python script, namely the xxxModel.json file,
// can be used as input to the fsharp procedure in PolyPoProject. The latter generates
// a json file with a poset structure. That, in turn, can be used by one of the encoders for eta
// to create a .mcrl2 file of an LTS that with the mCRL2 tool set can be minimised (via branching bisimulation)
// The last setp can also be performed with the python script min_spec.py
// The resulting minimised model can be visually inspected using ltsgraph provided by mCRL2.

open System
open System.Text.RegularExpressions

//printfn "Hello from F#"

// module Mazer =

type coord = {| x : int; y : int; z : int|}
type t = {| coord: coord; atoms: seq<char>; xplus : bool; yplus : bool; zplus : bool |}

let (|Regex|_|) pattern input =
    let m = Regex.Match(input, pattern)
    if m.Success then Some(List.tail [ for g in m.Groups -> g.Value ])
    else None

let number list =
        Seq.zip (Seq.initInfinite id) list

let splitWhile pred s =
        (List.takeWhile pred s,List.skipWhile pred s)

let splitPred pred s =
        let s' = 
            Seq.fold 
                (fun st el ->
                    match (pred el),st with
                    | true,_ -> [el]::st
                    | false,[] -> [[el]]
                    | false,(group::groups) -> (el::group)::groups) 
                []
                s
        Seq.rev (Seq.map Seq.rev s')

let findAllIndexes pred s =
        number s |>
        Seq.fold
            (fun acc (n,el) -> if pred el then n::acc else acc)
            [] |>
        Seq.rev

let rec splitBy2 s =    
        Seq.pairwise s |>
        number |>
        Seq.filter (fun (n,x) -> n % 2 = 0) |>
        Seq.map snd 
let processEvenLine line =                
        let nodoids = splitPred (fun (_,c) -> c = '[' || c = '(' ) (number line)
        seq {
            for nodoid in nodoids do
                let (start,bracket) = Seq.head nodoid 
                let zlink = bracket = '['
                let atomsRest = splitPred (fun (_,c) -> c = ']' || c = ')') nodoid  
          
                let atoms = Seq.tail <| Seq.head atomsRest
                let finish = 
                    Seq.tail atomsRest |>
                    Seq.concat |>
                    Seq.head |>
                    fst
                let xlink = Seq.exists (fun (_,c) -> c = '-') (Seq.concat (Seq.tail 
                    atomsRest))
                start,finish,(Seq.map snd atoms),zlink,xlink
        }
    
let processOddLine line startEndIds =    
        let idxs = Seq.toList <| findAllIndexes (fun c -> c = '|') line
        let rec consume idxs tuples acc =
            match (idxs,tuples,acc) with
            | [],_,_ -> acc
            | _,[],_ -> failwith "too many |"
            | idx::idxs',(a,b,id)::pairs',_ ->
                if a <= idx && idx <= b 
                then consume idxs' pairs' (id::acc)
                else consume idxs pairs' acc
        Seq.rev <| consume idxs startEndIds []


let p = processEvenLine "[fda]----(ba)   [c][]"

[<EntryPoint>]
let main argv =
    let nodes = Set.empty
    let arcs = Set.empty
    let floors =
        IO.File.ReadAllLines(argv.[0]) |>        
        List.ofArray |>        
        List.filter (fun s -> not <| Regex.IsMatch(s,"^\s*//")) |>
        List.fold 
            (fun floors line -> 
            match line,floors with
            | Regex @"^\s*-+\s*$" _,_ ->            
                []::floors 
            | Regex @"^\s*$" _,_ ->
                floors 
            | _,[] -> 
                [[line]]
            | _,floor::moreFloors -> 
                (line::floor)::moreFloors) 
            [] |>
        Seq.map Seq.rev |>
        Seq.rev

    let firstPass = seq {        
        for (fid,floor) in number floors do  
            for (lid,(even,odd)) in number (splitBy2 (Seq.append floor (seq {""}
                ))) do   
                let nctx = number <| processEvenLine even                      
                let xtc = Set.ofSeq <| processOddLine odd (Seq.toList (Seq.map (
                    fun (i,(s,f,_,_,_)) -> (s,f,i)) nctx))
                for (cid,(_,_,a,z,x)) in nctx do
                           yield {| coord = {| x = cid; y = lid; z = fid |}; atoms = a;
                            xplus = x; yplus = Set.contains cid xtc; zplus = z |}
        }    
    
    let nx (a : coord) = {| a with x = a.x + 1 |}
    let ny (a : coord) = {| a with y = a.y + 1 |}
    let nz (a : coord) = {| a with z = a.z + 1 |}
    let px (a : coord) = {| a with x = a.x - 1 |}
    let py (a : coord) = {| a with y = a.y - 1 |}
    let pz (a : coord) = {| a with z = a.z - 1 |}
        
    let links = 
        seq { 
            for (x : t) in firstPass do                                         
       
                for (t,v) in
                    seq {
                        (x.xplus,{| source = x.coord; target = nx x.coord |})
                        (x.yplus,{| source = x.coord; target = ny x.coord |})
                        (x.zplus,{| source = x.coord; target = nz x.coord |})
                    } do
                    yield (t,v)

        } |>
        Seq.filter (fun (t,v) -> t) |>
        Seq.map snd

    let linkSet = Set.ofSeq links 

    let nodes = 
        seq {
                        for node in firstPass do
                                yield {| node with 
                                            xminus = Set.contains {| source = px node.coord; target = node.coord |} linkSet
                                            yminus = Set.contains {| source = py node.coord; target = node.coord |} linkSet
                                            zminus = Set.contains {| source = pz node.coord; target = node.coord |} linkSet 
                                        |}                    
                        }

    
    let result = {| nodes = nodes; links = links |}

    //printfn (result)
    printfn "%s" <| Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented)

    0
// module PigLatin =
//     let toPigLatin (word: string) =
//         let isVowel (c: char) =
//             match c with
//             | 'a' | 'e' | 'i' |'o' |'u'
//             | 'A' | 'E' | 'I' | 'O' | 'U' -> true
//             |_ -> false
        
//         if isVowel word[0] then
//             word + "yay"
//         else
//             word[1..] + string word[0] + "ay"

// [<EntryPoint>]
// let main args =
//     for arg in args do
//         let newArg = PigLatin.toPigLatin arg
//         printfn "%s in Pig Latin is: %s" arg newArg

//     0