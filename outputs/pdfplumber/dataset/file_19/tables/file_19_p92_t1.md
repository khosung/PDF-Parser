| 공통 | ⦁ One-Step H 함수 또는 Two-Step MAC 함수를 검증대상 MAC으로 구성할 경우, 공유 비밀값 K_Z는 MAC 함수의 메시지로 사용되어야 한다. |
| --- | --- |
| SP800-56C Rev.2 One-Step | ⦁ H 함수는 검증대상 해시 또는 검증대상 HMAC으로 구성해야 한다. |
| SP800-56C Rev.2 Two-Step | ⦁ MAC 함수는 검증대상 HMAC 또는 검증대상 CMAC으로 구성해야 한다. ⦁ KDF 함수는 검증대상 KBKDF로 구성해야 한다. ⦁ MAC 함수를 CMAC으로 구성할 경우 HIGHT 기반 CMAC은 사용할 수 없다. ※ HIGHT 출력 크기에 따른 K 안전성 부족 DK ⦁ MAC 함수와 KDF 함수는 동일한 PRF를 사용해야 한다. ※ CMAC을 사용할 경우, KDF 함수는 128비트 키 길이를 갖는 PRF가 사용된다. 예) MAC 함수: CMAC_ARIA-256 사용, KDF 함수: CMAC_ARIA-128 사용 ⦁ MAC 함수의 출력값인 K 는 절단(truncate)없이 모두 KDF 함수의 키 값으로 DK 사용되어야 한다. |