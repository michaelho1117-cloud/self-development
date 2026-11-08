#!/usr/bin/env python3
"""Minimal SG lab: asset → threat → control mapping contracts (defensive only).

Run:  python3 verify.py
Opt:  python3 verify.py --learner   # enables TODO checks (fill stubs first)

No exploits, payloads, or attack procedures — classification & linkage only.
"""

from __future__ import annotations

import argparse
import sys
from typing import Literal

Cia = Literal["C", "I", "A"]
ControlRole = Literal["prevent", "reduce", "detect"]


# --- Tiny scenario (toy CRM inquiry web; conceptual only) --------------------

ASSETS: dict[str, dict[str, object]] = {
    "customer_pii": {
        "label": "顧客 PII（氏名・連絡先）",
        "cia": ("C",),
    },
    "order_records": {
        "label": "注文履歴",
        "cia": ("I", "C"),
    },
    "inquiry_api": {
        "label": "照会 API の稼働",
        "cia": ("A",),
    },
    "admin_console_auth": {
        "label": "管理者コンソールの認証セッション",
        "cia": ("C", "I"),
    },
}

# threat_id → {asset, kind, summary}
THREATS: dict[str, dict[str, str]] = {
    "T1": {
        "asset": "customer_pii",
        "kind": "disclosure",
        "summary": "照会結果の過剰取得による顧客 PII 漏えい",
    },
    "T2": {
        "asset": "order_records",
        "kind": "tampering",
        "summary": "権限不足チェック欠落による注文履歴の改ざん",
    },
    "T3": {
        "asset": "inquiry_api",
        "kind": "denial",
        "summary": "大量リクエストによる照会 API の停止",
    },
    "T4": {
        "asset": "admin_console_auth",
        "kind": "spoofing",
        "summary": "盗用クレデンシャルによる管理者なりすまし",
    },
}

# control_id → {threats: tuple, role, summary}
CONTROLS: dict[str, dict[str, object]] = {
    "C1": {
        "threats": ("T1",),
        "role": "prevent",
        "summary": "最小権限の認可＋応答フィールドの最小化",
    },
    "C2": {
        "threats": ("T2",),
        "role": "prevent",
        "summary": "更新 API の認可と監査用変更ログ",
    },
    "C3": {
        "threats": ("T3",),
        "role": "reduce",
        "summary": "レート制限と過負荷時の縮退応答",
    },
    "C4": {
        "threats": ("T4",),
        "role": "prevent",
        "summary": "管理者 MFA ＋管理面の到達経路制限",
    },
    "C5": {
        "threats": ("T4",),
        "role": "detect",
        "summary": "管理者ログイン失敗・異常時間帯の検知アラート",
    },
}


# --- Contract checks ----------------------------------------------------------


def check_every_threat_names_known_asset() -> None:
    for tid, threat in THREATS.items():
        asset = threat["asset"]
        assert asset in ASSETS, f"{tid}: asset {asset!r} must exist in ASSETS"


def check_cia_labels_are_valid() -> None:
    allowed = {"C", "I", "A"}
    for aid, meta in ASSETS.items():
        cia = meta["cia"]
        assert isinstance(cia, tuple) and cia, f"{aid}: cia must be non-empty tuple"
        assert set(cia) <= allowed, f"{aid}: cia labels must be C/I/A only"


def check_threat_kinds_match_asset_cia() -> None:
    """Coarse sanity: disclosure↔C, tampering↔I, denial↔A, spoofing↔auth assets."""
    kind_needs: dict[str, set[str]] = {
        "disclosure": {"C"},
        "tampering": {"I"},
        "denial": {"A"},
        "spoofing": {"C", "I"},  # session/auth integrity + confidentiality of creds
    }
    for tid, threat in THREATS.items():
        kind = threat["kind"]
        assert kind in kind_needs, f"{tid}: unknown kind {kind!r}"
        asset_cia = set(ASSETS[threat["asset"]]["cia"])  # type: ignore[arg-type]
        needed = kind_needs[kind]
        assert asset_cia & needed, (
            f"{tid}: kind {kind!r} does not align with asset CIA {sorted(asset_cia)}"
        )


def check_every_threat_has_at_least_one_control() -> None:
    covered: set[str] = set()
    for control in CONTROLS.values():
        covered.update(control["threats"])  # type: ignore[arg-type]
    missing = set(THREATS) - covered
    assert not missing, f"threats without controls: {sorted(missing)}"


