# DUT – Công nghệ thông tin (Việt–Nhật): khung chương trình đào tạo

- **Nguồn:** 6 ảnh chụp trang "Chi tiết Khung chương trình & Tiến độ, kết quả học tập" trên web sinh viên DUT, do user cung cấp ngày 2026-11-20. **Chưa đối chiếu** với văn bản CTĐT chính thức; chưa có số quyết định/khóa áp dụng.
- **File:** `curriculum.csv` (UTF-8 có BOM, 80 dòng), chép tay từ ảnh + kiểm tra tự động (mã tham chiếu tồn tại, không có chu trình, học trước nằm ở kỳ sớm hơn, cờ song hành khớp).
- **Không lưu:** cột "Điểm học", "Điểm chuyển" (dữ liệu cá nhân của người cung cấp). Hồ sơ SV mô phỏng phải là dữ liệu giả.

## Cột
`tt, hoc_ky, ma_hp, ten_hp, so_tin_chi, loai (bat_buoc|tu_chon), nhom_tu_chon, hoc_truoc, song_hanh, tien_quyet` (danh sách mã, ngăn cách `;`), `bat_buoc_dk_song_hanh` (dòng ghi "Được, nếu ĐK được HP song hành"), `ht_da`, `tq_da` (dấu ✓ trong ảnh; user xác nhận **không cần quan tâm** 2 cột này, giữ lại chỉ để đối chiếu với ảnh).

## Thống kê (tính từ file)
80 học phần: 58 bắt buộc (122 TC), 22 tự chọn trong 2 nhóm "Chọn 2 trong 11" (kỳ 5 và kỳ 7), mỗi môn 2 TC, mỗi nhóm chọn 2 môn → 8 TC tự chọn. Chuỗi "học trước" dài nhất: 6 học phần. Số tổ hợp chọn tự chọn: C(11,2) × C(11,2) = 55 × 55 = 3.025.

## Quy ước đã được user xác nhận (2026-11-20)
1. Nhiều mã trong cùng ô "học trước" = **cần đủ tất cả** (VÀ).
2. "Học song hành" = học **cùng kỳ**. (Mọi quan hệ song hành trong file đều là hai môn cùng kỳ chuẩn.)
3. Bảng **dừng ở dòng 80**.
4. Tự chọn: tổng 8 TC; mỗi đợt tự chọn phải chọn đúng 2 trong 11 môn của đợt đó.

## Còn mở
- Các học phần 0 tín chỉ (TH Kỹ thuật lập trình, TH LT hướng đối tượng, TH Lập trình mạng, TH Quản trị mạng, Giáo dục thể chất 1) giữ nguyên như hiển thị.
- Chưa rõ tổng tín chỉ tối thiểu để tốt nghiệp và điều kiện ngoài khung (chứng chỉ ngoại ngữ, giáo dục quốc phòng…); từ khung chỉ tính được 130 TC (122 + 8).
- Chưa rõ: SV có được đăng ký thêm môn tự chọn ngoài 2+2 không; "định hướng" chuyên ngành có được ghi ở tài liệu nào khác không.
