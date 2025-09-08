# Replace with real IDS dataset pipeline. Exports ONNX to ../models/model.onnx
import numpy as np, os
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve
from xgboost import XGBClassifier
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

X, y = np.random.rand(8000,2).astype('float32'), (np.random.rand(8000)>0.96).astype(int)
Xtr, Xte, ytr, yte = train_test_split(X,y,test_size=0.2, stratify=y, random_state=42)
clf = XGBClassifier(max_depth=4, n_estimators=300, learning_rate=0.1, subsample=0.8, eval_metric='logloss')
clf.fit(Xtr, ytr)
proba = clf.predict_proba(Xte)[:,1]
auc = roc_auc_score(yte, proba)
ap = average_precision_score(yte, proba)
print('ROC-AUC=', auc); print('PR-AUC=', ap)

# Find threshold at FPR≈1% (approx using PR)
precisions, recalls, thresholds = precision_recall_curve(yte, proba)
# crude selection for demonstration
thr = np.quantile(proba, 0.99)
print('THRESHOLD_SUGGEST=', float(thr))

onnx_model = convert_sklearn(clf, initial_types=[('input', FloatTensorType([None, 2]))])
os.makedirs('../models', exist_ok=True)
with open('../models/model.onnx', 'wb') as f:
    f.write(onnx_model.SerializeToString())
print('Saved ../models/model.onnx')
