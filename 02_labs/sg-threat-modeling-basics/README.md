# Lab: 脅威モデリング入門（資産 → 脅威 → 対策）

- **Track:** SG
- **Concept:** → [`01_concepts/sg-threat-modeling-basics.md`](../../01_concepts/sg-threat-modeling-basics.md)
- **Status:** verified
- **Created:** 2026-11-08

## Objective

玩具 CRM 照会 Web の **資産–脅威–対策** 対応が破綻していないことを、実行可能なアサーションで偽と判定できるようにする（攻撃手順は扱わない）。

## Setup

- Prerequisites: Python 3.10+
- Files / tools: `verify.py` only（標準ライブラリのみ）

## How to run

```bash
cd 02_labs/sg-threat-modeling-basics
python3 verify.py
```

Exit code `0` = 対応契約チェック通過。失敗時はアサーションメッセージが「どの結びつけが壊れたか」を示す。

## Task

1. コンセプトカードを読んだあと、**答えを見ずに**言う: 資産を書くとき C/I/A のどれを添えるか／対策行に必ず書く参照は何か。
2. `python3 verify.py` を実行し、全アサーションが通ることを確認する。
3. （任意・スキャフォールド）`verify.py` 末尾の `LEARNER_TODO` を埋め、`python3 verify.py --learner` で再実行する。詰まっても **unlock solution と言うまで** 解答ダンプを足さない（AGENT.md Law 1）。

## Assertions / checks (pass criteria)

- [x] すべての脅威が既知の資産を指す
- [x] 資産の CIA ラベルが C/I/A のみ
- [x] 脅威種別（disclosure / tampering / denial / spoofing）が資産の CIA と粗く整合
- [x] すべての脅威に1つ以上の対策が紐づく
- [x] TLS だけではモデル完了にならない（DoS・なりすましが残る）ことの契約
- [x] レート制限を PII 漏えいの主対策に誤紐づけしない

## Hints (scaffolding — reveal in order)

1. 行を埋める順序は **資産 → 脅威 → 対策**。対策名から逆算しない。
2. 「どの脅威 ID を薄くするか」が書いてない対策は、モデル上は装飾。
3. `LEARNER_TODO` は CIA の主眼と、脅威 ID → 対策 ID の逆引きだけ。

## Solution

> Locked by default. Unlock only after `unlock solution` or repeated failure (AGENT.md Law 1).

<!-- write steps here only when unlocking -->

## Reflection

- What broke my first attempt?
- What would I explain differently tomorrow?
