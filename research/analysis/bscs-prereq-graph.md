# BSCS – đồ thị môn học & tiên quyết (phân tích tự động, CẦN người duyệt)

Nguồn: `sources/text/curriculum-frameworks/bscs/` (S001 và các bản cũ). Parser: `parse_catalog.py` + `analyze_bscs.py` (heuristic). Chỉ phần *mô tả môn* được dùng; bảng khung chương trình chưa parse.

## 1. Số liệu mỗi phiên bản

| Phiên bản | Số môn parse | Có tiên quyết resolve được | Không có (None/N/A) | Cần review |
|---|---|---|---|---|
| V2021 | 41 | 15 | 19 | 7 |
| V2023-i4 | 40 | 14 | 19 | 7 |
| 23-27 | 41 | 19 | 20 | 2 |
| AY24-25c5 | 48 | 12 | 27 | 9 |
| 24-28 | 49 | 20 | 28 | 1 |

## 2. Đồ thị tiên quyết BSCS 2024-28 (môn có tiên quyết)

| Môn (mã trong mô tả) | TC | Tiên quyết (resolve) | Ghi chú |
|---|---|---|---|
| MATH1020 Calculus II | 4 | Calculus I |  |
| MATH2010 Probability and Statistics | 4 | Calculus I |  |
| MATH4010 Advanced Probability and Statistics | 3 | Probability and Statistics |  |
| PHYS1010 Physics I | 4 | Calculus I |  |
| PHYS2020 Physics II | 3 | Physics I |  |
| COMP1020 Object-oriented Programming and Data S | 4 | Introduction to Programming |  |
| COMP2020 Computer Organization | 4 | Object-oriented Programming and Data Structures |  |
| COMP3010 Algorithm Design | 4 | Object-oriented Programming and Data Structures, Discrete Mathematics |  |
| COMP2020 Software Construction | 4 | Object-oriented Programming and Data Structures |  |
| COMP2040 Operating Systems | 4 | Computer Organization |  |
| COMP2050 Artificial Intelligence | 4 | Introduction to Programming, Probability and Statistics |  |
| COMP3020 Machine Learning | 4 | Linear Algebra, Probability and Statistics, Object-oriented Programming and Data Structures |  |
| COMP3030 Databases and Database Systems | 4 | Object-oriented Programming and Data Structures |  |
| COMP3040 Computer Vision | 3 | Machine Learning, Linear Algebra, Object-oriented Programming and Data Structures |  |
| COMP3050 Networks | 3 | Computer Organization |  |
| COMP4010 Data Visualization | 3 | Introduction to Programming, Probability and Statistics |  |
| COMP4020 Natural Language Processing | 3 | Machine Learning, Object-oriented Programming and Data Structures |  |
| COMP4030 Cybersecurity | 3 | Object-oriented Programming and Data Structures, Discrete Mathematics |  |
| COMP4040 Data Mining and Big Data Analytics | 3 | Linear Algebra, Object-oriented Programming and Data Structures, Machine Learning |  |
| COMP4050 Cryptography | 3 | Linear Algebra |  |
| COMP4890 Graduation Thesis/Capstone | 6 | — | ⚠ REVIEW: Practice/Internship; Determined by the advisor This Capstone course is |

**Chuỗi tiên quyết dài nhất:** 4 môn liên tiếp. Môn cuối chuỗi: Operating Systems, Computer Vision, Networks, Natural Language Processing, Data Mining and Big Data Analytics.

**Môn là tiên quyết của nhiều môn nhất (điểm nghẽn):** Object-oriented Programming and Data Structures (9), Probability and Statistics (4), Linear Algebra (4), Calculus I (3), Introduction to Programming (3), Machine Learning (3)

**Tiên quyết trỏ tới môn không có trong mô tả (⚠):** không

## 3. Khác biệt giữa các phiên bản (theo tên môn)

### V2021 → V2023-i4
- Thêm (5): Agile Innovation & Entrepreneurship; Leadership Development; Cross-Cultural Navigation; Arts Appreciation; Music Appreciation
- Bỏ (6): Agile Innovation; Academic English 1; Academic English 2; Organization behaviors; Arts; OASIS
- Đổi tín chỉ (0): —
- Đổi tiên quyết (0): —

### V2023-i4 → 23-27
- Thêm (1): Art Appreciation and Application
- Bỏ (0): —
- Đổi tín chỉ (1): Databases and Database Systems: 4→3
- Đổi tiên quyết (5): Machine Learning: [linear algebra, probability and statistics]→[linear algebra, probability and statistics, object-oriented programming and data structures]; Computer Vision: [machine learning, linear algebra]→[machine learning, linear algebra, object-oriented programming and data structures]; Data Visualization: [introduction to programming, probability and statistics, data mining and big data analytics]→[introduction to programming, probability and statistics]; Natural Language Processing: [machine learning]→[machine learning, object-oriented programming and data structures]; Data Mining and Big Data Analytics: [linear algebra]→[linear algebra, object-oriented programming and data structures, machine learning]

### 23-27 → AY24-25c5
- Thêm (10): Technology Ethics; Computational Thinking; Academic and Professional Writing; Introduction to Data Literacy; Introduction to AI Literacy; Interpersonal and Multimedia Communication; Introduction to Managing Skills; Introduction to International Relations; Artistic Performance and Application; Leadership and Teambuilding Bootcamp
- Bỏ (3): Agile Innovation & Entrepreneurship; Leadership Development; Linear Algebra
- Đổi tín chỉ (1): Databases and Database Systems: 3→4
- Đổi tiên quyết (3): Computer Vision: [machine learning, linear algebra, object-oriented programming and data structures]→[machine learning]; Data Visualization: [introduction to programming, probability and statistics]→[introduction to programming, probability and statistics, data mining and big data analytics]; Natural Language Processing: [machine learning, object-oriented programming and data structures]→[machine learning]

### AY24-25c5 → 24-28
- Thêm (1): Linear Algebra
- Bỏ (0): —
- Đổi tín chỉ (0): —
- Đổi tiên quyết (3): Computer Vision: [machine learning]→[machine learning, linear algebra, object-oriented programming and data structures]; Data Visualization: [introduction to programming, probability and statistics, data mining and big data analytics]→[introduction to programming, probability and statistics]; Natural Language Processing: [machine learning]→[machine learning, object-oriented programming and data structures]
