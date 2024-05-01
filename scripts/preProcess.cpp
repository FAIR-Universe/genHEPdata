
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

    output_filename = outputFile_part + "_cuthist_" + ".root";

    TFile *outfile = new TFile(output_filename.c_str(), "RECREATE");
    TH1 *h_cutflow = new TH1F("cutflow", "Cut flow histogram", 10, 0.0, 10.0);

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

        std::array<double, 3> charge_jet = {0.0, 0.0, 0.0};
        std::array<double, 3> pt_jet = {0.0, 0.0, 0.0};
        std::array<double, 3> eta_jet = {0.0, 0.0, 0.0};
        std::array<double, 3> phi_jet = {0.0, 0.0, 0.0};
        std::array<TLorentzVector, 3> p_jet;

        double jet_all_pt = 0;
        for (i = 0; i < branchJet->GetEntriesFast(); ++i)
        {
            auto jet = (Jet *)branchJet->At(i);
            if (jet->PT < 20.0)
            {
            continue;
            }
            n_jet++;
            jet_all_pt += jet->PT;

            for (int j = 0; j < 3; j++)
            {
            if (jet->PT > pt_jet[j])
            {
                for (int k = 2; k > j; k--)
                {
                pt_jet[k] = pt_jet[k - 1];
                eta_jet[k] = eta_jet[k - 1];
                phi_jet[k] = phi_jet[k - 1];
                charge_jet[k] = charge_jet[k - 1];
                p_jet[k] = p_jet[k - 1];
                }

                pt_jet[j] = jet->PT;
                eta_jet[j] = jet->Eta;
                phi_jet[j] = jet->Phi;
                charge_jet[j] = jet->Charge;
                p_jet[j] = jet->P4();
                break;
            }
            }
        }

        process_flag = event->ProcessID;
        cross_section = event->CrossSection;
        Weight = luminosity * cross_section;

        myfile_part << entry << ",";
        myfile_part << pt_lep << "," << eta_lep << "," << phi_lep << "," << charge_lep << "," << flag_el << "," << flag_mu << ",";
        myfile_part << pt_had << "," << eta_had << "," << phi_had << "," << charge_had << ",";
        for (int j = 0; j < 3; j++)
        {
            myfile_part << pt_jet[j] << "," << eta_jet[j] << "," << phi_jet[j] << "," << charge_jet[j] << ",";
        }
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
