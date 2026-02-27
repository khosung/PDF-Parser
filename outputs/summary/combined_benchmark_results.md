# Combined PDF Extraction Benchmark

| pdf_file | library | parser_name | dataset_name | page_count | extract_time_sec | text_chars | text_coverage_pct | text_consensus_pct | table_count | table_structure_pct | image_count | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| file_18.pdf | pdfminer | pdfminer | dataset | 197 | 13.052 | 140483 | 100.000 | 91.361 | 0 | 0.000 | 0 | ok |
| file_19.pdf | pdfminer | pdfminer | dataset | 105 | 6.373 | 99579 | 100.000 | 94.743 | 0 | 0.000 | 0 | ok |
| file_8.pdf | pdfminer | pdfminer | dataset | 120 | 5.839 | 130915 | 100.000 | 97.241 | 0 | 0.000 | 0 | ok |
| file_18.pdf | pdfplumber | pdfplumber | dataset | 197 | 14.948 | 116323 | 82.802 | 91.036 | 225 | 68.889 | 158 | ok |
| file_19.pdf | pdfplumber | pdfplumber | dataset | 105 | 7.808 | 78580 | 78.912 | 94.337 | 188 | 35.106 | 131 | ok |
| file_8.pdf | pdfplumber | pdfplumber | dataset | 120 | 8.015 | 122391 | 93.489 | 97.065 | 198 | 69.192 | 16 | ok |
| file_18.pdf | pymupdf | pymupdf | dataset | 197 | 0.917 | 128822 | 91.699 | 91.355 | 0 | 0.000 | 123 | ok |
| file_19.pdf | pymupdf | pymupdf | dataset | 105 | 1.695 | 81117 | 81.460 | 94.741 | 0 | 0.000 | 89 | ok |
| file_8.pdf | pymupdf | pymupdf | dataset | 120 | 0.744 | 123272 | 94.162 | 97.284 | 0 | 0.000 | 16 | ok |
| file_18.pdf | pypdf | pypdf | dataset | 197 | 8.342 | 111557 | 79.410 | 75.000 | 0 | 0.000 | 123 | ok |
| file_19.pdf | pypdf | pypdf | dataset | 105 | 5.955 | 78550 | 78.882 | 84.782 | 0 | 0.000 | 89 | ok |
| file_8.pdf | pypdf | pypdf | dataset | 120 | 3.127 | 125431 | 95.811 | 96.888 | 0 | 0.000 | 16 | ok |