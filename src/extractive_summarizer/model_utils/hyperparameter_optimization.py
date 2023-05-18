import time
import sklearn.model_selection as sk
# import dask_ml.model_selection as dcv
from contextlib import contextmanager


# 超參數優化
def do_HPO(model, gridsearch_params, X, y, metric='f1', mode='gpu-Grid', n_folds=5, n_iter=10):
    if mode == 'gpu-grid':
        clf = sk.GridSearchCV(model, gridsearch_params, cv=n_folds, scoring=metric)
    elif mode == 'gpu-random':
        clf = sk.RandomizedSearchCV(model, gridsearch_params, cv=n_folds, scoring=metric, n_iter=n_iter)     
    else:
        print("please choose one of [gpu-grid, gpu-random] mode")
        return None, None  
    res = clf.fit(X, y)
    print("Best params: {}\nBest score: {}".format(res.best_params_, res.best_score_))
    return res.best_estimator_, res

# 代碼塊 - 執行時間
@contextmanager
def timed():
    t0 = time.time()
    yield
    t1 = time.time()
    print("Run time: %8.5f" % (t1 - t0))
    