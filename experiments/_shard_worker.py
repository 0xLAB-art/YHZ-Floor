
import hashlib, importlib.util, json, os, sys
from pathlib import Path
HERE = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
reg = json.loads((HERE / "_REGISTRATION.json").read_text())
ADAPTER = ROOT / reg["adapter"]
assert hashlib.sha256(ADAPTER.read_bytes()).hexdigest() == reg["adapter_sha256"]
os.environ["AGENTROUTER_LABEL_MODEL"] = reg["label"]
os.environ["APINEX_LABEL_MODEL"] = reg["label"]  # APINEX-routed cohorts (kimi-k3 labels) read this one
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "failure_log.jsonl"))
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
inj = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = inj
spec.loader.exec_module(inj)
sys.path.insert(0, str(ROOT))
spec2 = importlib.util.spec_from_file_location("base_runner", str(ROOT / reg["runner_path"]))
base = importlib.util.module_from_spec(spec2)
sys.modules["base_runner"] = base
spec2.loader.exec_module(base)
assert base.ClaudeProvider is inj.ClaudeProvider, "frozen runner did not bind injected adapter"
base.OUT = HERE
base.PROTOCOL = reg["protocol"]
base.SEEDS = tuple(int(s) for s in reg["seeds"])
# resume: skip seeds whose every cell is already judged in THIS shard
_rp = HERE / "results.jsonl"
if _rp.exists():
    _recorded = {}
    for _line in _rp.read_text().splitlines():
        if _line.strip():
            _rec = json.loads(_line)
            _recorded.setdefault(_rec["seed"], set()).add(_rec["cell"])
    _complete = {s for s, cells in _recorded.items() if cells >= set(base.CELLS)}
    if _complete:
        base.SEEDS = tuple(s for s in base.SEEDS if s not in _complete)
base.main()
