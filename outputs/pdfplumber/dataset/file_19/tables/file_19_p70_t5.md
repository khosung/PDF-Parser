| ‘소프트웨어/펌웨어 보안’ 요구사항의 무결성 시험 시 사용 가능한 암호 알고리즘 목록 |  |  |
| --- | --- | --- |
| 메시지 인증 | HMAC | · SHA2, LSH, SHA3 |
|  | GMAC | · AES*, ARIA, SEED, LEA |
|  | CMAC | · AES*, ARIA, SEED, LEA, HIGHT |
| 전자서명 | RSA-PSS | · |n| = 2048, 3072 · hash = SHA2-224/256 |
|  | KCDSA | · (|p|, |q|) = (2048, 224), (2048, 256), (3072, 256) · hash = SHA2-224/256 |
|  | EC-KCDSA | · curve = P-224/256, B-233/283, K-233/283 · hash = SHA2-224/256 |
|  | ECDSA | · curve = P-224/256, B-233/283, K-233/283 · hash = SHA2-224/256 |