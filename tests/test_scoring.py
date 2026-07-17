"""
Test: ML 评分模型
测试 ClassicalRescorer 和 ConsensusRescorer 的训练/预测/保存/加载。
"""
import os
import tempfile

import pytest
import numpy as np


class TestClassicalRescorerClassification:
    """测试分类模型"""

    def test_rf_classifier(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X),)
        assert np.all(proba >= 0) and np.all(proba <= 1)

    def test_lr_classifier(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="lr", task="classify", scale=True)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (len(X),)
        assert set(preds).issubset({0, 1})

    def test_gbt_classifier(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="gbt", task="classify", n_estimators=50)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X),)

    def test_xgb_classifier(self, sample_features):
        pytest.importorskip("xgboost")
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="xgb", task="classify", n_estimators=50)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X),)
        assert np.all(proba >= 0) and np.all(proba <= 1)

    def test_lgbm_classifier(self, sample_features):
        pytest.importorskip("lightgbm")
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="lgbm", task="classify", n_estimators=50)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X),)


class TestClassicalRescorerRegression:
    """测试回归模型"""

    def test_rf_regressor(self, sample_regression_data):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_regression_data
        model = ClassicalRescorer(model="rf", task="regress", n_estimators=50)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (len(X),)

    def test_ridge_regressor(self, sample_regression_data):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_regression_data
        model = ClassicalRescorer(model="ridge", task="regress", scale=True)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (len(X),)


class TestModelSaveLoad:
    """测试模型保存和加载"""

    def test_save_load_rf(self, sample_features, tmp_path):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        model.fit(X, y)

        save_path = str(tmp_path / "model.pkl")
        model.save(save_path)
        assert os.path.exists(save_path)

        loaded = ClassicalRescorer.load(save_path)
        proba_orig = model.predict_proba(X[:10])
        proba_loaded = loaded.predict_proba(X[:10])
        np.testing.assert_allclose(proba_orig, proba_loaded)

    def test_save_load_with_scaler(self, sample_features, tmp_path):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="lr", task="classify", scale=True)
        model.fit(X, y)

        save_path = str(tmp_path / "model_scaled.pkl")
        model.save(save_path)

        loaded = ClassicalRescorer.load(save_path)
        assert loaded.scaler is not None
        preds_orig = model.predict(X[:10])
        preds_loaded = loaded.predict(X[:10])
        np.testing.assert_array_equal(preds_orig, preds_loaded)


class TestConsensusRescorer:
    """测试共识评分"""

    def test_consensus_predict(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer, ConsensusRescorer
        X, y = sample_features

        m1 = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        m1.fit(X, y)
        m2 = ClassicalRescorer(model="lr", task="classify", scale=True)
        m2.fit(X, y)

        cons = ConsensusRescorer()
        cons.add(m1, weight=0.6)
        cons.add(m2, weight=0.4)
        scores = cons.predict(X)
        assert scores.shape == (len(X),)

    def test_consensus_rank_average(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer, ConsensusRescorer
        X, y = sample_features

        m1 = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        m1.fit(X, y)
        m2 = ClassicalRescorer(model="lr", task="classify", scale=True)
        m2.fit(X, y)

        cons = ConsensusRescorer()
        cons.add(m1)
        cons.add(m2)
        ranks = cons.rank_average(X)
        assert ranks.shape == (len(X),)
        # ranks should be non-negative
        assert np.all(ranks >= 0)

    def test_consensus_weights_normalized(self):
        from dockml.modern.scoring.classical import ConsensusRescorer
        cons = ConsensusRescorer()
        # 添加 dummy models
        class DummyModel:
            def predict_proba(self, X):
                return np.random.rand(len(X))
        cons.add(DummyModel(), weight=3.0)
        cons.add(DummyModel(), weight=7.0)
        np.testing.assert_allclose(cons.weights.sum(), 1.0)


class TestCVEvaluate:
    """测试交叉验证"""

    def test_cv_classify(self, sample_features):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_features
        model = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        results = model.cv_evaluate(X, y, n_fold=3)
        assert "test_roc_auc" in results
        assert "test_average_precision" in results
        assert results["test_roc_auc"] > 0.5  # better than random

    def test_cv_regress(self, sample_regression_data):
        from dockml.modern.scoring.classical import ClassicalRescorer
        X, y = sample_regression_data
        model = ClassicalRescorer(model="rf", task="regress", n_estimators=50)
        results = model.cv_evaluate(X, y, n_fold=3)
        assert "test_neg_root_mean_squared_error" in results or "test_r2" in results
