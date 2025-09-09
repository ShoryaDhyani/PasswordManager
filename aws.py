# aws.py

import boto3
import json
import os
import base64
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import enc_dec as encob

class AWSStorage:
    def __init__(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.region       = config['AWS']['region']
        self.bucket_name  = config['AWS']['bucket_name']
        self.user_pool_id = config['COGNITO']['user_pool_id']
        self.client_id    = config['COGNITO']['client_id']
        self.kms_key_id   = config['KMS']['key_id']
        self.s3           = boto3.client('s3', region_name=self.region)
        self.cognito      = boto3.client('cognito-idp', region_name=self.region)
        self.kms          = boto3.client('kms', region_name=self.region)
        self.current_user = None

    # ─── Envelope Encryption Helpers ─────────────────────────

    def _generate_data_key(self, user_id):
        """Generate a one-time data key bound to user_id."""
        resp = self.kms.generate_data_key(
            KeyId=self.kms_key_id,
            KeySpec='AES_256',
            EncryptionContext={'user_id': user_id}
        )
        # plaintext bytes for local AES, ciphertext to store
        return resp['Plaintext'], resp['CiphertextBlob']

    def _encrypt_blob(self, plaintext_bytes, data_key_plain):
        aesgcm = AESGCM(data_key_plain)
        nonce  = os.urandom(12)
        ct     = aesgcm.encrypt(nonce, plaintext_bytes, None)
        return nonce, ct

    def _decrypt_blob(self, nonce, ciphertext, user_id, encrypted_data_key):
        # recover the DEK
        resp = self.kms.decrypt(
            CiphertextBlob=encrypted_data_key,
            EncryptionContext={'user_id': user_id}
        )
        data_key = resp['Plaintext']
        aesgcm   = AESGCM(data_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    # ─── Public Storage Methods ─────────────────────────────

    def get_user_data_key(self, username):
        return f"users/{username}/data.json"

    # def save_user_data(self, username, data: dict, password: str):
    #     key = self.get_user_data_key(username)
    #     # raw = json.dumps(data).encode()
    #     # encob.AESEncryptor()  # Ensure AESEncryptor is initialized
    #     # Envelope encrypt
    #     # dk_plain, dk_encrypted = self._generate_data_key(username)
    #     # nonce, ct = self._encrypt_blob(raw, dk_plain)
    #     encrypted_data = encob.AESEncryptor().encrypt(data, password)

    #     # package everything into a JSON object
    #     # payload = {
    #     #     'encrypted_key': base64.b64encode(dk_encrypted).decode(),
    #     #     'nonce'        : base64.b64encode(nonce).decode(),
    #     #     'ciphertext'   : base64.b64encode(ct).decode()
    #     # }

    #     self.s3.put_object(
    #         Bucket=self.bucket_name,
    #         Key=key,
    #         Body=json.dumps(encrypted_data).encode()
    #     )
    #     return True
    
    def save_user_data(self, username, data: dict, password: str):
        key = self.get_user_data_key(username)
        # Convert data to JSON string before encryption
        json_data = json.dumps(data)
        encrypted_data = encob.AESEncryptor().encrypt(json_data, password)

        # Store directly without extra JSON encoding
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=encrypted_data.encode('utf-8')  # Directly store encrypted string
        )
        return True
    def load_user_data(self, username, password):
        key = self.get_user_data_key(username)
        try:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            encrypted_str = obj['Body'].read().decode('utf-8')

            # Decrypt and parse JSON
            decrypted = encob.AESEncryptor().decrypt(encrypted_str, password)
            return json.loads(decrypted)

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise


    # def load_user_data(self, username, password):
    #     key = self.get_user_data_key(username)
    #     try:
    #         obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
    #     except ClientError as e:
    #         if e.response['Error']['Code']=='NoSuchKey':
    #             return None
    #         raise

    #     # payload = json.loads(obj['Body'].read())
    #     # ek = base64.b64decode(payload['encrypted_key'])
    #     # nonce = base64.b64decode(payload['nonce'])
    #     # ct    = base64.b64decode(payload['ciphertext'])
    #     plain=encob.AESEncryptor().decrypt(obj['Body'].read().decode(), password)
    #     try:
    #         # plain = self._decrypt_blob(nonce, ct, username, ek)
    #         return json.loads(plain.decode())
    #     except ClientError:
    #         # wrong user_id / context will fail here
    #         return None

    # ─── Cognito & Misc Remain Unchanged ────────────────────

    def sign_up(self, username, password, email):
        resp = self.cognito.sign_up(
            ClientId=self.client_id,
            Username=username,
            Password=password,
            UserAttributes=[{'Name':'email','Value':email}]
        )
        return resp

    def confirm_sign_up(self, username, code):
        self.cognito.confirm_sign_up(
            ClientId=self.client_id,
            Username=username,
            ConfirmationCode=code
        )
        return True

    def login(self, username, password):
        resp = self.cognito.initiate_auth(
            ClientId=self.client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME':username,'PASSWORD':password}
        )
        self.current_user = username  # Store current user
        return resp['AuthenticationResult']
    

    def verify_password(self, password):
        if not self.current_user:
            raise Exception("No user is currently logged in.")

        try:
            self.cognito.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': self.current_user,
                    'PASSWORD': password
                }
            )
            return True  # Password is correct
        except ClientError as e:
            code = e.response['Error']['Code']
            if code in ['NotAuthorizedException', 'UserNotFoundException']:
                return False
            raise




    def test(self):
        user_data = {
            "username": "testuser",
            "password": "demo"
        }
        self.save_user_data(user_data['username'], user_data)
        print("User data saved successfully.")
        print("Loading user data...")
        loaded_data = self.load_user_data(user_data['username'])
        if loaded_data:
            print("User data loaded successfully:", loaded_data)    
        else:
            print("No user data found or decryption failed.")
if __name__ == "__main__":
    aws = AWSStorage()
    aws.test()