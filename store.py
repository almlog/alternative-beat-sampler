"""データ保存・読み出しモジュール（store.py）

シーケンスパターン、サウンドパラメータ、サンプラー状態を管理し、
メモリおよびローカルJSONファイルに永続化します。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STORE_FILE = Path(__file__).parent / "state.json"

DEFAULT_STATE: dict[str, Any] = {
    "tempo_bpm": 120,
    "filter_cutoff": 2000.0,
    "pitch": 1.0,
    "volume": 0.8,
    "patterns": {
        "kick":   [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        "snare":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        "hihat":  [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        "sample": [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    },
    "pads": {
        "pad1": {"name": "Kick 808", "type": "synth"},
        "pad2": {"name": "Snare Crack", "type": "synth"},
        "pad3": {"name": "Closed Hat", "type": "synth"},
        "pad4": {"name": "Custom Sample", "type": "custom"},
    },
}

_state: dict[str, Any] = dict(DEFAULT_STATE)


def load_state() -> dict[str, Any]:
    global _state
    if STORE_FILE.is_file():
        try:
            _state = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except Exception:
            _state = dict(DEFAULT_STATE)
    else:
        _state = dict(DEFAULT_STATE)
    return _state


def save_state() -> None:
    try:
        STORE_FILE.write_text(json.dumps(_state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Error saving state: {e}")


def get_state() -> dict[str, Any]:
    if not _state:
        load_state()
    return _state


def update_pattern(track: str, steps: list[int]) -> dict[str, Any]:
    state = get_state()
    if "patterns" not in state:
        state["patterns"] = {}
    state["patterns"][track] = [int(s) for s in steps[:16]]
    save_state()
    return state


def update_parameters(tempo_bpm: int | None = None, filter_cutoff: float | None = None,
                      pitch: float | None = None, volume: float | None = None) -> dict[str, Any]:
    state = get_state()
    if tempo_bpm is not None:
        state["tempo_bpm"] = int(max(40, min(240, tempo_bpm)))
    if filter_cutoff is not None:
        state["filter_cutoff"] = float(max(100.0, min(20000.0, filter_cutoff)))
    if pitch is not None:
        state["pitch"] = float(max(0.2, min(4.0, pitch)))
    if volume is not None:
        state["volume"] = float(max(0.0, min(1.0, volume)))
    save_state()
    return state


def update_all(new_data: dict[str, Any]) -> dict[str, Any]:
    state = get_state()
    state.update(new_data)
    save_state()
    return state


# 初期化時に読み込み
load_state()
