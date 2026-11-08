# Review: 対策先行と TLS 完了幻想

- **Type:** blindspot
- **Track:** SG
- **Date:** 2026-11-08
- **Concepts covered:** [`01_concepts/sg-threat-modeling-basics.md`](../01_concepts/sg-threat-modeling-basics.md)

## Prompt set (answer from memory first)

1. 脅威モデルの最小3列を書け。対策行に必ず添えるべき参照は何か。
2. 「顧客 DB」を資産として書くとき、C/I/A でどう分解するか（例を1つ）。
3. 「全 API を TLS にした」だけでモデル完了と言えるか。抑える脅威と残る脅威を挙げよ（概念カード Socratic #1）。

## Self-score

| # | Recall (0–2) | Notes |
|---|--------------|-------|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## Blindspots

- Topic: 対策名・プロトコル名から書き始め、資産の壊れ方（C/I/A）と脅威行への紐づけを飛ばす
  - Missed because: 実装者視点だと「入れる技術」が先に浮かび、守る対象の言語化が後回しになりやすい（カード作成時の定番ひっかけ）。
  - Next action: concept refresh — lab の mapping アサーションを再実行してから、Socratic #1 を口頭で答える

## Stress-test leftovers

公開静的サイトだけの範囲で、顧客 PII システムと同じ対策チェックリストをそのまま適用すべきか（概念カード Socratic #2）。

-

## Roadmap follow-up

- [x] Update `00_roadmap/next-topics.md` if priorities changed
- [ ] Commit: `review: …`（本サイクルは `learn(sg): …` に含める）
