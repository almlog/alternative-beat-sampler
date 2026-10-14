"""AIエージェント定義（agent.py）
Google ADK (Agent Development Kit) を用いた直感的グルーヴボックス・ビートメイカーエージェント。
"""

from __future__ import annotations

import json
import credentials
credentials.configure()

from google.adk.agents import Agent
import store

MODEL = "gemini-3.8-flash"


def generate_beat_pattern(genre: str, mood: str = "normal", target_track: str = "all") -> str:
    """指定されたジャンルや雰囲気、対象トラックに応じた16ステップシーケンスパターンとBPMを生成する。

    ユーザーからビート作成、ドラムパターン提案、リズムの変更、ジャンルに合わせたパターン生成の要望があった際に必ず呼び出す。

    Args:
        genre: 音楽ジャンル（例: 'Lo-Fi HipHop', 'House', 'Techno', 'Funk', 'Rock' 等）
        mood: 楽曲の雰囲気（例: 'relaxed', 'chill', 'aggressive', 'dark', 'bright' 等）
        target_track: 対象トラック（'all', 'kick', 'snare', 'hihat', 'sample' 等）

    Returns:
        生成された16ステップシーケンス情報、適用されたBPM、音楽的解説を含むJSON文字列。
    """
    genre_lower = (genre or "").lower()
    mood_lower = (mood or "").lower()
    track_lower = (target_track or "all").lower()

    # ジャンル・雰囲気に合わせたパターンとBPM設計
    if "lo-fi" in genre_lower or "lofi" in genre_lower or "chill" in mood_lower:
        bpm = 82
        cutoff = 1200.0
        patterns = {
            "kick":   [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "snare":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hihat":  [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0],
            "sample": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        }
        comment = f"{genre}（{mood}）向けに、レイドバックした少しヨレのあるグルーヴと落ち着いたテンポ（BPM {bpm}）を生成しました。"
    elif "house" in genre_lower or "four on the floor" in genre_lower:
        bpm = 124
        cutoff = 3500.0
        patterns = {
            "kick":   [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            "snare":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hihat":  [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            "sample": [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        }
        comment = f"{genre}向けの王道4つ打ちキックと裏拍オープンハイハット、推進力あるグルーヴ（BPM {bpm}）を生成しました。"
    elif "techno" in genre_lower:
        bpm = 132
        cutoff = 2800.0
        patterns = {
            "kick":   [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            "snare":  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            "hihat":  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "sample": [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
        }
        comment = f"{genre}向けの無機質で力強いミニマルビート（BPM {bpm}）を生成しました。"
    elif "funk" in genre_lower:
        bpm = 105
        cutoff = 4000.0
        patterns = {
            "kick":   [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            "snare":  [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
            "hihat":  [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
            "sample": [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        }
        comment = f"{genre}向けのハネたシンコペーション満載のファンキーなビート（BPM {bpm}）を生成しました。"
    else:
        # デフォルト汎用パターン（入力ハッシュに応じて適度に変更）
        hash_val = sum(ord(c) for c in (genre + mood))
        bpm = 90 + (hash_val % 40)
        cutoff = 2000.0 + (hash_val % 1000)
        patterns = {
            "kick":   [1, 0, 0, 0, (hash_val % 2), 0, 1, 0, 0, 0, 0, 0, 1, 0, (hash_val % 3 == 0), 0],
            "snare":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hihat":  [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "sample": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        }
        comment = f"{genre}（{mood}）に合わせたオリジナルパターン（BPM {bpm}）を生成しました。"

    # store への反映
    if track_lower == "all":
        for trk, stps in patterns.items():
            store.update_pattern(trk, stps)
    elif track_lower in patterns:
        store.update_pattern(track_lower, patterns[track_lower])

    store.update_parameters(tempo_bpm=bpm, filter_cutoff=cutoff)

    result_data = {
        "status": "success",
        "genre": genre,
        "mood": mood,
        "applied_bpm": bpm,
        "applied_filter": cutoff,
        "patterns": patterns if track_lower == "all" else {track_lower: patterns.get(track_lower)},
        "comment": comment,
    }
    return json.dumps(result_data, ensure_ascii=False)


def adjust_sound_parameters(tempo_bpm: int = 120, filter_cutoff: float = 2000.0) -> str:
    """テンポ（BPM）やフィルターカットオフ等の音響パラメータを設定する。

    ユーザーからテンポの変更、アップテンポ/スローテンポ化、フィルターの調整（こもらせる/明るくする等）の指示があった際に必ず呼び出す。

    Args:
        tempo_bpm: 再生速度テンポ（BPM: 40〜240）
        filter_cutoff: ローパスフィルターのカットオフ周波数（Hz: 100〜20000。低いとこもった音、高いと抜けの良い明るい音）

    Returns:
        更新された音響パラメータと解説を含むJSON文字列。
    """
    updated_state = store.update_parameters(tempo_bpm=tempo_bpm, filter_cutoff=filter_cutoff)

    desc = []
    if filter_cutoff <= 800:
        desc.append(f"ローパスフィルターを {filter_cutoff:.1f}Hz に絞り、温かみのあるこもったローファイサウンドに設定しました。")
    elif filter_cutoff >= 5000:
        desc.append(f"ローパスフィルターを {filter_cutoff:.1f}Hz に開き、高域の抜けの良いクリスプなサウンドに設定しました。")
    else:
        desc.append(f"フィルターカットオフを {filter_cutoff:.1f}Hz に調整しました。")

    desc.append(f"テンポを BPM {tempo_bpm} に設定しました。")

    res = {
        "status": "success",
        "tempo_bpm": updated_state.get("tempo_bpm", tempo_bpm),
        "filter_cutoff": updated_state.get("filter_cutoff", filter_cutoff),
        "description": " ".join(desc),
    }
    return json.dumps(res, ensure_ascii=False)


def execute_task(action: str, params: str = "") -> str:
    """音楽制作およびシーケンサー・サンプラー操作タスクを実行する汎用ツール。"""
    action_lower = action.lower()
    if "pattern" in action_lower or "beat" in action_lower or "generate" in action_lower:
        return generate_beat_pattern(genre=params or "Lo-Fi", mood="cool", target_track="all")
    elif "param" in action_lower or "tempo" in action_lower or "filter" in action_lower:
        return adjust_sound_parameters(tempo_bpm=120, filter_cutoff=1500.0)
    else:
        curr = store.get_state()
        return json.dumps({"status": "executed", "action": action, "current_tempo": curr.get("tempo_bpm")}, ensure_ascii=False)


INSTRUCTION = """あなたはブラウザベースのグルーヴボックス・サンプラー「alternative-beat-sampler」専属のAIビートメイカー＆共作パートナーです。
teenage engineering の PO-133 / EP-133 のような直感的でクリエイティブな音楽制作をサポートします。

【行動指針】
1. ユーザーからジャンル（Lo-Fi HipHop, House, Techno, Funk等）や雰囲気に合ったビート・ドラムパターンの提案や作成を求められた場合は、必ず `generate_beat_pattern` ツールを呼び出してください。
2. ユーザーからテンポ（BPM）の変更や、フィルターカットオフ（こもらせる、ハイカットする、明るくする等）などの音響パラメータ調整を求められた場合は、必ず `adjust_sound_parameters` ツールを呼び出してください。
3. ツールの実行結果をもとに、ビートのポイントや音楽的なアドバイスを添えて、フレンドリーで熱量のある日本語で回答してください。
"""

root_agent = Agent(
    model=MODEL,
    name="alternative_beat_sampler",
    description="ブラウザベースのグルーヴボックス・サンプラー用AIビートメイカー。パターンの自動生成や音響パラメータの調整を行う。",
    instruction=INSTRUCTION,
    tools=[generate_beat_pattern, adjust_sound_parameters, execute_task],
)
