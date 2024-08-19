
/*
This macro shows how to compute jet energy scale.
root -l examples/Example4.C'("delphes_output.root", "plots.root")'
*/

#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes)
#include "classes/DelphesClasses.h"
#include "ExRootAnalysis/ExRootTreeReader.h"
#include "ExRootAnalysis/ExRootResult.h"
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

    Int_t i, j, n_jet;
    Int_t process_flag;
    Int_t flag_el = 0;
    Int_t flag_mu = 0;
    Int_t flag_had = 0;

    std::string output_filename;

    output_filename = outputFile_part + "_cuthist.root";

    TFile *outfile = new TFile(output_filename.c_str(), "RECREATE");
    TH1 *h_cutflow = new TH1F("cutflow", "Cut flow histogram", 10, 0.0, 10.0);
    TH1 *process_ID = new TH1F("process_ID", "Process ID", 1000, 0.0, 1000.0);

    outputFile_part = outputFile_part + ".csv";
    myfile_part.open(outputFile_part);

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

        double charge_lep = 0.;
        double pt_lep = 0.;
        double eta_lep = 0.;
        double phi_lep = 0.;
        flag_el = 0;
        for (i = 0; i < branchElectron->GetEntriesFast(); ++i)
        {
            electron = (Electron *)branchElectron->At(i);
            if (electron->PT > 15)
            {
                pt_lep = electron->PT;
                eta_lep = electron->Eta;
                phi_lep = electron->Phi;
                charge_lep = electron->Charge;
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
                pt_lep = muon->PT;
                eta_lep = muon->Eta;
                phi_lep = muon->Phi;
                charge_lep = muon->Charge;
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

        if (pt_lep < 20)
        {
            continue;
        }
        h_cutflow->Fill(3);

        double charge_had = 0;
        double pt_had = 0.;
        double eta_had = 0.;
        double phi_had = 0.;
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
                charge_had = jet->Charge;
                pt_had = jet->PT;
                eta_had = jet->Eta;
                phi_had = jet->Phi;
                p_had = jet->P4();
                flag_had++;
            }
        }
        if (flag_had != 1)
        {
            continue;
        }
        h_cutflow->Fill(4);
        if ((charge_had + charge_lep) != 0)
        {
            continue;
        }
        h_cutflow->Fill(5);
        if (pt_had < 20)
        {
            continue;
        }
        h_cutflow->Fill(6);

        n_jet = 0;

        std::array<double, 2> pt_jet = {-7.0, -7.0};
        std::array<double, 2> eta_jet = {-7.0, -7.0};
        std::array<double, 2> phi_jet = {-7.0, -7.0};
        std::array<double, 2> charge_jet = {-7.0, -7.0};
        std::array<TLorentzVector, 2> p_jet;

        int i_leading_jet = -1;
        int i_subleading_jet = -1;
        double pt_leading_jet = -7;
        double pt_subleading_jet = -7;
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
            n_jet++;
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
            pt_jet[0] = jet->PT;
            eta_jet[0] = jet->Eta;
            phi_jet[0] = jet->Phi;
            charge_jet[0] = jet->Charge;
            p_jet[0] = jet->P4();
        }
        if (i_subleading_jet >= 0)
        {
            
            auto jet = (Jet *)branchJet->At(i_subleading_jet);
            pt_jet[1] = jet->PT;
            eta_jet[1] = jet->Eta;
            phi_jet[1] = jet->Phi;
            charge_jet[1] = jet->Charge;
            p_jet[1] = jet->P4();
        }
        if (n_jet < 2)
        {
            pt_jet[1] = eta_jet[1] = phi_jet[1] = charge_jet[1] = -7;
        }

        process_flag = event->ProcessID;
        Weight = 1;

        myfile_part << entry << ",";
        myfile_part << pt_lep << "," << eta_lep << "," << phi_lep << "," << charge_lep << "," << flag_el << "," << flag_mu << ",";
        myfile_part << pt_had << "," << eta_had << "," << phi_had << "," << charge_had << ",";
        myfile_part << pt_jet[0] << "," << eta_jet[0] << "," << phi_jet[0] << "," << charge_jet[0] << ",";
        myfile_part << pt_jet[1] << "," << eta_jet[1] << "," << phi_jet[1] << "," << charge_jet[1] << ",";

        myfile_part << n_jet << "," << jet_all_pt << ",";
        myfile_part << missingET->MET << "," << missingET->Phi << ",";

        myfile_part << Weight << "," << label << "," << process_flag << std::endl;
    }
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
