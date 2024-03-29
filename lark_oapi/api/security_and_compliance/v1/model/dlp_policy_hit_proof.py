# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .dlp_detect_mode_proof_context import DlpDetectModeProofContext


class DlpPolicyHitProof(object):
    _types = {
        "policy_id": int,
        "detect_mode_proof_contexts": List[DlpDetectModeProofContext],
    }

    def __init__(self, d=None):
        self.policy_id: Optional[int] = None
        self.detect_mode_proof_contexts: Optional[List[DlpDetectModeProofContext]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DlpPolicyHitProofBuilder":
        return DlpPolicyHitProofBuilder()


class DlpPolicyHitProofBuilder(object):
    def __init__(self) -> None:
        self._dlp_policy_hit_proof = DlpPolicyHitProof()

    def policy_id(self, policy_id: int) -> "DlpPolicyHitProofBuilder":
        self._dlp_policy_hit_proof.policy_id = policy_id
        return self

    def detect_mode_proof_contexts(self, detect_mode_proof_contexts: List[
        DlpDetectModeProofContext]) -> "DlpPolicyHitProofBuilder":
        self._dlp_policy_hit_proof.detect_mode_proof_contexts = detect_mode_proof_contexts
        return self

    def build(self) -> "DlpPolicyHitProof":
        return self._dlp_policy_hit_proof
