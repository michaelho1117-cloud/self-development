# Lab: アルゴリズムと計算量の直感（探索・整列）

- **Track:** FE
- **Concept:** → [`01_concepts/fe-algorithms-complexity.md`](../../01_concepts/fe-algorithms-complexity.md)
- **Status:** verified
- **Created:** 2026-11-08

## Objective

線形探索と二分探索の契約（正しさ・比較回数の差・空／1件）と、FE 用オーダー階の大小関係を、実行可能なアサーションで偽と判定できるようにする。

## Setup

- Prerequisites: Python 3.10+
- Files / tools: `verify.py` only（標準ライブラリのみ）

## How to run

```bash
cd 02_labs/fe-algorithms-complexity
python3 verify.py
```

Exit code `0` = 契約チェック通過。失敗時はアサーションメッセージが「どの直感が壊れたか」を示す。

## Task

1. コンセプトカードを読んだあと、**答えを見ずに**言う: 二分探索の前提条件は何か／線形探索の最悪オーダーは何か。
2. `python3 verify.py` を実行し、全アサーションが通ることを確認する。
3. （任意・スキャフォールド）`verify.py` 末尾の `LEARNER_TODO` を埋め、`python3 verify.py --learner` で再実行する。詰まっても **unlock solution と言うまで** 解答ダンプを足さない（AGENT.md Law 1）。

## Assertions / checks (pass criteria)

- [x] 線形探索: 未整列でも発見でき、ミス時は全件スキャン相当
- [x] 二分探索: 整列済みで正しく、同条件の線形より比較が少ない
- [x] 空配列・要素1のヒット／ミスが定義どおり
- [x] O(1) < O(log n) < O(n) < O(n log n) < O(n²) の階の大小

## Hints (scaffolding — reveal in order)

1. 二分は「中央を見て半分捨てる」。捨ててよい根拠はソート済み。
2. 比較回数が期待と違うときは、紙に `lo / mid / hi` を数ステップ書いてからコードを見る。
3. `LEARNER_TODO` は「成長の階」と「線形か二分か」の対応づけ。シナリオの前提（整列済みか／何回探すか）だけ見れば足りる。

## Solution

> Locked by default. Unlock only after `unlock solution` or repeated failure (AGENT.md Law 1).

<!-- write steps here only when unlocking -->

## Reflection

- What broke my first attempt?
- What would I explain differently tomorrow?
