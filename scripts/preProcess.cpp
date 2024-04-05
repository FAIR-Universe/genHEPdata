
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

//------------------------------------------------------------------------------

void AnalyseEvents(ExRootTreeReader *treeReader, string outputFile_part, const int label)
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

    TLorentzVector p_jet1;
    TLorentzVector p_jet2;
    TLorentzVector p_jet3;
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
    Double_t deltar_lep_had = 0;
    Double_t deltaeta_jet_jet = 0;
    Double_t prodeta_jet_jet = 0;
    Double_t deltar_lep_jet2 = 0;
    Double_t deltar_lep_jet1 = 0;
    Double_t mass_vis = 0;
    Double_t mass_jet_jet = 0;
    Double_t pt_tot = 0;
    Double_t pt_h = 0;
    Double_t sum_pt = 0;
    Double_t jet_all_pt = 0;
    Double_t pt_ratio_lep_had = 0;

    Double_t mT_lep_had = 0;

    double charge_lep = 0.;
    double pt_lep = 0.;
    double eta_lep = 0.;
    double phi_lep = 0.;

    double charge_had = 0;
    double pt_had = 0.;
    double eta_had = 0.;
    double phi_had = 0.;

    double charge_jet1 = 0;
    double pt_jet1 = 0.;
    double eta_jet1 = 0.;
    double phi_jet1 = 0.;

    double charge_jet2 = 0;
    double pt_jet2 = 0.;
    double eta_jet2 = 0.;
    double phi_jet2 = 0.;

    double charge_jet3 = 0;
    double pt_jet3 = 0.;
    double eta_jet3 = 0.;
    double phi_jet3 = 0.;

    string output_filename;

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

        charge_lep = 0.;
        pt_lep = 0.;
        eta_lep = 0.;
        phi_lep = 0.;
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

        charge_had = 0;
        pt_had = 0.;
        eta_had = 0.;
        phi_had = 0.;
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
        charge_jet1 = 0;
        pt_jet1 = 0.;
        eta_jet1 = 0.;
        phi_jet1 = 0.;

        charge_jet2 = 0.;
        pt_jet2 = 0.;
        eta_jet2 = 0.;
        phi_jet2 = 0.;

        charge_jet3 = 0.;
        pt_jet3 = 0.;
        eta_jet3 = 0.;
        phi_jet3 = 0.;

        for (i = 0; i < branchJet->GetEntriesFast(); ++i)
        {

            jet = (Jet *)branchJet->At(i);
            if (jet->PT < 20.0)
            {
                continue;
            }
            n_jet++;
            jet_all_pt += jet->PT;
            if (jet->PT > pt_jet1)
            {

                pt_jet2 = pt_jet1;
                eta_jet2 = eta_jet1;
                phi_jet2 = phi_jet1;
                charge_jet2 = charge_jet1;
                p_jet2 = p_jet1;

                pt_jet1 = jet->PT;
                eta_jet1 = jet->Eta;
                phi_jet1 = jet->Phi;
                charge_jet1 = jet->Charge;
                p_jet1 = jet->P4();
            }

            else if (jet->PT > pt_jet2)
            {

                pt_jet3 = pt_jet2;
                eta_jet3 = eta_jet2;
                phi_jet3 = phi_jet2;
                charge_jet3 = charge_jet2;
                p_jet3 = p_jet2;

                pt_jet2 = jet->PT;
                eta_jet2 = jet->Eta;
                phi_jet2 = jet->Phi;
                charge_jet2 = jet->Charge;
                p_jet2 = jet->P4();
            }
            else if (jet->PT > pt_jet3)
            {

                pt_jet3 = jet->PT;
                eta_jet3 = jet->Eta;
                phi_jet3 = jet->Phi;
                charge_jet3 = jet->Charge;
                p_jet3 = jet->P4();
            }
        }

        deltar_lep_had = p_had.DeltaR(p_lep);

        // if(deltar_lep_had > 2.5){continue;}

        mT_lep_had = TMath::Sqrt(pow(TMath::Sqrt(pow(p_lep.Px(), 2.0) + pow(p_lep.Py(), 2.0)) + TMath::Sqrt(pow(p_had.Px(), 2.0) + pow(p_had.Py(), 2.0)), 2.0) - pow(((p_lep.Px()) + (p_had.Px())), 2.0) - pow((p_lep.Py()) + (p_had.Py()), 2.0));

        // if (pt_jet1 < 40){continue;}
        h_cutflow->Fill(7);
        if (mT_lep_had > 80)
        {
            continue;
        }
        h_cutflow->Fill(8);
        process_flag = event->ProcessID;
        cross_section = event->CrossSection;
        Weight = luminosity * cross_section;
        mass_vis = TMath::Sqrt(2 * (pt_lep * pt_had) * cosh((eta_lep - eta_had) - cos(phi_lep - phi_had)));
        sum_pt = 0;
        jet_all_pt = 0;

        if (n_jet > 1)
        {
            mass_jet_jet = TMath::Sqrt(2 * (pt_jet1 * pt_jet2) * cosh((eta_jet1 - eta_jet2) - cos(phi_jet1 - phi_jet2)));
            deltaeta_jet_jet = TMath::Abs(eta_jet1 - eta_jet2);
            prodeta_jet_jet = eta_jet1 * eta_jet2;
            p_tot = p_jet1 + p_jet2 + p_lep + p_had;
            pt_tot = p_tot.Mag();
            pt_h = pt_lep + pt_had + pt_jet1 + pt_jet2;
            sum_pt = TMath::Abs(pt_had) + TMath::Abs(pt_lep) + TMath::Abs(pt_jet1) + TMath::Abs(pt_jet2) + TMath::Abs(pt_jet3);
            jet_all_pt = pt_jet1 + pt_jet2 + pt_jet3;
        }

        else
        {
            pt_jet2 = -7;
            phi_jet2 = -7;
            eta_jet2 = -7;
            charge_jet2 = -7;
            mass_jet_jet = -7;
            deltaeta_jet_jet = -7;
            prodeta_jet_jet = -7;
            p_tot = p_jet1 + p_lep + p_had;
            pt_tot = p_tot.Mag();
            pt_h = pt_lep + pt_had + pt_jet1;
        }

        myfile_part << entry << ",";
        myfile_part << pt_lep << "," << eta_lep << "," << phi_lep << "," << charge_lep << "," << flag_el << "," << flag_mu << ",";
        myfile_part << pt_had << "," << eta_had << "," << phi_had << "," << charge_had << ",";
        myfile_part << pt_jet1 << "," << eta_jet1 << "," << phi_jet1 << "," << charge_jet1 << "," << n_jet << ",";
        myfile_part << pt_jet2 << "," << eta_jet2 << "," << phi_jet2 << "," << charge_jet2 << "," << jet_all_pt << ",";
        myfile_part << missingET->MET << "," << missingET->Phi << ",";

        myfile_part << mT_lep_had << "," << mass_vis << "," << pt_h << "," << deltaeta_jet_jet << "," << mass_jet_jet << "," << prodeta_jet_jet << "," << deltar_lep_had << "," << pt_tot << "," << sum_pt << "," << pt_ratio_lep_had << ",";

        myfile_part << Weight << "," << label << "," << process_flag << std::endl;
    }
    outfile->Write();
    outfile->Close();
}
//------------------------------------------------------------------------------

void preProcess(const char *inputFile, string outputFile_part, const int label)
{

    gSystem->Load("libDelphes");

    TChain *chain = new TChain("Delphes");
    chain->Add(inputFile);

    ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
    ExRootResult *result = new ExRootResult();

    AnalyseEvents(treeReader, outputFile_part, label);

    cout << "** Exiting..." << endl;

    delete result;
    delete treeReader;
    delete chain;
}
