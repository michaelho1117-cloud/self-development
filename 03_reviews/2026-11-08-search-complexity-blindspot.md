# Review: 二分探索の前提とオーダー取り違え

- **Type:** blindspot
- **Track:** FE
- **Date:** 2026-11-08
- **Concepts covered:** [`01_concepts/fe-algorithms-complexity.md`](../01_concepts/fe-algorithms-complexity.md)

## Prompt set (answer from memory first)

1. 線形探索と二分探索の最悪オーダーを書け。二分の**必須前提**は何か。
2. O(*n*) と O(*n*²) を、ループの形（一重／二重）で一言で区別せよ。
3. 問い合わせが1回だけの未整列データに「ソートしてから二分」は線形より速いか（概念カード Socratic #1）。

## Self-score

| # | Recall (0–2) | Notes |
|---|--------------|-------|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## Blindspots

- Topic: 二分探索の前提（ソート済み）と、ソート費用を無視した「二分＝常に速い」思い込み
  - Missed because: 探索手順だけ見て、前提条件と前処理コストを分離して言語化していなかった（カード作成時に再確認した定番ひっかけ）。
  - Next action: concept refresh — lab の比較回数アサーションを再実行してから、Socratic #1 を口頭で答える

## Stress-test leftovers

空配列とキー不在で、線形／二分がそれぞれどう終了するかを定義から言えるか。

-

## Roadmap follow-up

- [x] Update `00_roadmap/next-topics.md` if priorities changed
- [ ] Commit: `review: …`（本サイクルは `learn(fe): …` に含める）
