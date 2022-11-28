import requests
import shutil
from os import remove, mkdir
from statistics import mean, geometric_mean, harmonic_mean
from os.path import exists
import pandas as pd 
from os.path import exists
from alive_progress import alive_bar

# Arborescence du sysème de fichier import requests
import shutil
from os import remove, mkdir
from statistics import mean, geometric_mean, harmonic_mean
from os.path import exists
PATH            = "data/"
PATH_REQUEST    = "data/requests/"
PATH_DWH        = "data/dwh/"
PATH_DEF        = "data/def/"
PATH_E          = "data/e/"
PATH_NT         = "data/nt/"
PATH_RE         = "data/re/"
PATH_RS         = "data/rs/"
PATH_RT         = "data/rt/"

# Extension des fichiers 
EXT_REQUEST     = ".txt"
EXT_DEF         = "_def.csv"
EXT_E           = "_e.csv"
EXT_NT          = "_nt.csv"
EXT_RE          = "_re.csv"
EXT_RS          = "_rs.csv"
EXT_RT          = "_rt.csv"

# Data Warehouse
DWH_0 = "DWH_0.csv" 
DWH_1 = "DWH_1.csv" 
DWH_2 = "DWH_2.csv" 
DWH_3 = "DWH_3.csv" 
DWH_4 = "DWH_4.csv" 

class Terme: 
    def __init__(self, mot):
        self.mot = mot

        if self.isKnow(): 
            self.load()
        else: 
            self.download()

    def getMot(self): 
        return self.mot

    def getID(self): 
        return self.id

    def isKnow(self):
        return exists(PATH_REQUEST + self.mot + EXT_REQUEST)

    def request(self): 
        url = 'https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=' + self.mot + '&rel='
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        r = requests.post(url, headers=headers)

        # Enregistrer la requetes dans un fichier text
        f = open(PATH_REQUEST + self.mot + EXT_REQUEST, "w")
        f.write(r.text)
        f.close()

        f = open(PATH_REQUEST + self.mot + EXT_REQUEST, "r")
        lines = f.readlines()
        f.close()

        requestIsGood = "<br>//&nbsp; &nbsp; &nbsp; WARNING TROP GROS.<br>TOWARD CACHE<br>\n" not in lines and "<CODE>MUTED_PLEASE_RESEND\n" not in lines and "<div class=\"jdm-warning\"><br>Le terme '" + self.mot + "' n'existe pas !</div></div>\n"

        if not requestIsGood: 
            remove(PATH_REQUEST + self.mot + EXT_REQUEST)
            

        return requestIsGood

    def download(self):
        i = 0

        while not self.request() and i < 5: 
            i += 1

        f = open(PATH_REQUEST + self.mot + EXT_REQUEST, "r")
        lines = f.readlines()
        try : 
            code = [lines.index('<CODE>\n'), lines.index('</CODE>\n') +1]
        except ValueError: 
            code = [0, 0]

        index = {}

        for i in range(code[0], code[1]):
            if lines[i] == "<def>\n":
                index["def"] = i

            if lines[i] == "// les types de noeuds (Nodes Types) : nt;ntid;'ntname'\n":
                index["nt"] = i

            if lines[i] == "// les noeuds/termes (Entries) : e;eid;'name';type;w;'formated name' \n":
                index["e"] = i

            if lines[i] == "// les types de relations (Relation Types) : rt;rtid;'trname';'trgpname';'rthelp' \n":
                index["rt"] = i

            if lines[i] == "// les relations sortantes : r;rid;node1;node2;type;w \n":
                index["rs"] = i

            if lines[i] == "// les relations entrantes : r;rid;node1;node2;type;w \n":
                index["re"] = i 

            if lines[i] == "// END\n":
                index["end"] = i 
    

        #index
        m_def   = open(PATH_DEF + self.mot + EXT_DEF, "w")
        m_nt    = open(PATH_NT  + self.mot + EXT_NT,  "w")
        m_e     = open(PATH_E   + self.mot + EXT_E,   "w")
        m_rt    = open(PATH_RT  + self.mot + EXT_RT,  "w")
        m_rs    = open(PATH_RS  + self.mot + EXT_RS,  "w")
        m_re    = open(PATH_RE  + self.mot + EXT_RE,  "w")

        # Head
        m_nt.write("nt;ntid;ntname\n")
        m_e.write("e;eid;name;type;w;help\n")
        m_rt.write("rt;rtid;trname;trgpname;rthelp\n")
        m_rs.write("r;rid;node1;node2;type;w\n")
        m_re.write("r;rid;node1;node2;type;w\n")

        try: 
            for i in range(index['def'], index['nt']):
                m_def.write(lines[i])

            for i in range(index['nt']+2, index['e']):
                m_nt.write(lines[i].replace("'", ""))

            for i in range(index['e']+2, index['rt']):
                if lines[i].count(";") <= 5:
                    m_e.write(lines[i].replace("'", ""))

            for i in range(index['rt']+2, index['rs']):
                m_rt.write(lines[i].replace(" ; ", " ").replace("'", "")) # Modifier les séparateur pour éviter les pb à l'ouverture

            if 're' in index and 'rs' in index: 
                for i in range(index['rs']+2, index['re']):
                    m_rs.write(lines[i])

                for i in range(index['re']+2, index['end']):
                    m_re.write(lines[i])
            elif 'rs' in index: 
                for i in range(index['rs']+2, index['end']):
                    m_rs.write(lines[i])
            elif 're' in index: 
                for i in range(index['re']+2, index['end']):
                    m_re.write(lines[i])
        except KeyError: 
            pass

        m_def.close()
        m_nt.close()
        m_e.close()
        m_rt.close()
        m_rs.close()
        m_re.close()

        self.load()

    def load(self):
        self.E  = pd.read_csv(PATH_E  + self.mot + EXT_E,  sep=";")
        self.NT = pd.read_csv(PATH_NT + self.mot + EXT_NT, sep=";")
        self.RE = pd.read_csv(PATH_RE + self.mot + EXT_RE, sep=";")
        self.RS = pd.read_csv(PATH_RS + self.mot + EXT_RS, sep=";")
        self.RT = pd.read_csv(PATH_RT + self.mot + EXT_RT, sep=";")
        self.R  = pd.concat([self.RS, self.RE])

        if self.RS.shape[0] > 0:
            self.id = int(self.RS['node1'][0])
        else:
            self.id = -1

        #self.id = int(self.E.loc[self.E['name'] == self.mot]['eid'][0])

    def initMyLocalDataBase(): 
        if not exists(PATH): 
            mkdir(PATH)

        if not exists(PATH_DEF): 
            mkdir(PATH_DEF)

        if not exists(PATH_REQUEST): 
            mkdir(PATH_REQUEST)

        if not exists(PATH_DWH): 
            mkdir(PATH_DWH)

            # Creer les entrepots
            DWH1 = open(PATH_DWH + DWH_1, "w")
            DWH2 = open(PATH_DWH + DWH_2, "w")
            DWH3 = open(PATH_DWH + DWH_3, "w")
            DWH4 = open(PATH_DWH + DWH_4, "w")

            # Ecrirre les entete
            DWH1.write("mot1;type_relation;name_relation;weight_relation;mot2\n")
            DWH2.write("mot1;type_relation_1;name_relation_1;weight_relation_1;mot2;type_relation_2;name_relation_2;weight_relation_2;mot3;mean;geometric_mean;harmonic_mean\n")
            DWH3.write("mot1;type_relation_1;name_relation_1;weight_relation_1;mot2;type_relation_2;name_relation_2;weight_relation_2;mot3;type_relation_3;name_relation_3;weight_relation_3;mot4;mean;geometric_mean;harmonic_mean\n")
            DWH4.write("mot1;type_relation_1;name_relation_1;weight_relation_1;mot2;type_relation_2;name_relation_2;weight_relation_2;mot3;type_relation_3;name_relation_3;weight_relation_3;mot4;type_relation_4;name_relation_4;weight_relation_4;mot5;mean;geometric_mean;harmonic_mean\n")
            
            # Fermer les fichier
            DWH1.close() 
            DWH2.close() 
            DWH3.close() 
            DWH4.close() 

        if not exists(PATH_E): 
            mkdir(PATH_E)

        if not exists(PATH_NT): 
            mkdir(PATH_NT)

        if not exists(PATH_RE): 
            mkdir(PATH_RE)

        if not exists(PATH_RS): 
            mkdir(PATH_RS)

        if not exists(PATH_RT): 
            mkdir(PATH_RT)

    def deleteMyLocalDataBase():
        if exists(PATH):
            shutil.rmtree(PATH)

    def isValidTerme(terme): 
        return " " not in terme and "<" not in terme and">" not in terme and":" not in terme and "\x9c" not in terme and "ï" not in terme and "_" not in terme

