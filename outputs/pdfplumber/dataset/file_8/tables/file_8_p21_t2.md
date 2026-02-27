| 서비스·분류 | API·명칭 | 동작·내용 | 입력 | 출력 |
| --- | --- | --- | --- | --- |
|  | KISA_Crypto_initialize() | 암호모듈 초기화 | - |  |
|  | KISA_Crypto_getState() | 암호모듈·현재· 상태확인 | - |  |
|  | KISA_Crypto_getVersion() | 암호모듈·이름·및·· 버전·확인 | - |  |
|  | KISA_Crypto_selftest() | (주기적)·자가시험 (암호·알고리즘·시험,· 소프트웨어·무결성· 시험) | - |  |
|  | KISA_Crypto_encryptInit(); KISA_Crypto_encryptUpdate(); KISA_Crypto_encryptFinal(); KISA_Crypto_encrypt(); | 블록암호· 암호화 | 블록암호· 설정정보, 평문,·키,·IV |  |
|  | KISA_Crypto_decryptInit(); KISA_Crypto_decryptUpdate(); KISA_Crypto_decryptFinal(); KISA_Crypto_decrypt(); | 블록암호 복호화 | 블록암호·설정정보, 암호문,·키,·IV |  |
|  | KISA_Crypto_hashInit(); KISA_Crypto_hashUpdate(); KISA_Crypto_hashFinal(); KISA_Crypto_hash(); | 해시함수· 수행 | 해시함수·설정정보, 메시지 |  |
|  | KISA_Crypto_hmacInit(); KISA_Crypto_hmacUpdate(); KISA_Crypto_hmacFinal(); KISA_Crypto_hmac(); | HMAC·연산·수행 | HMAC·설정정보,· 메시지,·MAC·키 |  |
|  | KISA_Crypto_drbgInit(); KISA_Crypto_drbgReseed(); KISA_Crypto_drbgGenerate(); KISA_Crypto_drbgClose(); KISA_Crypto_drbgRand(); | 난수·생성 | 난수발생기 설정정보, 엔트로피,· 난수출력길이 |  |