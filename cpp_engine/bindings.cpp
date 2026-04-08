#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Very important: automatically converts lists/strings

namespace py = pybind11;

// Declaring functions from smart_linker.cpp in order to use them here
void init_tree(const std::vector<std::string>& words);
std::string inject_links(const std::string& text);

PYBIND11_MODULE(cpp_linker, m){
  m.doc() = "C++ Engine for Aho-Corasick string matching in ObsidiantPipe";

  // Exposing functions to Python
  m.def("initialize_search_tree", &init_tree, "Initialize the Aho-Corasick trie with a list of keywords");
  m.def("inject_obsidian_links", &inject_links, "Parse text and replace keywords with Obsidian links");
}

