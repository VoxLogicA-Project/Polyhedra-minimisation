module ClassAtoms.StateLabels

open System
open System.Text.Json
open System.Text.Json.Serialization
open FSharp.Collections 

let loadFile filePath  = 
     System.IO.File.ReadLines(filePath) |> Seq.toList

// For the blue and red triangle example we should get that:
// t1_0 corresponds to lts state label 1
// t1_1 corresponds to lts state label  2
// t1_2 to 3
// t1_3 to 5
// t1_4 to 6
// t1_5 to 4
// t1_6 to 7 

let rec insert v i l =
    match i, l with
    | 0, xs -> v::xs
    | i, x::xs -> x::insert v (i - 1) xs
    | i, [] -> failwith "index out of range"
// inserts a value v at index i in list l

let rec remove i l =
    match i, l with
    | 0, x::xs -> xs
    | i, x::xs -> x::remove (i - 1) xs
    | i, [] -> failwith "index out of range"
// removes element i from list l

let replace v i l =
    insert v i (remove i l)

let getIndex (n : int) (l : list<int>)=
    [|for i = 0 to l.Length-1 do
        if l.[i] = n then i|].[0]
// gives the index of the first occurrence of item n in a list

let rec dropFirst (i:int) l =
    match i, l with
    | 0, x::xs -> x::xs
    | i, x::xs -> dropFirst (i - 1) xs
    | i, [] -> failwith "index out of range"
// Drops the first i items from a list l

let isDigit c = Char.IsDigit c
// checks whether character is a digit

let strip chars = String.collect (fun c -> if Seq.exists((=)c) chars then "" else string c)
// use: strip "xyz" "12x45yz" gives "1245"

let splitString (s:string) =
  let i = s.IndexOfAny("0123456789 ,".ToCharArray())
  if i < 0 then None 
  else Some(s.Substring(0, i), s.Substring(i+1))
// splits a string into two parts whenever it encounters a digit (0-9) a space or a comma

let splitStringLeftOfDot (s:string) =
    let i = s.IndexOfAny(".=".ToCharArray())
    if i < 0 then ""
    else s.Substring(0, i)
// splits a string taking the left part whenever it encounters a dot or equal character

let splitStringRightOfUnderscore (s:string) =
    let i = s.IndexOfAny("_".ToCharArray())
    if i < 0 then ""
    else s.Substring(i+1)




// toLtsState finds state-labels in the text file produced by ltspp 
// after removing the first three lines and the last (2?)
// Maybe one should first make each three lines into one line
let toLtsState str = 
    let rec loop xs stack (state : string) = 
        match (xs, stack, state) with
        | '=' :: ys, '='::stack, state -> loop ys stack state
        | '=' :: ys,  stack, state -> loop ys ('=' :: stack) (state)        
        | '0' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "0")
        | '1' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "1")
        | '2' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "2")
        | '3' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "3")
        | '4' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "4")
        | '5' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "5")
        | '6' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "6")
        | '7' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "7")
        | '8' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "8")
        | '9' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "9")
        | ')' :: ys, '=' :: stack, state -> loop ys stack state
        | _ :: ys, stack, state -> loop ys stack state
        | [], stack, state -> state //|> int
    loop (Seq.toList str) [] ""

let toLtsStateProc str = 
    let rec loop xs stack (state : string) = 
        match (xs, stack, state) with   
        | '=' :: '=':: ys,stack, state -> loop ys ('=' :: stack) (state)
        | '=' :: ' ':: ys, stack, state -> loop ys ('+' :: stack) state        
        | '0' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "0")
        | '1' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "1")
        | '2' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "2")
        | '3' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "3")
        | '4' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "4")
        | '5' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "5")
        | '6' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "6")
        | '7' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "7")
        | '8' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "8")
        | '9' :: ys, '='::stack, state -> loop ys ('=' :: stack) (state + "9")
        | ')' :: ys, '=' :: stack, state -> loop ys ('+'::stack) state
        | _ :: ys, stack, state -> loop ys stack state
        | [], stack, state -> state //|> int
    loop (Seq.toList str) [] ""


let toMcrl2State str = 
    let rec loop xs stack (state : string) = 
        match (xs, stack, state) with
        | '.' :: ys,  stack, state -> loop ys ('.' :: stack) (state)        
        | '0' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "0")
        | '1' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "1")
        | '2' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "2")
        | '3' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "3")
        | '4' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "4")
        | '5' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "5")
        | '6' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "6")
        | '7' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "7")
        | '8' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "8")
        | '9' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "9")
        | 't' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "t")
        | '_' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state + "_")
        | ' ' :: ys, '.'::stack, state -> loop ys ('.' :: stack) (state)
        | '+' :: ys, '.' :: stack, state -> loop ys stack (state + ",")
        | ';' :: ys, '.' :: stack, state -> loop ys stack state
        | _ :: ys, stack, state -> loop ys stack state
        | [], stack, state -> state //|> int
    loop (Seq.toList str) [] ""

