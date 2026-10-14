# alternative-beat-sampler 🎵

> **PO / EP-133 Style Browser Groovebox & AI Co-Producer**  
> 複雑なDAWソフトを使わずに、ブラウザ上で直感的なダイヤルやパッドを使ってオリジナル音楽をスケッチし、AIとの共作で簡単にビートを生み出せるWebサンプラー・シーケンサー。

---

## 🌟 特徴

- **16ステップ・シーケンサー**: Kick, Snare, HiHat, Sample の4トラックを直感的にマトリクス操作
- **Web Audio API による本格サウンドエンジン**:
  - アナログモデリングによるドラム合成（808キック、クラックスネア、ハイハット）
  - ローパスフィルター、ピッチベンド、ボリュームのリアルタイムコントロール
- **サンプラー機能**: マイクからのワンショット録音や音声ファイルのドラッグ＆ドロップで Pad 4 に音色をアサイン
- **AI ビートメイカー共作（Google ADK + Gemini 3.8 Flash）**:
  - 「Lo-Fi HipHopのビートを組んで」「BPM130でフィルターを絞って」など、チャットで指示するとAIがシーケンスやパラメータを自動生成・画面に即時反映！
- **Google標準リッチUI**: Tailwind CSS、Google Fonts（Noto Sans JP, Space Mono）、Material Symbols を導入した洗練されたガジェットUI

---

## 🚀 起動方法

### ローカル起動

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# 環境変数の設定 (.env.example をコピーして GEMINI_API_KEY を設定)
cp .env.example .env
# .env を編集して GEMINI_API_KEY を記入

# サーバ起動
uvicorn main:app --host 0.0.0.0 --port 8080
```

ブラウザで `http://localhost:8080` を開きます。

---

## 🛠️ 技術スタック

- **Backend**: FastAPI, Python 3.12, Uvicorn
- **AI Agent**: Google ADK (Agent Development Kit), Gemini 3.8 Flash
- **Frontend**: HTML5, JavaScript (Web Audio API), Tailwind CSS
- **Deployment**: Google Cloud Run, Secret Manager

---

## 📄 ライセンス

MIT License
