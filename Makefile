FUNCTION=cartolafc_function
ZIP=olheiro.zip
OUT=outfile


deploy:
	echo ">>> Recreating zip file locally."

	rm -f $(ZIP)
	zip $(ZIP) -r requests lambda_function.py

	echo ">>> Uploading function code remotely."

	aws lambda update-function-code --function-name $(FUNCTION) --zip-file fileb://$(ZIP)

run:
	aws lambda invoke --function-name $(FUNCTION) $(OUT)

test:
	python test_lambda_function.py