def check_controls_reference_real_threats_and_roles() -> None:
    allowed_roles = {"prevent", "reduce", "detect"}
    for cid, control in CONTROLS.items():
        role = control["role"]
        assert role in allowed_roles, f"{cid}: role must be prevent|reduce|detect"
        threats = control["threats"]
        assert isinstance(threats, tuple) and threats, f"{cid}: threats must be non-empty"
        for tid in threats:
            assert tid in THREATS, f"{cid}: unknown threat {tid!r}"


def check_tls_alone_is_not_a_complete_model() -> None:
    """Conceptual trap from the card: TLS is not a full threat model."""
    # TLS mainly helps disclosure / tampering on the wire — not DoS, not authz gaps.
    tls_covers = {"disclosure_in_transit", "tampering_in_transit"}
    scenario_threat_kinds = {t["kind"] for t in THREATS.values()}
    # Our toy model includes denial + spoofing; TLS alone cannot claim completion.
    assert "denial" in scenario_threat_kinds, "fixture must include a DoS-class threat"
    assert "spoofing" in scenario_threat_kinds, "fixture must include a spoofing threat"
    assert "denial" not in tls_covers
    assert "spoofing" not in tls_covers


def check_bad_linkage_is_rejected() -> None:
    """Falsify misunderstanding: rate-limit is not the primary control for PII disclosure."""
    pii_threats = {tid for tid, t in THREATS.items() if t["asset"] == "customer_pii"}
    rate_limit_controls = {
        cid for cid, c in CONTROLS.items() if "レート制限" in str(c["summary"])
    }
    for cid in rate_limit_controls:
        linked = set(CONTROLS[cid]["threats"])  # type: ignore[arg-type]
        assert linked.isdisjoint(pii_threats), (
            f"{cid}: rate limiting must not be the mapped control for PII disclosure"
        )


# --- LEARNER_TODO (scaffolding; optional) ------------------------------------
# Fill these only when practicing recall. Default run does not call them.
# Do not ask the tutor for an unlock dump until you have attempted twice.


def primary_cia_for_asset(asset_id: str) -> str:
    """Return the single most characteristic CIA letter for the asset_id.

    TODO: implement from the concept card / ASSETS map (delete the raise when ready).
    Hint: customer_pii → C, inquiry_api → A, order_records → I (改ざんが主眼のとき).
    """
    raise NotImplementedError("learner TODO: map asset_id → primary C|I|A")


def control_ids_for_threat(threat_id: str) -> set[str]:
    """Return control ids that list threat_id in their threats tuple.

    TODO: implement by scanning CONTROLS (delete the raise when ready).
    """
    raise NotImplementedError("learner TODO: find controls linked to a threat")


def learner_checks() -> None:
    expected_cia = {
        "customer_pii": "C",
        "inquiry_api": "A",
        "order_records": "I",
        "admin_console_auth": "C",  # セッション/資格情報の機密を主眼
    }
    for asset_id, letter in expected_cia.items():
        got = primary_cia_for_asset(asset_id)
        assert got == letter, f"cia {asset_id!r}: expected {letter!r}, got {got!r}"

    assert control_ids_for_threat("T3") == {"C3"}, "T3 should map to rate-limit control"
    assert control_ids_for_threat("T4") == {"C4", "C5"}, "T4 needs prevent + detect"
    assert control_ids_for_threat("T1") == {"C1"}, "T1 maps to least-privilege / minimize"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--learner",
        action="store_true",
        help="also run LEARNER_TODO checks (fill stubs first)",
    )
    args = parser.parse_args()

    check_every_threat_names_known_asset()
    check_cia_labels_are_valid()
    check_threat_kinds_match_asset_cia()
    check_every_threat_has_at_least_one_control()
    check_controls_reference_real_threats_and_roles()
    check_tls_alone_is_not_a_complete_model()
    check_bad_linkage_is_rejected()
    print("OK: asset→threat→control mapping contracts hold (defensive checklist)")

    if args.learner:
        try:
            learner_checks()
        except NotImplementedError as exc:
            print(f"LEARNER_TODO incomplete: {exc}", file=sys.stderr)
            return 2
        print("OK: learner CIA / linkage mapping")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
