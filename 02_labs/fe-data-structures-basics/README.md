# Lab: データ構造の基礎（配列 / リスト / スタック / キュー）

- **Track:** FE
- **Concept:** → [`01_concepts/fe-data-structures-basics.md`](../../01_concepts/fe-data-structures-basics.md)
- **Status:** verified
- **Created:** 2026-11-08

## Objective

配列アクセス・スタック LIFO・キュー FIFO の契約を、実行可能なアサーションで偽と判定できるようにする（誤解があれば `verify.py` が落ちる）。

## Setup

- Prerequisites: Python 3.10+
- Files / tools: `verify.py` only（標準ライブラリのみ）

## How to run

```bash
cd 02_labs/fe-data-structures-basics
python3 verify.py
```

Exit code `0` = 契約チェック通過。失敗時はアサーションメッセージが「どの契約が壊れたか」を示す。

## Task

1. コンセプトカードを読んだあと、**答えを見ずに**次を口頭で言う: スタックの出し入れ端はいくつか／キューはいくつか。
2. `python3 verify.py` を実行し、全アサーションが通ることを確認する。
3. （任意・スキャフォールド）`verify.py` 末尾の `LEARNER_TODO` ブロックを開き、コメントの指示どおりに小さな関数を埋めてから再実行する。詰まっても **unlock solution と言うまで** README / カードに解答ダンプを足さない（AGENT.md Law 1）。

## Assertions / checks (pass criteria)

- [x] 配列: 既知添字の読みが期待値と一致
- [x] スタック: 後から入れた値が先に出る（LIFO）
- [x] キュー: 先に入れた値が先に出る（FIFO）
- [x] 空構造への不正操作が明示的に失敗する（契約の端）

## Hints (scaffolding — reveal in order)

1. スタックは「片方の端だけ」。キューは「入れる端」と「出す端」が別。
2. アサーションが落ちたら、期待シーケンスを紙に `in → … → out` で書いてからコードを見る。
3. `LEARNER_TODO` は「どの ADT か」を選ぶ問題。操作列の入出力だけ見れば構造が決まる。

## Solution

> Locked by default. Unlock only after `unlock solution` or repeated failure (AGENT.md Law 1).

<!-- write steps here only when unlocking -->

## Reflection

- What broke my first attempt?
- What would I explain differently tomorrow?
