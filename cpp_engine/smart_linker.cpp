#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <unordered_map>
#include <algorithm>

using namespace std;

// Structure for a node from the Trie
// IMPORTANT : "children" is a way to "choose" on which path the you would go on from the current node
// since one node (e.g. root) can have multiple links, each leading us to a different node from the lower layer
struct TrieNode {
    unordered_map<char, int> children; // Saves the childrens's index and the letter you need to ACCESS IT.
    int fail = 0; // Failure link
    vector<int> output; // Words' IDs end here
};

class SmartLinker {
  private:
    vector<TrieNode> trie;
    vector<pair<string, string>> keywords_data; // Pairs of {Found_word, Obsidian_destination}

    // Function that verifies whether a character is a word separator
    bool is_word_boundary (char c){
      if (c == ' ' || c == '\n' || c == '\t' || c == '\r' || 
            c == '.' || c == ',' || c == ';' || c == ':' || 
            c == '!' || c == '?' || c == '(' || c == ')' || 
            c == '[' || c == ']' || c == '"' || c == '\'') {
            return true;
    }
    return false;
  }

  public:
    SmartLinker(){
      trie.emplace_back(); // Root node (index 0)
    }
  
    // 1) Initialize tree with all words from master_glossary
    void initialize_search_tree(const unordered_map<string, string>& words_dict){
      trie.clear();
      trie.emplace_back();
      keywords_data.clear();
      
      //Building the Trie and initializing a dictionary from Python
      for(const auto& pair: words_dict){
        const string& word = pair.first;
        const string& destination = pair.second;

        keywords_data.push_back({word, destination});
        int word_idx = keywords_data.size() - 1;

        int node = 0;
        for(char c : word){
          if(!trie[node].children.count(c)){
            trie[node].children[c] = trie.size();
            trie.emplace_back();
          }
          node = trie[node].children[c];
        }
        trie[node].output.push_back(word_idx);
      }
      build_failure_links();
    }

    // 2) Searches the text and replaces with [[Word]]
    string inject_obsidian_links(const string& text){
      if (keywords_data.empty() || text.empty()) return text;

      int node = 0;
      // Keeps the found intervals: [start_index, end_index, word_id]
      vector<pair<pair<int, int>, int>> matches;

      for(size_t i = 0; i < text.size(); ++i){
        char c = text[i];
        while(node > 0 && !trie[node].children.count(c)){
          node = trie[node].fail;
        }
        if (trie[node].children.count(c)){
          node = trie[node].children[c];
        }

        for(int word_idx : trie[node].output){
          int word_len = keywords_data[word_idx].first.size();
          int start_pos = static_cast<int>(i) - word_len + 1;
          int end_pos = static_cast<int>(i);

          // Verification -- Word Boundary
          bool is_valid_start = (start_pos == 0 || is_word_boundary(text[start_pos - 1]));
          bool is_valid_end = (end_pos == static_cast<int>(text.size()) - 1 || is_word_boundary(text[end_pos + 1]));

          if(is_valid_start && is_valid_end){
            matches.push_back({{start_pos, i}, word_idx});
          }
        }
      }

      // Building the new text with [[...]]
      // (For simplicity, direct replacement has no overlapping)
      string result = "";
      int last_pos = 0;

      // Sorts from the start position
      sort(matches.begin(), matches.end());

      for(auto& match : matches){
        int start = match.first.first;
        int end = match.first.second;
        int word_idx = match.second;

        if(start < last_pos) continue; // Prevents links overlapping

        result += text.substr(last_pos, start - last_pos);

        string display_text = keywords_data[word_idx].first;
        string destination = keywords_data[word_idx].second;

        // Construction of the Obsidian link : [[Destination|ShownText]]
        if(display_text == destination){
            result += "[[" + display_text + "]]";
        } else {
            result += "[[" + destination + "|" + display_text + "]]";
        }

        last_pos = end + 1;
        
      }
      result += text.substr(last_pos);
      return result;
    }

  private:
    // Building the failure links using BFS
    void build_failure_links(){
      queue<int> q;
      for(auto& pair : trie[0].children){
        trie[pair.second].fail = 0;
        q.push(pair.second);
      }

      while(!q.empty()){
        int current = q.front();
        q.pop();

        for(auto& pair : trie[current].children){
          char c = pair.first;
          int child = pair.second;

          int fail_node = trie[current].fail;
          while(fail_node > 0 && !trie[fail_node].children.count(c)){
            fail_node = trie[fail_node].fail;
          }
          if(trie[fail_node].children.count(c)){
            trie[child].fail = trie[fail_node].children[c];
          }else {
            trie[child].fail = 0;
          }

          // Sticking the outputs of the current node
          auto& fail_out = trie[trie[child].fail].output;
          trie[child].output.insert(trie[child].output.end(), fail_out.begin(), fail_out.end()); 
          q.push(child);
        }
      }
    }
};

// Global initialization 
SmartLinker global_linker;

void init_tree(const unordered_map<string,string>& words_dict){
  global_linker.initialize_search_tree(words_dict);
}

string inject_links(const string& text){
  return global_linker.inject_obsidian_links(text);
}