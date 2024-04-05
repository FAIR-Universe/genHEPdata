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
    std::uniform_int_distribution<int> dist(1, 100000000);
    return dist(gen);
}

// Function to check if a seed is in the used seeds file
bool isSeedUsed(int seed, const std::string &filename)
{
    std::ifstream file(filename);
    if (!file)
    {
        std::cerr << "Error opening file: " << filename << std::endl;
        return false;
    }

    int usedSeed;
    while (file >> usedSeed)
    {
        if (usedSeed == seed)
        {
            return true;
        }
    }

    return false;
}

void writeRamdomSeedToFile(const std::vector<int> &generateSeedList, const std::string &filename)
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

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        std::cerr << "Usage: " << argv[0] << " <seedfilename> <num_of_seeds> <Process> [Label]" << std::endl;
        return 1;
    }
    std::string filename = argv[1];
    int max_seed = std::stoi(argv[2]);
    std::string Process = argv[3];

    std::string Label = "0";
    if (argc == 5)
    {
        Label = argv[4];
    }

    std::string current_file = "/global/cfs/cdirs/m4287/hep/genHEPdata/scripts/";
    int seed;
    std::vector<int> generateSeedList;

    int seed_num = 0;
    while (seed_num < max_seed)
    {
        seed = generateSeed();
        if (isSeedUsed(seed, filename))
        {
            std::cout << "Seed is already used." << std::endl;
            continue;
        }
        std::cout << "Generated seed: " << seed << std::endl;
        auto seed_str = std::to_string(seed);

        auto command = std::string("sbatch ") + current_file + "run_batch.sh " + seed_str + " " + Process + " " + Label;

        system(command.c_str());

        generateSeedList.push_back(seed);
        seed_num++;
    }

    writeRamdomSeedToFile(generateSeedList, filename);

    return 0;
}