let groupLines (lpspp: list<string>) = 
    let rec loop (lst) =
        match lst with
        | x::y::z :: xs -> if ((toLtsState(x+y+z)) <> "") 
                           then (toLtsState(x+y+z)) :: (loop xs) 
                           else (loop xs)
        | _ :: xs -> []
        | [] -> []
    loop (Seq.toList (dropFirst 3 lpspp))
// groups triples of 3 lines into one line

let groupLinesProc (lpspp: list<string>) = 
    let rec loop (lst) =
        match lst with
        | x::y::z :: xs -> if ((toLtsStateProc(x+y+z)) <> "") 
                           then (toLtsStateProc(x+y+z)) :: (strip " ." y) :: (loop xs) 
                           else (loop xs)
        | _ :: xs -> []
        | [] -> []
    loop (Seq.toList (dropFirst 3 lpspp))


let scanMcrlLines (mcrl: list<string>) =
    let rec loop (lst) =
        match lst with
        | x::xs -> if ((toMcrl2State x) <> "") 
                   then (((toMcrl2State x).Split ',') |> Array.toList) :: (loop xs) 
                   else (loop xs)
        | [] -> []
    loop (Seq.toList (dropFirst 6 mcrl))
  
 
let getSummandGroups (mcrl: list<string>) =
    let rec loop (lst) =
        match (lst: list<string>) with
        | x::xs -> (List.map splitStringLeftOfDot ((strip " ;" x).Split('+') |> Array.toList)) :: (loop xs)
        | [] -> []
    loop (Seq.toList (dropFirst 5 mcrl))

let getMcrlStates (mcrl: list<list<string>>) =
    let rec loop (lst) =
        match (lst: list<list<string>>) with
        | [x]::y::xs -> if x <> "" then (x :: loop xs) else loop xs
        | [x]::[] -> []
        | _ -> []
    loop mcrl 

let getIndexSummandGroup (st: string) (mcrl:list<list<string>> ) =
    let rec loop (lst) =
        match (lst: list<list<string>>) with
        | [x]::y::xs -> if x <> st 
                          then (List.length y) + (loop xs)
                          else 0
        | [x]::[] -> 0
        | _ -> 0
    loop mcrl
                             

let toState str = 
    let rec loop xs stack (state : string) = 
        match (xs, stack, state) with
        | '(' :: ys,  stack, state -> loop ys ('(' :: stack) (state)
        | '0' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "0")
        | '1' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "1")
        | '2' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "2")
        | '3' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "3")
        | '4' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "4")
        | '5' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "5")
        | '6' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "6")
        | '7' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "7")
        | '8' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "8")
        | '9' :: ys, '('::stack, state -> loop ys ('(' :: stack) (state + "9")
        | ')' :: ys, '(' :: stack, state -> loop ys stack state
        | _ :: ys, stack, state -> loop ys stack state
        | [], stack, state -> state |> int
    loop (Seq.toList str) [] ""

let toClass str =
    let rec loop xs flag (cls : string) =
        match (xs, flag, cls) with
        | '0' :: ys, true, cls -> loop ys true (cls + "0")
        | '1' :: ys, true, cls -> loop ys true (cls + "1")
        | '2' :: ys, true, cls -> loop ys true (cls + "2")
        | '3' :: ys, true, cls -> loop ys true (cls + "3")
        | '4' :: ys, true, cls -> loop ys true (cls + "4")
        | '5' :: ys, true, cls -> loop ys true (cls + "5")
        | '6' :: ys, true, cls -> loop ys true (cls + "6")
        | '7' :: ys, true, cls -> loop ys true (cls + "7")
        | '8' :: ys, true, cls -> loop ys true (cls + "8")
        | '9' :: ys, true, cls -> loop ys true (cls + "9")
        | ':' :: ys, true, cls -> loop ys false cls
        | _ :: ys, false, cls -> loop ys false cls
        | [], _ , cls -> cls |> int
        | _, true, _ -> failwith "Classes not empty initially"
    loop (Seq.toList str) true ""

let getStatesOnly ltsinfo =
    (dropFirst 7 ltsinfo) |> List.map(toState)

let getClassesOnly ltsinfo =
    (dropFirst 7 ltsinfo)  |> List.map(toClass)

let getNumberOfClasses ltsinfo =
    String.Concat(Array.ofList(List.filter isDigit (Seq.toList ((dropFirst 3 ltsinfo).[0])))) |> int

let createAtomsList (n:int) (cls : list<int>) (slmin: list<int>) (co : list<int>) (res: list<bool>) =
    let rec loop (nr:int) xs ys (rs:list<bool>) =
        if (xs = [] || ys = []) then rs
            else if (xs.Head = nr) 
                 then loop nr (xs.Tail) (ys.Tail) (replace true (getIndex (ys.Head) co) rs) 
                 else loop nr xs.Tail ys.Tail rs
    loop n (cls) (slmin) (res)


