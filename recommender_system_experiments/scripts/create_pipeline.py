from sklearn2pmml.pipeline import PMMLPipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn2pmml import _escape
import joblib
import dill
import os

VECTOR_DIM = 1000

def store_pkl(obj, name, flavour = "joblib", escape_func = _escape):
	if escape_func:
		obj = escape_func(obj, escape_func = escape_func)
	path = "pkl/" + name + ".pkl"
	if not os.path.exists("pkl"):
		os.makedirs("pkl", exist_ok=True)
	if flavour == "joblib":
		joblib.dump(obj, path, compress = 9)
	elif flavour == "dill":
		with open(path, "wb") as dill_file:
			dill.dump(obj, dill_file)
	else:
		raise ValueError(flavour)

pipeline = PMMLPipeline(
    [
        ("vectorizer", TfidfVectorizer(
            max_features=VECTOR_DIM,
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b\w+\b'
        )),
    ]
)
pipeline.configure()

pipeline.fit_transform(["Sample text for vectorization."])
store_pkl(pipeline, "tfidf_vectorizer", flavour="joblib")
