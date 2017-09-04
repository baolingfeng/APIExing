#!/bin/bash

python enner.py bc-ce < api_recog/train_all.conll > api_recog/train_all.data
python enner.py bc-ce < api_recog/test_all.conll > api_recog/test_all.data
python enner.py bc-ce < api_recog/test_all.conll > api_recog/test_pd.data
python enner.py bc-ce < api_recog/test_all.conll > api_recog/test_np.data
python enner.py bc-ce < api_recog/test_all.conll > api_recog/test_mpl.data

crfsuite learn -m model_all api_recog/train_all.data

crfsuite tag -m model_all -qt api_recog/test_all.data
crfsuite tag -m model_all -qt api_recog/test_pd.data
crfsuite tag -m model_all -qt api_recog/test_np.data
crfsuite tag -m model_all -qt api_recog/test_mpl.data
