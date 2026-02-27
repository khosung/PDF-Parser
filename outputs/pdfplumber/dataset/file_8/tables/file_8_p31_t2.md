| 서비스·분류 | API·명칭 | 목적/기능 | 입력 | 출력 | 인가된·역할 |
| --- | --- | --- | --- | --- | --- |
|  | KISA_Crypto_initialize() | 암호모듈 초기화 | - | 오류코드 (성공/실패) |  |
|  | KISA_Crypto_getState() | 암호모듈· 현재· 상태·확인 | - | 암호모듈 상태값 |  |
|  | KISA_Crypto_getVersion() | 암호모듈·이름· 및·버전·확인 | - | 암호모듈 버전값 |  |
|  | KISA_Crypto_selftest() | (주기적) 자가시험 (암호· 알고리즘·시험,· 소프트웨어· 무결성·시험) | - | 오류코드 (성공/실패) |  |
|  | KISA_Crypto_encryptInit(); KISA_Crypto_encryptUpdate(); KISA_Crypto_encryptFinal(); KISA_Crypto_encrypt(); | 블록암호· 암호화 | 블록암호· 설정·정보,· 평문,· 키,·IV | 암호문,· 오류코드 |  |
|  | KISA_Crypto_decryptInit(); KISA_Crypto_decryptUpdate(); KISA_Crypto_decryptFinal(); KISA_Crypto_decrypt(); | 블록암호 복호화 | 블록암호·설정· 정보,·암호문,· 키,·IV | 평문, 오류코드 |  |
|  | KISA_Crypto_hashInit(); KISA_Crypto_hashUpdate(); KISA_Crypto_hashFinal(); KISA_Crypto_hash(); | 해시함수· 수행 | 해시함수·설정· 정보,·메시지 | 해시값, 오류코드 |  |