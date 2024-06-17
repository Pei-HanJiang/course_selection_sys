#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

// TreeNode class to store course ID (string) and corresponding filename
class TreeNode {
public:
    std::string key;  
    std::string file;
    TreeNode* left;
    TreeNode* right;

    TreeNode(const std::string& k, const std::string& f) : key(k), file(f), left(nullptr), right(nullptr) {}
};

// Binary Search Tree class
class BinarySearchTree {
private:
    TreeNode* root;

    TreeNode* insert(TreeNode* node, const std::string& key, const std::string& file) {
        if (node == nullptr) {
            return new TreeNode(key, file);
        }
        if (key == node->key) {
            node->file = file;  // Update file if key already exists
        } else if (key < node->key) {
            node->left = insert(node->left, key, file);
        } else {
            node->right = insert(node->right, key, file);
        }
        return node;
    }

    TreeNode* search(TreeNode* node, const std::string& key) const {
        if (node == nullptr || node->key == key) {
            return node;
        }
        if (key < node->key) {
            return search(node->left, key);
        }
        return search(node->right, key);
    }

public:
    BinarySearchTree() : root(nullptr) {}

    void insert(const std::string& key, const std::string& file) {
        root = insert(root, key, file);
    }

    TreeNode* search(const std::string& key) const {
        return search(root, key);
    }
};

// Function to parse each file and insert course IDs into the BST
void parseFile(const std::string& filePath, BinarySearchTree& bst) {
    std::ifstream file(filePath);
    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string part;
        std::string courseId;

        if (std::getline(ss, part, ':')) {
            courseId = part;
            bst.insert(courseId, filePath);
        }
    }
}

// Function to build the tree by parsing all files in the directory
void buildTree(const std::string& directory, BinarySearchTree& bst) {
    for (int i = 1; i <= 354; ++i) {
        std::string givenfile = std::to_string(i) + ".txt";
        std::string filepath = directory + "/" + givenfile;
        parseFile(filepath, bst);
    }
}

std::vector<std::string> Students;
int SearchSPair(const std::string givenfile, const std::string target_course_id)
{
    std::string filepath = "data/" + givenfile;
    std::ifstream file(filepath);
    if (!file)
    {
        std::cerr << "Error opening file: " << filepath << std::endl;
    }

    std::string line;
    getline(file, line);
    int amount = 0;
    while (getline(file, line))
    {
        std::istringstream ss(line);
        std::string student_id, course_id;
        getline(ss, student_id, ',');
        getline(ss, course_id, ',');
        course_id.erase(course_id.find_last_not_of(" \n\r\t") + 1);

        // Check if the first field (student_id) matches the target student ID
        if (course_id == target_course_id)
        {
            // print student_id
            // std::cout << student_id << std::endl;
            Students.push_back(student_id);
            amount++;
        }
    }

    file.close();
    return amount;
}

// Function to track and read out all numbers associated with a course ID
void trackAndReadNumbers(const BinarySearchTree& bst, const std::string& courseId) {
    TreeNode* resultNode = bst.search(courseId);
    if (resultNode) {
        std::cout << "Course ID " << courseId << " found in file: " << resultNode->file << std::endl;

        // Read and print the numbers associated with the course ID from the file
        std::ifstream infile(resultNode->file);
        std::string line;
        while (std::getline(infile, line)) {
            // Check if the line contains the course ID followed by ":"
            std::size_t pos = line.find(courseId + ":");
            if (pos != std::string::npos) {
                // Move past the course ID and ":"
                pos += courseId.length() + 1;

                // Extract numbers after the course ID and print each one
                std::istringstream ss(line.substr(pos));
                std::string number;
                while (ss >> number) {
                    // std::cout << number << std::endl;
                    SearchSPair(number, courseId);
                }
            }
        }
    } else {
        std::cout << "Course ID " << courseId << " not found" << std::endl;
    }
}



int main() {
    std::string directory = "course_index"; 
    BinarySearchTree bst;
    buildTree(directory, bst);

    // Example of searching for a course ID and reading associated numbers
    std::string courseId = "2149";
    trackAndReadNumbers(bst, courseId); 


    std::sort(Students.begin(), Students.end());
    for(size_t i = 0; i < Students.size(); i++){
        std::cout << Students[i] << std::endl;
    }
    std::cout << "Total number of students: " << Students.size() << std::endl;


    return 0;
}
