# PDF-Parser

PDF 문서에서 텍스트, 표, 이미지를 추출하고, 라이브러리별 성능을 비교하기 위한 실험용 프로젝트입니다.

## 구조

- `parser/pymupdf_parser.py`
- `parser/pdfplumber_parser.py`
- `parser/pdfminer_parser.py`
- `parser/pypdf_parser.py`
- `run_parsers_cli.py` (parser 하위 모든 Python 파일 실행)
- `summarize_outputs.py` (`outputs/parser이름` 전체를 walk 하여 통합 결과 생성)

## 설치

```bash
pip install -r requirements.txt
```

## 1) 메인 실행 (CLI)

```bash
python run_parsers_cli.py --parsers-dir parser --input-dir dataset --output-root outputs
```

- `--parsers-dir`: 실행할 parser python 파일 루트
- `--input-dir`: PDF 입력 경로
- `--output-root`: 기본 `outputs`

`run_parsers_cli.py`는 `parser` 하위의 `*.py`를 모두 실행하며, 각 결과는 자동으로 `outputs/parser이름/데이터셋이름`에 저장됩니다.

## 2) 기본 출력 구조

각 parser(`pymupdf`, `pdfplumber`, `pdfminer`, `pypdf`)마다 아래 구조가 생성됩니다.

- `outputs/parser이름/데이터셋이름/benchmark_results.csv`
- `outputs/parser이름/데이터셋이름/benchmark_results.md`
- `outputs/parser이름/데이터셋이름/file_번호/texts/*`
- `outputs/parser이름/데이터셋이름/file_번호/tables/*` (pdfplumber 기반 Markdown 테이블)
- `outputs/parser이름/데이터셋이름/file_번호/images/*` (가능한 라이브러리에서 추출)

## 3) 통합 결과 생성 (outputs walk)

```bash
python summarize_outputs.py --input-dir outputs --output-dir outputs/summary
```

- `--input-dir`에 `outputs`를 주면 하위 `outputs/parser이름/데이터셋이름`을 자동 탐색
- 각 parser 결과를 합쳐서 아래 파일 생성
	- `outputs/summary/combined_benchmark_results.csv`
	- `outputs/summary/combined_benchmark_results.md`

## 비교 지표 정의

- `extract_time_sec`: 파일 단위 추출 시간
- `text_chars`: 추출된 텍스트 길이
- `text_coverage_pct`: 동일 PDF 내 최대 길이 대비 텍스트 커버리지(대리 정확도)
- `text_consensus_pct`: 타 라이브러리와의 평균 유사도(대리 정확도)
- `table_count`: 감지/추출된 표 개수
- `table_structure_pct`: 비어있지 않은 표 비율(구조 유지력 대리 지표)
- `image_count`: 추출 혹은 감지된 이미지 개수

> 참고: `text_coverage_pct`, `text_consensus_pct`는 `summarize_outputs.py`에서 통합 계산됩니다.