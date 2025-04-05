
/*
This macro shows how to compute jet energy scale.
root -l examples/Example4.C'("delphes_output.root", "plots.root")'
*/

#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes)
#include "classes/DelphesClasses.h"
#include "ExRootTreeReader.h"
#include "ExRootResult.h"
#else
class ExRootTreeReader;
class ExRootResult;
#endif

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>

//------------------------------------------------------------------------------

void AnalyseEvents(ExRootTreeReader *treeReader, std::string outputFile_part, const int label)
{

    TClonesArray *branchElectron = treeReader->UseBranch("Electron");
    TClonesArray *branchMuon = treeReader->UseBranch("Muon");
    TClonesArray *branchEvent = treeReader->UseBranch("Event");
    TClonesArray *branchJet = treeReader->UseBranch("Jet");
    TClonesArray *branchMissingET = treeReader->UseBranch("MissingET");

    Long64_t allEntries = treeReader->GetEntries();
    ofstream myfile_det;
    ofstream myfile_part;

    Jet *jet;
    Electron *electron;
    Muon *muon;
    MissingET *missingET;

    TLorentzVector p_lep;
    TLorentzVector p_had;
    TLorentzVector p_tot;
    double Weight = 1.;
    double cross_section = 1.;
    double luminosity = 139; // fb-1
    Long64_t entry;

    Int_t i, j, PRI_n_jets;
    Int_t flag_el = 0;
    Int_t flag_mu = 0;
    Int_t flag_had = 0;

    std::string output_filename;

    TFile *outfile = new TFile(output_filename.c_str(), "RECREATE");
    TH1 *h_cutflow = new TH1F("cutflow", "Cut flow histogram", 10, 0.0, 10.0);
    TH1 *process_ID = new TH1F("process_ID", "Process ID", 1000, 0.0, 1000.0);
    // Create a TTree (more flexible than TNtuple for complex data)
    TTree *tree = new TTree("physics", "Physics Event Data");
    
    // Define variables for all columns
    Int_t entry;
    Float_t PRI_lep_pt, PRI_lep_eta, PRI_lep_phi;
    Int_t PRI_lep_charge;
    Bool_t PRI_electron_flag, PRI_muon_flag;
    Float_t PRI_had_pt, PRI_had_eta, PRI_had_phi;
    Int_t PRI_had_charge;
    Float_t PRI_jet_leading_pt, PRI_jet_leading_eta, PRI_jet_leading_phi;
    Int_t PRI_jet_leading_charge;
    Float_t PRI_jet_subleading_pt, PRI_jet_subleading_eta, PRI_jet_subleading_phi;
    Int_t PRI_jet_subleading_charge;
    Int_t PRI_n_jets;
    Float_t PRI_jet_all_pt;
    Float_t PRI_met, PRI_met_phi;
    Float_t Weight;
    Int_t Label;
    Int_t Process_flag;
    
    // Create branches for all variables
    tree->Branch("entry", &entry, "entry/I");
    tree->Branch("PRI_lep_pt", &PRI_lep_pt, "PRI_lep_pt/F");
    tree->Branch("PRI_lep_eta", &PRI_lep_eta, "PRI_lep_eta/F");
    tree->Branch("PRI_lep_phi", &PRI_lep_phi, "PRI_lep_phi/F");
    tree->Branch("PRI_lep_charge", &PRI_lep_charge, "PRI_lep_charge/I");
    tree->Branch("PRI_electron_flag", &PRI_electron_flag, "PRI_electron_flag/O");
    tree->Branch("PRI_muon_flag", &PRI_muon_flag, "PRI_muon_flag/O");
    tree->Branch("PRI_had_pt", &PRI_had_pt, "PRI_had_pt/F");
    tree->Branch("PRI_had_eta", &PRI_had_eta, "PRI_had_eta/F");
    tree->Branch("PRI_had_phi", &PRI_had_phi, "PRI_had_phi/F");
    tree->Branch("PRI_had_charge", &PRI_had_charge, "PRI_had_charge/I");
    tree->Branch("PRI_jet_leading_pt", &PRI_jet_leading_pt, "PRI_jet_leading_pt/F");
    tree->Branch("PRI_jet_leading_eta", &PRI_jet_leading_eta, "PRI_jet_leading_eta/F");
    tree->Branch("PRI_jet_leading_phi", &PRI_jet_leading_phi, "PRI_jet_leading_phi/F");
    tree->Branch("PRI_jet_leading_charge", &PRI_jet_leading_charge, "PRI_jet_leading_charge/I");
    tree->Branch("PRI_jet_subleading_pt", &PRI_jet_subleading_pt, "PRI_jet_subleading_pt/F");
    tree->Branch("PRI_jet_subleading_eta", &PRI_jet_subleading_eta, "PRI_jet_subleading_eta/F");
    tree->Branch("PRI_jet_subleading_phi", &PRI_jet_subleading_phi, "PRI_jet_subleading_phi/F");
    tree->Branch("PRI_jet_subleading_charge", &PRI_jet_subleading_charge, "PRI_jet_subleading_charge/I");
    tree->Branch("PRI_n_jets", &PRI_n_jets, "PRI_n_jets/I");
    tree->Branch("PRI_jet_all_pt", &PRI_jet_all_pt, "PRI_jet_all_pt/F");
    tree->Branch("PRI_met", &PRI_met, "PRI_met/F");
    tree->Branch("PRI_met_phi", &PRI_met_phi, "PRI_met_phi/F");
    tree->Branch("Weight", &Weight, "Weight/F");
    tree->Branch("Label", &Label, "Label/I");
    tree->Branch("Process_flag", &Process_flag, "Process_flag/I");

    outputFile_part = outputFile_part + ".csv";

    // Loop over all events
    for (entry = 0; entry < allEntries; ++entry)
    {

        // if (entry > 10000) break;
        //  Load selected branches with data from specified event
        treeReader->ReadEntry(entry);
        HepMCEvent *event = (HepMCEvent *)branchEvent->At(0);
        // std::cout << "weight : " << event->Weight << std::endl;

        h_cutflow->Fill(0);
        process_ID->Fill(event->ProcessID);

        missingET = (MissingET *)branchMissingET->At(0);
        // if(missingET->MET < 20){continue;}
        h_cutflow->Fill(1);

        flag_el = 0;
        for (i = 0; i < branchElectron->GetEntriesFast(); ++i)
        {
            electron = (Electron *)branchElectron->At(i);
            if (electron->PT > 15)
            {
                PRI_lep_pt = electron->PT;
                PRI_lep_eta = electron->Eta;
                PRI_lep_eta = electron->Phi;
                PRI_lep_charge = electron->Charge;
                p_lep = electron->P4();
                flag_el++;
            }
        }

        flag_mu = 0;
        for (j = 0; j < branchMuon->GetEntriesFast(); ++j)
        {
            muon = (Muon *)branchMuon->At(j);
            if (muon->PT > 15)
            {
                PRI_lep_pt = muon->PT;
                PRI_lep_eta = muon->Eta;
                PRI_lep_eta = muon->Phi;
                PRI_lep_charge = muon->Charge;
                p_lep = muon->P4();
                flag_mu++;
            }
        }
        if ((flag_el > 1) || (flag_mu > 1))
        {
            continue;
        }

        if (flag_mu == flag_el)
        {
            continue;
        }
        h_cutflow->Fill(2);

        if (PRI_lep_pt < 20)
        {
            continue;
        }
        h_cutflow->Fill(3);

        flag_had = 0;

        for (i = 0; i < branchJet->GetEntriesFast(); ++i)
        {

            jet = (Jet *)branchJet->At(i);
            if (jet->PT < 20)
            {
                continue;
            }
            if (jet->TauTag == 1)
            {
                PRI_had_charge = jet->Charge;
                PRI_had_pt = jet->PT;
                PRI_had_eta = jet->Eta;
                PRI_had_phi = jet->Phi;
                p_had = jet->P4();
                flag_had++;
            }
        }
        if (flag_had != 1)
        {
            continue;
        }
        h_cutflow->Fill(4);
        if ((PRI_had_charge + PRI_lep_charge) != 0)
        {
            continue;
        }
        h_cutflow->Fill(5);
        if (PRI_had_pt < 20)
        {
            continue;
        }
        h_cutflow->Fill(6);

        PRI_n_jets = 0;

        int i_leading_jet = -1;
        int i_subleading_jet = -1;
        double pt_leading_jet = -25;
        double pt_subleading_jet = -25;
        double jet_all_pt = 0;

        for (i = 0; i < branchJet->GetEntriesFast(); ++i)
        {
            auto jet = (Jet *)branchJet->At(i);
            if (!jet) {
                std::cerr << "Error: Jet is null at index " << i << std::endl;
                continue;
            }
            double ptj = jet->PT;
            if (ptj < 20.0)
            {
                continue;
            }
            if (jet->TauTag == 1)
            {
                continue;
            }
            PRI_n_jets++;
            jet_all_pt += ptj;

            if (ptj > pt_leading_jet)
            {
                i_subleading_jet = i_leading_jet;
                pt_subleading_jet = pt_leading_jet;
                i_leading_jet = i;
                pt_leading_jet = ptj;
            }
            else if (ptj > pt_subleading_jet)
            {
                i_subleading_jet = i;
                pt_subleading_jet = ptj;
            }
        }

        if (i_leading_jet >= 0)
        {   
            auto jet = (Jet *)branchJet->At(i_leading_jet);
            PRI_jet_leading_pt = jet->PT;
            PRI_jet_leading_eta = jet->Eta;
            PRI_jet_leading_phi = jet->Phi;
            PRI_jet_leading_charge = jet->Charge;
        }
        if (i_subleading_jet >= 0)
        {
            
            auto jet = (Jet *)branchJet->At(i_subleading_jet);
            PRI_jet_subleading_pt = jet->PT;
            PRI_jet_subleading_eta = jet->Eta;
            PRI_jet_subleading_phi = jet->Phi;
            PRI_jet_subleading_charge = jet->Charge;
        }
        if (PRI_n_jets < 2)
        {
            PRI_jet_subleading_pt = PRI_jet_subleading_eta = PRI_jet_subleading_phi = PRI_jet_subleading_charge = -25;
        }

        Process_flag = event->ProcessID;
        Weight = 1;

        tree->Fill();
    }
    
    // Write and close
    tree->Write();
    outfile->Write();
    outfile->Close();
}
//------------------------------------------------------------------------------

void preProcess(const char *inputFile, std::string outputFile_part, const int label)
{

    gSystem->Load("libDelphes");

    TChain *chain = new TChain("Delphes");
    chain->Add(inputFile);

    ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
    ExRootResult *result = new ExRootResult();

    AnalyseEvents(treeReader, outputFile_part, label);

    std::cout << "** Exiting..." << std::endl;

    delete result;
    delete treeReader;
    delete chain;
}
