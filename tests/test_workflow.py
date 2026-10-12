import json
import pytest
from ndeq_examples.runner import run
from ndeq_examples.config import resolve
from ndeq_examples.models import build


@pytest.mark.parametrize("example",["decay","heat","star","api_mesh","api_callbacks"])
def test_key_smoke_outputs(example,tmp_path):
    out = run(example,root=tmp_path)
    status = json.loads((out/"status.json").read_text(encoding="utf-8"))
    assert status["status"] in ("smoke_passed","snippet_verified")
    assert (out/"metrics.json").exists()
    if example in ("decay","heat","star"):
        assert status["numerical_pass"] is False
        assert (out/"test_data.npz").exists()
        assert (out/"solution.png").exists()


def test_optimizer_owns_exactly_the_star_network():
    solver=build(resolve("star"))
    assert {id(p) for n in solver.nets for p in n.parameters()} == {
        id(p) for g in solver.optimizer.param_groups for p in g["params"]}
    assert solver.optimizer.param_groups[0]["lr"] == .01


def test_resume_from_finished_checkpoint_preserves_prediction(tmp_path):
    import numpy as np
    first=run("decay",root=tmp_path)
    resumed=run("decay",root=tmp_path,resume_from=first)
    assert first != resumed
    assert np.array_equal(np.load(first/"test_data.npz")["prediction"],
                          np.load(resumed/"test_data.npz")["prediction"])
    history=json.loads((resumed/"history.json").read_text(encoding="utf-8"))
    assert len(history["train_loss"])==2


def test_resume_interrupted_training_matches_uninterrupted(tmp_path):
    import numpy as np
    from ndeq_examples.runner import setup,checkpoint
    complete=run("decay",root=tmp_path)
    setup(42)
    cfg=resolve("decay"); cfg["device"]="cpu"
    solver=build(cfg)
    solver.fit(1,tqdm_file=None)
    interrupted=tmp_path/"interrupted"
    interrupted.mkdir()
    checkpoint(interrupted,solver,cfg)
    resumed=run("decay",root=tmp_path,resume_from=interrupted)
    assert np.array_equal(np.load(complete/"test_data.npz")["prediction"],
                          np.load(resumed/"test_data.npz")["prediction"])

