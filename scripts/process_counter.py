
import json


def process_counter(output_file_name):
    import ROOT

    f = ROOT.TFile(output_file_name + ".root")
    process_hist = f.Get("process_ID")
    
    process_dict = {}
    for i in range(1000):
        if process_hist.GetBinContent(i+1) > 0:
            print("Process ID: ", i)
            print(process_hist.GetBinContent(i+1))
            process_dict[i] = process_hist.GetBinContent(i+1)

        
    with open(output_file_name + ".json", "w") as f:
        json.dump(process_dict, f)
        

    
if __name__ == "__main__":
    import sys
    process_counter(sys.argv[1])
    