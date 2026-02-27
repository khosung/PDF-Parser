| 서비스·분류 | API·명칭 | 동작·내용 | 입력 | 출력 |
| --- | --- | --- | --- | --- |
|  | KISA_Crypto_genKeyPair(); | 키쌍·생성 | 키·길이· |  |
|  | KISA_Crypto_publicEncrypt(); | 공개키·암호· 암호화 | 평문,· 공개키·파라미터 |  |
|  | KISA_Crypto_privateDecrypt(); | 공개키·암호· 복호화 | 암호문,· 개인키·파라미터 |  |
|  | KISA_Crypto_genKeyPair(); | 키쌍·생성 | 키·길이· |  |
|  | KISA_Crypto_privateSign(); | 서명키로·서명·생성 | 메시지,·개인키· 파라미터 |  |
|  | KISA_Crypto_publicVerify(); | 검증키로·서명·검증 | 서명,·메시지,· 공개키·파라미터 |  |
|  | KISA_Crypto_DH_ genParameter(); | 도메인·변수·생성 | 키길이 |  |
|  | KISA_Crypto_DH_ genKeyPair(); | 키쌍·생성 | 도메인·파라미터 |  |
|  | KISA_Crypto_DH_ computeSharedSecret(); | 키·설정 | 도메인,·개인키·및· 공개키·파라미터 |  |