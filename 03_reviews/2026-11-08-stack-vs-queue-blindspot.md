# Review: スタック vs キューの取り違え

- **Type:** blindspot
- **Track:** FE
- **Date:** 2026-11-08
- **Concepts covered:** [`01_concepts/fe-data-structures-basics.md`](../01_concepts/fe-data-structures-basics.md)

## Prompt set (answer from memory first)

1. LIFO / FIFO を日本語と操作名（push・pop / enqueue・dequeue）で対応づけよ。
2. 「戻り」が必要な処理と「到着順を守る」処理を一つずつ挙げ、使う構造を言え。
3. 空のときに pop / dequeue したら仕様上どう扱うべきか（概念カードの Socratic #2）。

## Self-score

| # | Recall (0–2) | Notes |
|---|--------------|-------|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## Blindspots

- Topic: スタックとキューの端の数・順序契約
  - Missed because: 両方を「並び」としか見ておらず、入口／出口の非対称を言語化していなかった（カード作成時に再確認した定番ひっかけ）。
  - Next action: concept refresh — lab の LIFO/FIFO アサーションを先に再実行してから口頭説明

## Stress-test leftovers

Why-not-X（戻る履歴を FIFO にすると壊れる理由）を、具体的なページ列で言えるか。

-

## Roadmap follow-up

- [x] Update `00_roadmap/next-topics.md` if priorities changed
- [ ] Commit: `review: …`（本サイクルは `learn(fe): …` に含める）
