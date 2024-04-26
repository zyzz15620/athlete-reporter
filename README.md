## Tổng Quan:
Đây là một script viết bằng Python kết nối đến một cơ sở dữ liệu MySQL chứa dữ liệu của các vận động viên, trích xuất thông tin về các thuộc tính vật lý của vận động viên, tính toán z-score cho các thuộc tính được chọn và tạo ra các báo cáo dựa trên phân tích đó.

## Tính Năng:
- Kết Nối Cơ Sở Dữ Liệu MySQL: Script thiết lập kết nối đến một cơ sở dữ liệu MySQL nơi dữ liệu của các vận động viên được lưu trữ.
- Trích Xuất Dữ Liệu: Script trích xuất dữ liệu của các vận động viên từ cơ sở dữ liệu, bao gồm các thuộc tính như dung tích hô hấp, linh hoạt, sức mạnh và sức bền.
- Tính Toán Z-score: Z-score được tính toán cho mỗi thuộc tính của từng vận động viên dựa trên so sánh với một nhóm tham chiếu.
- Tạo Báo Cáo: Script tạo ra các báo cáo chi tiết cho mỗi vận động viên, bao gồm thông tin cá nhân, các thuộc tính vật lý, z-score và các biểu đồ minh họa.

## Cách Sử Dụng:
- Cấu Hình Cơ Sở Dữ Liệu: Cập nhật script với các thông tin xác thực cơ sở dữ liệu MySQL phù hợp (host, user, password, database).
- Tùy Biến: Sửa đổi lại Template (dòng 75) dẫn đến file Template mẫu
- Tùy Biến: Sửa lại phạm vi các môn võ cần xuất báo cáo (dòng 9)
- Tạo Báo Cáo: Chạy script để tạo ra các báo cáo cá nhân cho các vận động viên trong cơ sở dữ liệu.
