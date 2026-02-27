| 항목 | AS03.04, AS03.05, AS03.06, AS03.08 |
| --- | --- |
| 보안요구사항 개요 | 암호모듈의·논리적·인터페이스(데이터·입/출력,·제어·입력)·명세 |
| VE03.04.01 | 암호모듈이·제공하는·서비스에·대한·논리적·인터페이스·명세 |
| VE03.05.01 | 데이터·입력·인터페이스를·통해·입력되는·모든·데이터·명세 |
| VE03.06.01 | 데이터·출력·인터페이스를·통해·출력되는·모든·데이터·명세 |
| VE03.08.01 | 제어·입력·인터페이스를·통해·입력되는·제어·데이터·명세 |
| 작성 예시 |  |
| 서비스·분류 API·명칭 동작·내용 입력 출력 암호모듈 오류코드 초기화 KISA_Crypto_initialize() - 초기화 (성공/실패) 암호모듈·현재· 암호모듈 상태확인 KISA_Crypto_getState() - 상태확인 상태값 암호모듈·이름·및·· 암호모듈 버전확인 KISA_Crypto_getVersion() - 버전·확인 버전값 (주기적)·자가시험 (암호·알고리즘·시험,· 오류코드 자가시험 KISA_Crypto_selftest() - 소프트웨어·무결성· (성공/실패) 시험) KISA_Crypto_encryptInit(); 블록암호· KISA_Crypto_encryptUpdate(); 블록암호· 암호문,· 설정정보, KISA_Crypto_encryptFinal(); 암호화 오류코드 평문,·키,·IV KISA_Crypto_encrypt(); 블록암호 KISA_Crypto_decryptInit(); KISA_Crypto_decryptUpdate(); 블록암호 블록암호·설정정보, 평문, KISA_Crypto_decryptFinal(); 복호화 암호문,·키,·IV 오류코드 KISA_Crypto_decrypt(); KISA_Crypto_hashInit(); KISA_Crypto_hashUpdate(); 해시함수· 해시함수·설정정보, 해시값, 해시함수 KISA_Crypto_hashFinal(); 수행 메시지 오류코드 KISA_Crypto_hash(); KISA_Crypto_hmacInit(); 메시지 KISA_Crypto_hmacUpdate(); HMAC·설정정보,· HMAC값, HMAC·연산·수행 인증코드 KISA_Crypto_hmacFinal(); 메시지,·MAC·키 오류코드 KISA_Crypto_hmac(); KISA_Crypto_drbgInit(); 난수발생기 KISA_Crypto_drbgReseed(); 난수 설정정보, 난수비트열, KISA_Crypto_drbgGenerate(); 난수·생성 발생기 엔트로피,· 오류코드 KISA_Crypto_drbgClose(); 난수출력길이 KISA_Crypto_drbgRand(); |  |