let mcrlLtsMapping mcrlSL (mcrl: list<int>) mcrlProc (lps: list<int>) (lpsProc: list<string>) =
    let vals = [for i in [1..(List.length mcrlSL)] -> -1]
    let rec loop (cells: list<string>) vs =
        match (cells) with
        | x :: xs -> if x = "t1_0"
                     then // In this case of t1_0 the value of idxt is 0
                          let idxProc = List.findIndex (fun e -> e = [x]) mcrlProc
                          // The LTS label of the initial mcrl spec t1_0 is always "1" (assumption)
                          let vs1 = replace 1 0 vs
                          printfn "vs1: %A" vs1
                          printfn "vs: %A" vs
                          // Replace -1 labels by actual LTS state labels in vs-list
                          // such that the element with index y in list (index corresponding to t1_y) 
                          // gets the corresponding LTS state number
                          let rec loop1 (i:int) (vls: list<int>) =
                              if (i>(-1)) 
                              then 
                                   //loop1 (i-1) (replace lps.[val_mc+i] (mcrl.[idxt+i]) vls)
                                   loop1 (i-1) (replace lps.[i] (mcrl.[i]) vls)
                              else vls
                          loop xs (loop1 (List.length mcrlProc.[idxProc+1]) vs1)   
                     else   // When x is not initial mcrl2 process label "t1_0'
                            printfn "mcrl state %A" x 
                            // Get the y in t1_y as an integer
                            let idxt = (splitStringRightOfUnderscore x) |> int
                            // Index of element in mcrl2 specification t1_idtx
                            printfn "idxt: %d" idxt
                            // If t1_idxt does not have a corresponding LTS state number yet in vs
                            if vs.[idxt] = -1
                            then // Skip this case and deal with it later (append to end of list)
                                 loop (List.append xs [x]) vs 
                            else // Show corresponding LTS value already collected for t1_idtx in results vs
                                 printfn "vs.idxt: %d" vs.[idxt]
                                 // Find index of t1_idxt in the mrcl processes list
                                 let idxProc = List.findIndex (fun e -> e = [x]) mcrlProc
                                 printfn "idxProc: %d" idxProc
                                 printfn "List length idxProc+1: %d" (List.length mcrlProc.[(idxProc)+1])
                                 // Find the corresponding position index in lpsProc of "vs.idxt"
                                 let idxProcLps = List.findIndex (fun e -> e = string (vs.[idxt])) lpsProc
                                 printfn "idxProcLps: %d" idxProcLps
                                 // Divide this position index by 2 to get position index in the lps state list 
                                 printfn "idxProcLps div 2 %d" (idxProcLps / 2)
                                 // Replace in vs the values for all the summands of t1_idxt
                                 let rec loop2 (i:int) (vls: list<int>) =
                                         if (i>0)
                                         then
                                            let indexMc = getIndexSummandGroup ("t1_" + (string idxt)) mcrlProc
                                            printfn "IndexMc: %d" indexMc
                                            printfn "(mcrl.[indexMc+i-1]): %d" (mcrl.[indexMc+i-1])
                                            printfn "(lps.[(idxProcLps / 2)+i-1]): %d" (lps.[(idxProcLps / 2)+i-1])
                                            loop2 (i-1) (replace (lps.[(idxProcLps / 2)+i-1]) (mcrl.[indexMc+i-1]) vls)
                                         else vls
                                 printfn "vs: %A" vs 
                                 loop xs (loop2 (List.length mcrlProc.[(idxProc)+1]) vs)
        | [] -> vs // Nothing more to do, give final results in vs list
    loop mcrlSL vals 

//[<JsonFSharpConverter>]
// let options =
//     JsonFSharpOptions()
//         .WithUnionAdjacentTag()
//         .WithUnionAllowUnorderedTag()
//         .ToJsonSerializerOptions()
        

type AtomsOut = { eqclass: list<bool>}

    
// The following is for safer loading
// Need to study better how this could work.
// let safeReadStateLabels filePath =
//     try
//         Some(getStatesOnly (loadStateLabels filePath))
//     with
//     | :? System.IO.IOException -> None

// let safeReadStateClassLabels filePath =
//     try
//         Some(getClassesOnly (loadStateLabels filePath))
//     with
//     | :? System.IO.IOException -> None

// Example of json serializer.
// See info: https://github.com/Tarmil/FSharp.SystemTextJson/blob/master/docs/Using.md
//[<JsonFSharpConverter>]
//type Example = { x: string; y: string }

//JsonSerializer.Serialize({ x = "Hello"; y = "world!" })
// --> {"x":"Hello","y":"world!"}