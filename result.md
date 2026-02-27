# PDF 추출 벤치마크 결과 정리

## 1. 실험 목적

국가사이버안보센터 공지 PDF(8, 18, 19번) 기반으로 아래 4개 라이브러리를 비교했습니다.

- PyMuPDF
- pdfplumber
- pdfminer.six
- pypdf

비교 지표는 아래 항목을 사용했습니다.

- `extract_time_sec` (추출 속도)
- `text_chars`, `text_coverage_pct`, `text_consensus_pct` (텍스트 추출 품질 대리 지표)
- `table_count`, `table_structure_pct` (표 추출/구조 유지)
- `image_count` (이미지 감지/추출)

---

## 2. 실험 데이터 및 실행

- 입력 데이터: `dataset/file_8.pdf`, `dataset/file_18.pdf`, `dataset/file_19.pdf`
- 파서 스크립트: `parser/*.py`
- 통합 요약: `summarize_outputs.py`
- 최종 원본 결과:
  - `outputs/summary/combined_benchmark_results.csv`
  - `outputs/summary/combined_benchmark_results.md`

---

## 3. 라이브러리별 요약 (3개 PDF 평균/합계)

| library | 평균 추출시간(s) | 평균 text_coverage(%) | 평균 text_consensus(%) | 표 개수(합계) | 표 구조율(평균, %) | 이미지 개수(합계) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pymupdf | **1.14** | 89.11 | **94.46** | 0 | 0.00 | 228 |
| pdfminer | 8.67 | **100.00** | 94.45 | 0 | 0.00 | 0 |
| pdfplumber | 10.83 | 85.07 | 94.15 | **611** | **57.73** | **305** |
| pypdf | 6.17 | 84.70 | 85.56 | 0 | 0.00 | 228 |

### 해석

- **속도 우위:** `pymupdf`가 압도적으로 빠름
- **텍스트 최대 확보:** `pdfminer`가 `text_coverage_pct=100%`로 가장 높음
- **표 추출:** `pdfplumber`만 실질적으로 표를 대량 추출함
- **이미지 추출:** `pdfplumber`가 가장 많고, `pymupdf`, `pypdf`도 가능
- **안정성:** `pypdf`는 `file_18`에서 `text_consensus_pct`가 낮아(75.0) 본문 주 추출기로는 불리.

> 참고: `pdfminer`의 `table_count`, `image_count`가 0인 이유는 현재 구현(`parser/pdfminer_parser.py`)이 텍스트 중심 추출만 수행하기 때문입니다. (해당 parser의 목적이 원래 텍스트 중심으로 이루어진 것 같았습니다..!)

---

## 4. 파일별 요약

### file_18.pdf
- 속도: `pymupdf` (0.914s) 최고
- 텍스트 커버리지: `pdfminer`가 가장 컸음(pdfminer의 목적이 텍스트 중심이었으니까, 이해되는 결과지만, 실제로 파일을 보면 상당히 들여쓰니나 특수 기호 등 깨져있는 모습이 많이 보였음.)
- 표/이미지: `pdfplumber` 표 225개, 이미지 158개

### file_19.pdf
- 속도: `pymupdf` (1.688s) 최고
  텍스트 커버리지: `pdfminer`가 가장 컸음
- 표/이미지: `pdfplumber` 표 188개, 이미지 131개

### file_8.pdf
- 속도: `pymupdf` (0.817s) 최고
  텍스트 커버리지: `pdfminer`
- 표/이미지: `pdfplumber` 표 198개, 이미지 16개

---

## 5. 결론

- 이번 벤치마크는 **정상 수행**되었습니다.(모든 행 `status=ok`)
- 단일 도구보다 **혼합 전략**이 유리하다는 생각이 들었습니다. 다음 단계로는 현재 데이터 기준 최적 조합은 `pymupdf + pdfplumber`로 사용해서 텍스트와 이미지, 표를 따로 추출하는 방식을 도입해보면 더 좋은 결과를 낼 수 있을 것 같습니다. 
