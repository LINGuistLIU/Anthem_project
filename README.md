How to run: 

1. convert the ShAReCLEF2014 disorders and disorder negations into WebAnno TSV v3.2 format 

    ```python convert_ShAReCLEF2014_to_WebAnnoTSV3.py```

2. convert the treatments annotated by the BERT model to the ShAReCLEF 2014 format.

    ```python convert_treatments_to_ShAReCLEF2014.py```

3. add the output from step 2 to the WebAnno TSV v3.2 format.

    ```python convert_treatments_to_WebAnnoTSV3.py```
