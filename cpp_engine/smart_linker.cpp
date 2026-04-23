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
    vector<string> keywords;

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

  public:
    SmartLinker(){
      trie.emplace_back(); // Root node (index 0)
    }
  
    // 1) Initialize tree with all words from master_glossary
    void initialize_search_tree(const vector<string>& words){
      keywords = words;
      trie.clear();
      trie.emplace_back();

      // Building the Trie
      for(int i = 0; i < words.size(); ++i){
        int node = 0;
        for(char c : words[i]){
          if(!trie[node].children.count(c)){
            trie[node].children[c] = trie.size();
            trie.emplace_back();
          }
          node = trie[node].children[c];
        }
        trie[node].output.push_back(i);
      }
      build_failure_links();
    }

    // 2) Searches the text and replaces with [[Word]]
    string inject_obsidian_links(const string& text){
      if (keywords.empty() || text.empty()) return text;

      int node = 0;
      // Keeps the found intervals: [start_index, end_index, word_id]
      vector<pair<pair<int, int>, int>> matches;

      for(int i = 0; i < text.size(); ++i){
        char c = text[i];
        while(node > 0 && !trie[node].children.count(c)){
          node = trie[node].fail;
        }
        if (trie[node].children.count(c)){
          node = trie[node].children[c];
        }

        for(int word_idx : trie[node].output){
          int word_len = keywords[word_idx].size();
          int start_pos = i - word_len + 1;
          matches.push_back({{start_pos, i}, word_idx});
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

        if(start < last_pos) continue;

        result += text.substr(last_pos, start - last_pos);
        result += "[[" + keywords[word_idx] + "]]";
        last_pos = end + 1;
      }
      result += text.substr(last_pos);
      return result;
    }
};

// Global initialization 
SmartLinker global_linker;

void init_tree(const vector<string>& words){
  global_linker.initialize_search_tree(words);
}

string inject_links(const string& text){
  return global_linker.inject_obsidian_links(text);
}