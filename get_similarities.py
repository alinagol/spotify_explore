from pymongo import MongoClient
import json
from scipy.spatial.distance import euclidean, pdist, squareform


# MongoDB

cfg = json.load(open('config/mongo.json'))

db = 'mongodb://{host}:{port}'.format(**cfg['local'])  # local DB
with MongoClient(db) as client:
    tracksDB = client[cfg['local']['database']]['tracks']
    artistsDB = client[cfg['local']['database']]['artists']

#

def similarity_func(u, v):
    return 1/(1+euclidean(u, v))

DF_var = pd.DataFrame.from_dict({"s1":[1.2,3.4,10.2],"s2":[1.4,3.1,10.7],"s3":[2.1,3.7,11.3],"s4":[1.5,3.2,10.9]})
DF_var.index = ["g1","g2","g3"]

dists = pdist(DF_var, similarity_func)
DF_euclid = pd.DataFrame(squareform(dists), columns=DF_var.index, index=DF_var.index)