# Eddx2JSON
This is a code repository for converting mind maps from Edraw eddx files to JSON format.

* How to run:\
Modify the file name in the last line of eddx2json.py, place your .eddx file in the current directory, and run the script. After execution, a folder with the same name as your .eddx file will be created, and each page's mind map will be converted and saved separately in its corresponding subfolder.
* The mode parameter has two options: topic_root and idea_root.\
The former exports the second-level nodes (MainTopic) as root nodes and ignores the top-level node, while the latter exports the top-level node (MainIdea) as the root node.
