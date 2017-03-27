sudo apt-get install python3-numpy python3-nltk
sudo apt-get install python3-pip python-dev build-essential
sudo -H pip3 install PyEnchant
python3 -m nltk.downloader punkt
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader wordnet
python3 -m nltk.downloader averaged_perceptron_tagger
sudo -H pip3 install python-weka-wrapper3