class Trie(object):
    def __init__(self,wd="",end=False):
        self.br={}; self.end=end
        if wd!="": self.addword(wd)
    def __repr__(self): # Uniquement pour les tests
        br=self.br.__repr__()
        m='E,' if self.end else ""
        return "T["+m+br+"]"

    def addword(self,wd):
        br=self.br
        if wd:
            c=wd[0]; rst=wd[1:] # Découpage essentiel
            if c not in br: 
                br[c]=Trie() # Nouvelle branche
            br[c].addword(rst)
        else: 
            self.end=True # Marqueur de la fin       

    def searchword(self,wd):
        if self.search(wd): 
            print(str(wd) + " is in Trie")
            self.sufix(wd)
        else:
            print(str(wd) + " is not in Trie")

    def sufix(self, wd):
        br = self.br
        for c in wd:
            br = br[c]

        print(br.words())

    def search(self,wd):
        br=self.br
        if wd:
            c=wd[0]; rst=wd[1:] # Découpage essentiel
            if c in br : 
                if len(rst) == 0: 
                    return True
                else : 
                    return br[c].search(rst)
            else : 
                return False
            

    def __getitem__(self,c):  # Objet émule une liste/dict.
        return self.br[c]

    # Renvoie tout les mots du dictionnaire
    def words(self):
        br=self.br
        l=[]
        for c in br:
            w=br[c].words() # Les suffixes du mot en question
            if w==[]: 
                x=[c] # Si vide
            else:
                x=[c + " " + h for h in w] # Non vide. c à la tête
                if br[c].end: 
                    x+= (" " + str(c)) #[c] # Cas spécial ! 
            l+=x
        return l