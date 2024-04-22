mkdir -p lambda-layer/python
cd lambda-layer/python
pip3 install --platform manylinux2014_x86_64 --target . --python-version 3.12 --only-binary=:all: line-bot-sdk

cd ..
zip -r ./lambda_layers/linebot_lambda_layer.zip python

echo "Layer build complete"