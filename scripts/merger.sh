#!/bin/bash
###################################################################
Help()
	
{
	echo "########################################### - HELP - ##########################################"
	echo "This is script to merge csv files togather into one."
	echo 
	echo "Syntax: ./merger.sh [options] [arguments]"
	echo
	echo "options: for merging"
	echo "-i	Input file location"
	echo "-o	Output files name"
	echo "-n	Create new file"
	echo
	echo "options: for post processing"
	echo "-r	Remove redundent files"
	echo "-c	Converts merged csv to root file"
	echo 
	echo "-h	Display help"
	echo
	echo "################################################################################################"
}


###################################################################
file_read_loc="../htautau_100M"

merged_file_name="./Merged_output.csv"
merged_file_name_root="./Merged_output.root"
merged_cuthist_name="./Merged_cuthist.root"

# loop through all output text files in the current directory and append their content to the merged file

if (( $# == 0 )); then
	echo "Invalid Entry! please evaluate the help by using -h option"
    exit 1
fi

while getopts "o:i:nrch" option;
do
	case $option in

	o)
		avalue="$OPTARG"
		merged_file_name="${avalue}_output.csv"
		merged_file_name_root="${avalue}_output.root"
		merged_cuthist_name="${avalue}_cuthist.root"

	;;
	i)
		file_read_loc="$OPTARG"

	;; 
	n)
		fladn=1
	;;
	r)
		fladr=1
	;;
	c)
		fladc=1
	;;
	h)
		Help
		exit
	;;
	\?)
		echo "Invalid option"
		Help
		exit 1
	;; 


    esac
done



# loop through all output text files in the current directory and append their content to the merged file

if [[ ${fladn} == 1 ]]
then

	echo
	echo "Merged file name is ${merged_file_name}"
	echo "Merged root file name is ${merged_file_name_root}"
	echo "Merged cut hist file name is ${merged_cuthist_name}"
	echo
	touch ${merged_file_name}
	rm ${merged_file_name}
	touch ${merge_file_name}
	
	touch ${merged_cuthist_name}
	rm ${merged_cuthist_name}
	echo  "entry,PRI_lep_pt,PRI_lep_eta,PRI_lep_phi,PRI_lep_charge,PRI_electron_flag,PRI_muon_flag,\
PRI_had_pt,PRI_had_eta,PRI_had_phi,PRI_had_charge,\
PRI_jet_leading_pt,PRI_jet_leading_eta,PRI_jet_leading_phi,PRI_jet_leading_charge,PRI_n_jets,\
PRI_jet_subleading_pt,PRI_jet_subleading_eta,PRI_jet_subleading_phi,PRI_jet_subleading_charge,PRI_jet_all_pt,\
PRI_met,PRI_met_phi,\
Weight,Label,Process_flag" >  ${merged_file_name} ;

fi



for file in ${file_read_loc}*
do	
	if [[ "${file: -4}" == ".csv" ]]
	then
		cat ${file} >>  ${merged_file_name}
		#echo "Merged file ${file} to ${merged_file_name}"
	fi
done

if [[ ${fladr} == 1 ]]
then
	rm ${file_read_loc}*
fi

if [[ ${fladc} == 1 ]]
then
	input_filename="\"${merged_file_name}\""
	output_filename="\"${merged_file_name_root}\""
	root -l -b -q "convert_csv2root.C(${input_filename},${output_filename})"

fi	
