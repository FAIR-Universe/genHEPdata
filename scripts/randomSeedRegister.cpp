#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <algorithm>

// Function to generate a random seed
int generateSeed()
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(1, 4000000);
    return dist(gen);
}

void writeRandomSeedToFile(const std::vector<int> &generateSeedList, const std::string &filename)
{
    std::ofstream file(filename, std::ios::app);
    if (!file)
    {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }

    for (int seed : generateSeedList)
    {
        file << seed << std::endl;
    }
}

// Function to sort a vector
void sortVector(std::vector<int>& vec)
{
    std::sort(vec.begin(), vec.end());
}

// Function to perform binary search on a sorted vector
bool binarySearch(const std::vector<int>& vec, int target)
{
    return std::binary_search(vec.begin(), vec.end(), target);
}

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        std::cerr << "Usage: " << argv[0] << " <seedfilename> <num_of_seeds> <Process> [Label]" << std::endl;
        return 1;
    }
    std::string filename = argv[1];
    int max_seed = std::stoi(argv[2]);
    std::string process = argv[3];

    std::string label = "0";
    if (argc == 5)
    {
        label = argv[4];
    }

    std::string current_file = "/global/cfs/cdirs/m4287/hep/genHEPdata/scripts/";
    int seed;
    std::vector<int> generate_seed_list;
    std::vector<int> used_seed_list;

    std::ifstream file(filename, std::ios::app);
    if (!file)
    {
        std::cerr << "Error opening file: " << filename << std::endl;
        return 1;
    }

    int used_seed;
    while (file >> used_seed)
    {
        used_seed_list.push_back(used_seed);
    }

    std::sort(used_seed_list.begin(), used_seed_list.end());

    int seed_num = 0;
    while (seed_num < max_seed)
    {
        seed = generateSeed();
        bool is_seed_used = std::binary_search(used_seed_list.begin(), used_seed_list.end(), seed);
        if (is_seed_used)
        {
            std::cout << "Seed is already used." << std::endl;
            continue;
        }
        std::cout << "Generated seed: " << seed << std::endl;
        auto seed_str = std::to_string(seed);

        auto command = std::string("sbatch ") + current_file + "run_batch.sh " + seed_str + " " + process + " " + label + " &";

        system(command.c_str());

        generate_seed_list.push_back(seed);
        seed_num++;
    }

    writeRandomSeedToFile(generate_seed_list, filename);

    return 0;
}