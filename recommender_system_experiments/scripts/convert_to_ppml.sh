
[ -d "jpmml-sklearn" ] || git clone https://github.com/jpmml/jpmml-sklearn.git

# if [ -d "jpmml-sklearn/pmml-sklearn-example" ]; then
#   cd jpmml-sklearn 
#   mvn clean install -DskipTests 
# else
#   echo "Error: pmml-sklearn-example directory not found."
#   exit 1
# fi

# cd ../../
java -jar jpmml-sklearn/pmml-sklearn-example/target/pmml-sklearn-example-executable-1.9-SNAPSHOT.jar --pkl-input data/03_artifacts/pipeline.pkl --pmml-output data/03_artifacts/pipeline.pmml
