# Hoax Analyzer
Machine Learning Section

## How to Start
### Python
1. First, you have to make sure that Python3 has already installed in your computer. You can get Python3 by typing:
    ```sh
    $ sudo apt-get update && sudo apt-get install -y build-essential git libjpeg-dev
    $ apt-get install python3
    $ apt-get install python3-pip
    ```
2. Install dependencies by typing:
    ```sh
    $ bash setup.sh
    ```
2. Move to folder `scripts`. Rename `config.py-ex` into `config.py` and fill every variables with the corresponding and correct values.
3. You can test the program by typing `python3 hoax_analyzer.py [filename]`. For example:
    ```sh
    $ python3 hoax_analyzer.py ../dataset/idn-hoax/1.txt
    ```
    *Please note that you have to have the ../dataset/idn-hoax/1.txt file beforehand*

### Java
1.  First, you have to make sure that Java has already installed in your computer. For further information, you can visit http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html.
2.  Copy `resource` folder contents to `scripts/resource` (if you want to execute the Python program) and `lib/resource` (if you want to execute in the lib folder). The folder contains resources to execute HoaxAnalyzer.jar. You can find the folder in `java/HoaxAnalyzer/`.
3. You can try to execute the jar file by typing `java -jar HoazAnalyzer.jar [type] [filename]`in the `lib` folder. For example:
    ```sh
    $ java -jar HoaxAnalyzer.jar preprocess ../dataset/idn-hoax/1.txt
    $ java -jar HoaxAnalyzer.jar extract ../dataset/idn-fact/1.txt
    ```
    *Please note that you have to have the ../dataset/idn-hoax/1.txt and ../dataset/idn-fact/1.txt files beforehand*
