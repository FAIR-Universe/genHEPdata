
# Variables
CXX = g++
CXXFLAGS = -Wall -g 
SRCS = randomSeedRegister.cpp 
TARGET_DIR = ../bin
TARGETS = $(SRCS:.cpp=)
BIN_TARGETS = $(addprefix $(TARGET_DIR)/, $(TARGETS))

# Default rule to build all targets
all: $(TARGET_DIR) $(BIN_TARGETS)

# Rule to build each target separately
$(TARGET_DIR)/%: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

# Ensure the target directory exists
$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

# Clean rule to remove all executables and object files
clean:
	rm -f $(BIN_TARGETS) *.o

# Phony targets to avoid conflicts with files named "all", "clean", or the target directory name
.PHONY: all clean $(TARGET_DIR)
