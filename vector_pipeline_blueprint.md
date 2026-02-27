# Vector DB + LLM QA Framework Blueprint

## 1) 데이터 모델 (멀티모달)

문서 단위를 다음과 같이 저장합니다.

- `doc_id`: 문서 식별자
- `chunk_id`: 청크 식별자
- `source_type`: `text | table | image`
- `content`: 원문 텍스트 또는 테이블 Markdown
- `embedding`: 벡터
- `metadata`
  - `page_number`
  - `section_title`
  - `bbox` (가능 시)
  - `extraction_lib` (pymupdf/pdfplumber/...)
  - `quality_flags` (예: low_text_coverage)

## 2) Chunking 전략

- 텍스트: 제목/문단 경계 기반 semantic chunking + 최대 토큰 제한
- 표: 표 단위 1차 chunk, 큰 표는 행 단위 분할(헤더 유지)
- 이미지: 캡션/주변 텍스트를 연결한 설명 텍스트 생성

## 3) Embedding 전략

- 텍스트/표: 다국어 임베딩 모델 (`bge-m3`, `multilingual-e5-large` 등)
- 이미지: CLIP 계열 임베딩(`open_clip` 등)
- 하이브리드 검색: dense + sparse(BM25)

## 4) Vector DB 스키마 (예: ChromaDB/Pinecone)

- Collection 분리
  - `doc_text_chunks`
  - `doc_table_chunks`
  - `doc_image_chunks`
- 공통 메타데이터 필드
  - `doc_id`, `chunk_id`, `source_type`, `page_number`, `created_at`

## 5) 질의응답 파이프라인

1. Query 분류 (`text-centric`, `table-centric`, `figure-centric`)
2. 타입별 retriever 가중치 조정
3. 상위 K개 컨텍스트 재정렬(Reranker)
4. 근거 인용 포함 응답 생성

## 6) 품질 관리 지표

- Retrieval: Recall@k, MRR
- Generation: Faithfulness, Citation Precision
- Extraction QA: 텍스트 커버리지, 표 구조 유지율, 이미지 누락률

## 7) 권장 실험 순서

1. Phase 1 결과 기반 파서 1~2개 선택
2. Phase 2 레이아웃 분석으로 문서 구조 인식 강화
3. Phase 3에서 멀티모달 인덱싱 + RAG 평가셋 구축