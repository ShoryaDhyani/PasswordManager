import base64
import json
import os
from typing import Any, Dict, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import settings

VAULT_VERSION = 1


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64decode(data: str) -> bytes:
    return base64.b64decode(data.encode("ascii"))


def _aad_for_user(user_id: str) -> bytes:
    return f"vault:{user_id}".encode("utf-8")


def _kms_client():
    return boto3.client("kms", region_name=settings.aws_region)


def _s3_client():
    return boto3.client("s3", region_name=settings.aws_region)


def _vault_object_key(user_id: str) -> str:
    prefix = settings.vault_prefix.strip("/")
    if prefix:
        return f"{prefix}/{user_id}.json"
    return f"{user_id}.json"


def _encrypt_payload(plaintext: bytes, user_id: str) -> Dict[str, Any]:
    kms_client = _kms_client()
    response = kms_client.generate_data_key(KeyId=settings.kms_key_arn, KeySpec="AES_256")
    data_key = response["Plaintext"]
    encrypted_data_key = response["CiphertextBlob"]

    aesgcm = AESGCM(data_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, _aad_for_user(user_id))

    return {
        "version": VAULT_VERSION,
        "key_id": settings.kms_key_arn,
        "encrypted_data_key": _b64encode(encrypted_data_key),
        "nonce": _b64encode(nonce),
        "ciphertext": _b64encode(ciphertext),
    }


def _decrypt_payload(payload: Dict[str, Any], user_id: str) -> bytes:
    if payload.get("version") != VAULT_VERSION:
        raise ValueError("Unsupported vault version")

    encrypted_data_key = _b64decode(payload["encrypted_data_key"])
    nonce = _b64decode(payload["nonce"])
    ciphertext = _b64decode(payload["ciphertext"])

    kms_client = _kms_client()
    response = kms_client.decrypt(CiphertextBlob=encrypted_data_key)
    data_key = response["Plaintext"]

    aesgcm = AESGCM(data_key)
    return aesgcm.decrypt(nonce, ciphertext, _aad_for_user(user_id))


def load_vault(user_id: str) -> Tuple[Dict[str, Any], Optional[str]]:
    s3_client = _s3_client()
    object_key = _vault_object_key(user_id)

    try:
        response = s3_client.get_object(Bucket=settings.s3_bucket, Key=object_key)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code in {"NoSuchKey", "404", "NotFound"}:
            return {}, None
        raise

    raw_payload = response["Body"].read()
    payload = json.loads(raw_payload)
    plaintext = _decrypt_payload(payload, user_id)
    vault = json.loads(plaintext.decode("utf-8"))
    etag = response.get("ETag")
    return vault, etag


def save_vault(user_id: str, vault: Dict[str, Any]) -> Optional[str]:
    s3_client = _s3_client()
    object_key = _vault_object_key(user_id)

    plaintext = json.dumps(vault, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload = _encrypt_payload(plaintext, user_id)
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    response = s3_client.put_object(
        Bucket=settings.s3_bucket,
        Key=object_key,
        Body=body,
        ContentType="application/json",
    )
    return response.get("ETag")
