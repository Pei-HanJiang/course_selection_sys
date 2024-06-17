#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iomanip>
#include <filesystem>

using namespace std;

unordered_map<string, unordered_set<string> > studentToFile;
unordered_map<string, unordered_set<string> > courseToFile;

void loadDataFromFile(const string &filename)
{
    ifstream file(filename);
    if (!file.is_open())
    {
        cerr << "Error opening file: " << filename << endl;
        return;
    }

    string line;
    getline(file, line);
    while (getline(file, line))
    {
        string student_id, course_id;
        size_t pos = line.find(',');
        if (pos != string::npos)
        {
            student_id = line.substr(0, pos);
            course_id = line.substr(pos + 1);
            course_id.erase(course_id.find_last_not_of(" \n\r\t") + 1);

            string shortFilename = filename.substr(5); // Remove "data/" prefix

            studentToFile[student_id].insert(shortFilename);
            courseToFile[course_id].insert(shortFilename);
        }
    }

    file.close();
}

void loadAllData()
{
    for (int i = 1; i <= 466; ++i)
    {
        stringstream ss;
        ss << "data/" << setw(4) << setfill('0') << i;
        string filename = ss.str();

        loadDataFromFile(filename);
    }
}

void createIndexFiles(const string &baseIndexFolder, const unordered_map<string, unordered_set<string> > &dataMap)
{
    int fileCount = 1;
    int currentSize = 0;

    ofstream indexFile(baseIndexFolder + "/" + to_string(fileCount) + ".txt");
    if (!indexFile.is_open())
    {
        cerr << "Error creating index file: " << baseIndexFolder + "/" + to_string(fileCount) + ".txt" << endl;
        return;
    }

    for (const auto &entry : dataMap)
    {
        string line = entry.first + ":";

        for (const string &filename : entry.second)
        {
            line += " " + filename;
        }
        line += "\n";

        // Check if adding this line exceeds the size limit
        if (currentSize + line.size() > 2048)
        { // 2 KB limit
            indexFile.close();
            ++fileCount;
            indexFile.open(baseIndexFolder + "/" + to_string(fileCount) + ".txt");
            if (!indexFile.is_open())
            {
                cerr << "Error creating index file: " << baseIndexFolder + "/" + to_string(fileCount) + ".txt" << endl;
                return;
            }
            currentSize = 0;
        }

        indexFile << line;
        currentSize += line.size();
    }

    indexFile.close();
}

vector<string> Course;

int SearchPair(const string givenfile, const string target_student_id)
{
    string filepath = "data/" + givenfile;
    ifstream file(filepath);
    if (!file)
    {
        cerr << "Error opening file: " << filepath << endl;
    }

    string line;
    getline(file, line);
    int i = 0;
    while (getline(file, line))
    {
        // Use stringstream to split the line by comma
        istringstream ss(line);
        string student_id, course_id;
        getline(ss, student_id, ',');
        getline(ss, course_id, ',');

        // Check if the first field (student_id) matches the target student ID
        if (student_id == target_student_id)
        {
            // cout << course_id << endl;
            Course.push_back(course_id);
            i++;
        }
    }

    // Close the file
    file.close();
    return i;
}

void queryStudentCourses(const string &student_id)
{
    int total = 0;
    if (studentToFile.find(student_id) != studentToFile.end())
    {
        cout << "Courses for student " << student_id << ":" << endl;
        for (const auto &filename : studentToFile[student_id])
        {
            // cout << filename << " ";
            total += SearchPair(filename, student_id);
        }
        cout << endl;
    }
    else
    {
        cout << "No courses found for student " << student_id << endl;
    }
    sort(Course.begin(), Course.end());
    for(size_t i = 0; i < Course.size(); i++){
        cout << Course[i] << endl;
    }
    cout << "Total classes taken : " << Course.size() << endl;
}

// find the students with given course id
vector<string> Students;
int SearchSPair(const string givenfile, const string target_course_id)
{
    string filepath = "data/" + givenfile;
    ifstream file(filepath);
    if (!file)
    {
        cerr << "Error opening file: " << filepath << endl;
    }

    string line;
    getline(file, line);
    int amount = 0;
    while (getline(file, line))
    {
        istringstream ss(line);
        string student_id, course_id;
        getline(ss, student_id, ',');
        getline(ss, course_id, ',');
        course_id.erase(course_id.find_last_not_of(" \n\r\t") + 1);

        // Check if the first field (student_id) matches the target student ID
        if (course_id == target_course_id)
        {
            // cout << student_id << endl;
            Students.push_back(student_id);
            amount++;
        }
    }

    file.close();
    return amount;
}

void queryCourseStudents(const string &course_id)
{
    int total = 0;
    if (courseToFile.find(course_id) != courseToFile.end())
    {
        cout << "Students for course " << course_id << ":" << endl;
        for (const auto &filename : courseToFile[course_id])
        {
            total += SearchSPair(filename, course_id);
        }
        cout << endl;
    }
    else
    {
        cout << "No students found for course " << course_id << endl;
    }
    sort(Students.begin(), Students.end());
    for(size_t i = 0; i < Students.size(); i++){
        cout << Students[i] << endl;
    }
    cout << "Total number of students : " << Students.size() << endl;

}

int main()
{
    loadAllData();

    createIndexFiles("student_index", studentToFile);
    createIndexFiles("course_index", courseToFile);

    cout << "Index files created successfully." << endl;

    // Demo queries
    queryStudentCourses("D0996611");
    // queryCourseStudents("2997");

    return 0;
}
