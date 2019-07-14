import os
import requests
import json
import urllib3
import xml.etree.ElementTree as ET
from lxml import html, etree
from datetime import datetime

requests.packages.urllib3.disable_warnings()

class resourceAccumulator():
    def __init__(self):
        self.resources = {}

    def addParentPage(self,parent):
        self.resources[parent] = {}
        self.resources[parent]['script'] = []
        self.resources[parent]['input'] = []
        self.resources[parent]['hidden'] = []
        self.resources[parent]['href'] = []
        self.resources[parent]['session'] = {}
    
    def addResources(self,category,resources,parent):
        for webItem in resources:
            self.resources[parent][category].append(webItem)

class processURL():
    def getPageHandle(self,url):
        return requests.get(url,verify=False)

    def getPageContent(self,url):
        htObject = self.getPageHandle(url)
        return htObject.content

    def makeXHTML(self,content):
        xObject = html.fromstring(content)
        xStrObj = etree.tostring(xObject)
        return ET.fromstring(xStrObj)

    def getProcObj(self,url):
        rawObj = self.getPageContent(url)
        return self.makeXHTML(rawObj)

class parsePage():
    def getSources(self,xmlDoc):
        returns = []
        for tagged in xmlDoc.iter('script'):
            if 'src' in tagged.attrib:
                returns.append(tagged.attrib['src'])
        return returns

    def getInputs(self,xmlDoc):
        returns = []
        for field in xmlDoc.iter('input'):
            fieldAttr = {}
            for keyID in field.attrib:
                fieldAttr[keyID] = field.attrib[keyID]
            returns.append(fieldAttr)
        return returns

    def getHidden(self,xmlDoc):
        types = open('resources/tagtypes.txt').read().splitlines()
        returns = []
        for each in types:
            typeDef = {}
            for x in xmlDoc.iter(each):
                if 'hidden' in x.attrib:
                    for attr in x.attrib:
                        typeDef[attr] = x.attrib[attr]
                    returns.append(typeDef)
        return returns
            
    def getHref(self,xmlDoc):
        returns = []
        for a in xmlDoc.iter('a'):
            if 'href' in a.attrib:
                returns.append(a.attrib['href'])
        for l in xmlDoc.iter('link'):
            if 'href' in l.attrib:
                returns.append(l.attrib['href'])
        return returns

    def getSession(self,url):
        session = requests.Session()
        active = session.get(url)
        return active.cookies.get_dict()

class scanBroker():
    def __init__(self):
        self.accumulator = resourceAccumulator()

    def prepScan(self,urls):
        for uri in urls:
            self.accumulator.addParentPage(uri)
    
    def startScan(self,urls):
        for item in urls:
            print('Processing {}...'.format(item))
            doc = processURL().getProcObj(item)
            print(' |-Getting HTML Doc for XML conversion...')
            print(' |-Processing Scripts...')
            self.accumulator.addResources('script',parsePage().getSources(doc),item)
            print(' |-Processing Inputs...')
            self.accumulator.addResources('input',parsePage().getInputs(doc),item)
            print(' |-Processing Hidden Elements...')
            self.accumulator.addResources('hidden',parsePage().getInputs(doc),item)
            print(' |-Processing Hrefs...')
            self.accumulator.addResources('href',parsePage().getHref(doc),item)
            print(' |-Gathering Session Variables...')
            self.accumulator.addResources('session',parsePage().getSession(item),item)            

    def finalizeScan(self):
        print('Finalizing scan and writing json report...')
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        if os.path.exists('reports') == False:
            os.mkdir('reports')
        jsonFileOut = open('reports/{}.json'.format(now),'w')
        jsonFileOut.write(json.dumps(self.accumulator.resources,
                          sort_keys=True,
                          indent=4
                          ))
        jsonFileOut.close()
        print('Done! You may review the results in "reports/{}.json"'.format(now))
        
            
    def initializeScan(self,urls):
        self.prepScan(urls)
        self.startScan(urls)
        self.finalizeScan()


                    
        
    
