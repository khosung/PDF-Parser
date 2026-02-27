| 서비스·분류 | API·명칭 | 목적/기능 | 입력 | 출력 | 인가된·역할 |
| --- | --- | --- | --- | --- | --- |
|  | KISA_Crypto_hmacInit(); KISA_Crypto_hmacUpdate(); KISA_Crypto_hmacFinal(); KISA_Crypto_hmac(); | HMAC·연산· 수행 | HMAC·설정· 정보,·메시지,· MAC·키 | HMAC값, 오류코드 |  |
|  | KISA_Crypto_drbgInit(); KISA_Crypto_drbgReseed(); KISA_Crypto_drbgGenerate(); KISA_Crypto_drbgClose(); KISA_Crypto_drbgRand(); | 난수·생성 | 난수발생기 설정·정보, 엔트로피,· 난수출력·길이 | 난수비트열, 오류코드 |  |
|  | KISA_Crypto_genKeyPair(); | 키쌍·생성 | 키·길이· | 공개키·및· 개인키· 파라미터 |  |
|  | KISA_Crypto_publicEncrypt(); | 공개키·암호· 암호화 | 평문,·공개키· 파라미터 | 암호문 |  |
|  | KISA_Crypto_privateDecrypt(); | 공개키·암호· 복호화 | 암호문,· 개인키· 파라미터 | 평문 |  |
|  | KISA_Crypto_genKeyPair(); | 키쌍·생성 | 키·길이· | 공개키·및· 개인키· 파라미터 |  |
|  | KISA_Crypto_privateSign(); | 서명키로· 서명·생성 | 메시지,·개인키 파라미터 | · 서명 |  |
|  | KISA_Crypto_publicVerify(); | 검증키로· 서명·검증 | 서명,·메시지,· 공개키· 파라미터 | 오류코드 |  |
|  | KISA_Crypto_DH_genParameter(); | 도메인·변수· 생성 | 키길이 | 도메인· 파라미터, 오류코드 |  |
|  | KISA_Crypto_genKeyPair(); | 키쌍·생성 | 키길이 | 공개키·및· 개인키· 파라미터,· 오류코드 |  |
|  | KISA_Crypto_compute_Key(); | 키·설정 | 도메인,·개인키 및·공개키· 파라미터 | · 공유키, 오류코드 |  |