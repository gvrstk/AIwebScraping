#Import Pandas Library to read Excel file
import pandas as pd
#Import subprocess 
# Import Requests and BeautifulSoup
import requests
from bs4 import BeautifulSoup
import os
import spacy
import textacy
#from spacy import displacy
import csv
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)

curdir = os.path.dirname(os.path.abspath(__file__))

def readFile():
#Create Pandas Object
  data = pd.read_excel( curdir +"\\" + "Resources.xlsx")
  return data

def getData(link):
  resp = requests.get(link)
  return resp


# Process Response using BeautifulSoup 
def extractHTML(resp):
  soup = BeautifulSoup(resp.content, 'html5lib')
  parsed_text = ""
  for para in soup.find_all("p"):
      #parsed_text_str += str(para.get_text())
       parsed_text = " ".join((parsed_text, str(para.get_text())))

  return parsed_text
 
print("current Dir: " + curdir)
xlfile = readFile()
#xlfile.info()
for ind in xlfile.index :
    print(xlfile['topic'][ind], xlfile['link'][ind] )
    topic = xlfile['topic'][ind]
    url = xlfile['link'][ind]
    filters = xlfile['element'][ind]
    r = getData(url)
    print("----------------------------------- Extracted Data -----------------------------------")
    results = extractHTML(r)
    #print(results)
    filepath = curdir + "\\scraping_out\\" + topic + "_rawout.txt"
    f = open(filepath, "w" , encoding="utf-8")
    f.write(results)
    f.close()
    #Write Data into csv
    sentences = [[i] for i in nlp(results).sents]
    myheaders = ['sentence']
    myvalues = sentences
    filename = curdir + "\\csv_out\\" + topic + "_csvout.csv"
    with open(filename, 'w',newline='',encoding="utf-8") as myfile:
       writer = csv.writer(myfile)
       writer.writerow(myheaders)
       writer.writerows(myvalues)
    csv_sentences = pd.read_csv(filename)
    entity_pairs = []
    doc = nlp(results)
    triples = list(textacy.extract.subject_verb_object_triples(doc))
    #print(triples)
    #listofverb = ["maintains",]
    nodes = []
    relations = []# iterate over the triples
    for triple in triples:    # extract the Subject and Object from triple"
     #print(str(triple.subject))
     if str(triple.subject) == "[RBI]" and (str(triple.verb) == "[works]" or str(triple.verb) == "[maintains]" or str(triple.verb) == "[manages]" or str(triple.verb) == "[monitors]" or str(triple.verb) == "[controls]" or str(triple.verb) == "[works]" or str(triple.verb) == "[helps]" or str(triple.verb) == "[play]" or str(triple.verb) == "[facilitates]" ):
        #print("in IF")
        node_subject = "_".join(map(str, triple.subject))
        node_object  = "_".join(map(str, triple.object))    
        nodes.append(node_subject)
        nodes.append(node_object)    # extract the relation between S and O
        # add the attribute 'action' to the relation
        relation = "_".join(map(str, triple.verb))
        relations.append((node_subject,node_object,{'action':relation}))# remove duplicate nodes
        nodes = list(set(nodes))
        #print(relations)

print(relations)
G = nx.DiGraph()
G.add_nodes_from(nodes)
G.add_edges_from(relations)
# extract the attribute 'action' from edges
edge_attribute = nx.get_edge_attributes(G, 'action')
edges, weights = zip(*edge_attribute.items())# resize figure
plt.rcParams["figure.figsize"] = [5, 2]
plt.rcParams["figure.autolayout"] = True# set figure layout
pos = nx.circular_layout(G)# draw graph
nx.draw(G, pos, node_color='b', width=1, with_labels=True)# draw edge attributes
nx.draw_networkx_edge_labels(G, pos,edge_attribute, label_pos=0.50 )
plt.show()    
