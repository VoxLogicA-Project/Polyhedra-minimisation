// For more information see https://aka.ms/fsharp-console-apps

// Mieke Massink
// Date: 2024/02/01
// Code to produce PolyLogicA results in the Atoms.json style for each
// equivalence class obtained from .lts minimisation via the mcrl2 toolset
// of an LTS encoding of a polyhedral model.

// This operation takes two files as input (later three) and produces
// a single .json file in the Atoms.json format with one result per equivalence
// class

// The four input files are the following text files:
// 1) Output of ltsinf -l name.lts of the full .lts produced by mcrl2 operators
//    from the .mcrl2 encoding. This is a .txt file.
// 2) Output of the ltsinfo -l name_minimised.lts of the minimised .lts. This is
//    also a .txt file.
// 3) Output of lpspp (without summand numbers) on name.lps of the full .mcrl2 file produced by the eta-encoder
//    with the following parameters for mcrl22lps:
//    mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm {input_file} {base_name}.lps
//    from the .mcrl2 encoding. This is a .txt file. (e.g. triangleRBModel_Poset.txt)
// 4) The original .mcrl2 specification in mcrl2 language of the poset (e.g. triangleRBModel_Poset.mcrl2)
//    i.e. the .mcrl2 input file for the encoding.

// Example for the blue triangle:
// >dotnet run ltsinfo_full.txt ltsinfo_minimised.txt triangleRBModel_Poset.txt triangleRBModel_Poset.mcrl2
//
// (Of course, dotnet above runs in the directory of the F# source code, and the paths to the various files
//  above have been omitted)
//
// Note that in the cod below the .json results for each equivalence class are still produced with printfn instead
// of generating separate Json files. Still to be done.

module ClassAtoms.Main

open StateLabels
open System.Text.Json
open System.Text.Json.Serialization

[<EntryPoint>]
let main (argv : string array) =
        printfn "Start loading state-label file of full lts model ..."
        let stateLabelsInput = getStatesOnly(loadFile argv[0])
        printfn "State labels full: %A" stateLabelsInput 
        printfn "Start loading state-class-label file of minimised lts model ..."
        let inputMinimised = (loadFile argv[1])
        printfn "Start loading lpspp text file of full lts model ..."
        let lpsppStates = (loadFile argv[2])
        let (lpsStates:list<int>) = (groupLines lpsppStates) |> List.map System.Int32.Parse
        printfn "lpspp state numbers appearing in summands: %A" lpsStates
        let (lpsStatesProc:list<string>) = (groupLinesProc lpsppStates) //|> List.map System.Int32.Parse
        printfn "lpsppProc process states and summand atomic propositions: %A" lpsStatesProc
        printfn "Start loading mcrl2-spec summand state numbers in order of appearing in summands ..."
        let mcrl2States =  (loadFile argv[3])
        let (mcStates:list<int>) = List.map (fun (x:string) -> (x.[3..] |> int)) (List.concat (scanMcrlLines mcrl2States))
        printfn "mcrl2-spec summand state numbers: %A" mcStates
        let mcSummands = getSummandGroups mcrl2States
        printfn "mcrl2-spec states and summands: %A" mcSummands
        let mcrlStateLabels = (getMcrlStates (getSummandGroups mcrl2States))
        // List of integers mapping cell index y (of t1_y) to LTS state number
        let cellStateMap = mcrlLtsMapping mcrlStateLabels  mcStates mcSummands lpsStates lpsStatesProc
        //let cellStateMap = mcrlLtsMappingTest mcrlStateLabels  mcStates mcSummands lpsStates lpsStatesProc
        printfn "Map mcrl2 cells to LTS states: %A" cellStateMap
        let stateLabelsMinimised = getStatesOnly (inputMinimised)
        printfn "State labels minimised: %A" stateLabelsMinimised
        let stateClassLabelsInput = getClassesOnly (inputMinimised)
        printfn "Class labels minimised: %A" stateClassLabelsInput
        printfn "Number of classes: %A" (getNumberOfClasses inputMinimised)
        printfn "All four files loaded, produce Atom file for each equivalence class ..."
        // resultInit is initial list of Atoms initially set to false. For each eq. class C the for-loop
        // below produces an Atoms list where the position corrisponding to the cell that
        // is part of class C is set to true. All others remaining false.
        // For now the Json Atoms list is shown on standard output. Still need to
        // produce them as .json file(s).
        let resultInit = [for i in [1..(List.length mcrlStateLabels) ] -> false]
        for i in [0..((getNumberOfClasses inputMinimised)-1)] do
                let result = createAtomsList i stateClassLabelsInput stateLabelsMinimised cellStateMap resultInit
                //printfn "%s" <| Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented)
                printfn "Class %i: %A" i result
                //let test = JsonSerializer.Serialize({ eqclass = result},options)
                let test = JsonSerializer.Serialize({ eqclass = result})
                printfn "Test: %s" <| test
        0


