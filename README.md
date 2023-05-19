# Ext-Abs-StructuredSum
This repo is the *Automatic generation of structured abstracts for academic papers by using extractive and abstractive methods.*   
For each article, it is divided into the IMRD (Introduction, Methods, Results, Discussion) sections as input. 
This workflow is generated through a two-stage process and then merged into a structured abstract. 
The first stage is an extractive method, using a classifier to select a set of important sentences. 
The second stage is an abstractive method, using sentences set as input to generate a more readable abstract.
Based on the results from this experimental dataset, LGBM+BioBART exhibits the best summarization capability.

## Data collection
Retrieve articles written in structured format from PMC(PubMed Central) as the dataset. The code can be found in `pmc_builder/`  
1. `crawler/get_xml.py` - download XML files through the BioC API  
2. `crawler/xml2json.py` - convert to Json format  
3. `preprocess_json.py` - preprocess the files and save them in sentence-based JSON format.  

Next, use `feature_extractor.py` to extract sentence features from each article, and use `feature_by_train_test.py` to combine the data into train.parquet and test.parquet.
These files will be used as the dataset to train an extractive sentence classifier.

Note: You can directly download the `dataset/` from [here](https://drive.google.com/file/d/1hUCBdKWv91aSjJAtO_N3lc9yKpNtAMst/view?usp=sharing).  


## Extractive model
This step is to train a sentence classifier that distinguishes whether a sentence is suitable for abstract.
The sentence features used include sentence length, sentence position, title words, proper nouns, numerical token, TF-ISF, cosine similarity (SBERT) and section of the sentence.
The code can be found in `extractive_summarizer/model_training.ipynb`.

The model used is as follows:  
+ RF
+ XGBoost
+ LightGBM

After finding the best combination of models, `rouge_evaluation/ext_score.ipynb` can be used to evaluate the model scores.  
Through the best model, it outputs pairs of extracted sentences and abstract sentences written by the author.
These pairs are then used to fine-tune the next stage of the Seq2Seq model.


## Abstractive model
This step is fine-tuning a Transformer-based model using the extracted set of sentences as input to generate output that closely resembles a real abstract.
The code can be found in `abstractive_summarizer/model_training.ipynb`.

The model used is as follows:  
+ BART
+ BioBART

Similarly, by using `rouge_evaluation/abstr_score.ipynb`, you can obtain the scores of the model. This represents the results of the combined extractive and abstractive methods.


## References
+ `pmc_builder/extoracle` uses code partially derived from [pltrdy/extoracle_summarization](https://github.com/pltrdy/extoracle_summarization)
+  All articles were collected using the [BioC API](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/) provided by PMC
