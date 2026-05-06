# Hướng Dẫn Annotation Evidence

## Mục tiêu

Tài liệu này chuẩn hóa cách gán nhãn evidence để phần `annotated evidence evaluation` có giá trị học thuật cao hơn.

Mục tiêu của annotation không phải là chấm xem câu trả lời có đúng hay không.

Mục tiêu là xác định:

- evidence nào thật sự hỗ trợ câu trả lời
- tập evidence nào là đủ
- evidence nào gây mâu thuẫn hoặc gây nhiễu

## 1. Các trường annotation chính

Mỗi mẫu annotation nên điền các trường:

- `gold_evidence_node_ids`
- `sufficient_evidence_sets`
- `contradiction_node_ids`
- `annotation_status`
- `notes`

## 2. Định nghĩa

### Gold evidence node

Là node mà nội dung của nó trực tiếp đóng góp vào việc suy ra câu trả lời đúng.

Một node chỉ nên được gán là gold nếu:

- chứa fact cần thiết
- hoặc chứa reasoning trace/insight cần thiết
- hoặc nối được một bước bridge bắt buộc trong lập luận

Không gán gold cho node chỉ vì:

- có từ khóa giống câu hỏi
- có nội dung liên quan chung chung
- có vẻ “có ích” nhưng không thật sự cần thiết

### Sufficient evidence set

Là một tập node mà khi kết hợp lại, người đánh giá có thể suy ra câu trả lời đúng một cách hợp lý.

Một câu có thể có nhiều sufficient set.

Ví dụ:

- set A: một passage bridge + một passage answer
- set B: một trace đúng + một supporting insight

### Contradiction node

Là node có nội dung:

- phủ định fact đúng
- gây định hướng sai
- mâu thuẫn trực tiếp với gold evidence

## 3. Quy tắc annotation

### Rule 1. Ưu tiên tính cần thiết

Nếu bỏ node đó đi mà vẫn suy ra câu trả lời đúng rõ ràng, thì node đó thường không phải gold evidence bắt buộc.

### Rule 2. Không annotate theo cảm tính “có vẻ liên quan”

Node chỉ giống từ khóa nhưng không giúp suy luận thì không phải evidence tốt.

### Rule 3. Tách “liên quan” và “đủ”

Một node có thể liên quan nhưng chưa đủ.

Vì vậy:

- `gold_evidence_node_ids` là tập node hỗ trợ thật sự
- `sufficient_evidence_sets` là tập con đủ để trả lời

### Rule 4. Ghi contradiction rõ ràng

Nếu node làm lệch hướng hoặc phủ định đáp án đúng, hãy đưa vào `contradiction_node_ids`.

### Rule 5. Ưu tiên nhất quán giữa annotator

Nếu có nhiều annotator:

- nên đọc chung guideline này
- nên làm 10-20 mẫu pilot trước
- sau đó mới chia mẫu lớn

## 4. Quy trình annotation khuyến nghị

### Bước 1

Đọc câu hỏi và đáp án đúng.

### Bước 2

Đọc `selected_retrieval_path` trước để xem hệ thống đã chọn gì.

### Bước 3

Đọc `candidate_retrieval_path` để xem còn node nào có thể là gold nhưng hệ thống bỏ sót.

### Bước 4

Đánh dấu:

- node gold
- node contradiction
- một hay nhiều sufficient evidence set

### Bước 5

Đặt `annotation_status=done` khi đã hoàn tất.

## 5. Mẹo để annotation có giá trị cho paper

### Nên làm

- chọn một tập mẫu đại diện
- có cả easy và hard case
- có cả case đúng và case sai
- có cả case bị noisy/contradictory memory

### Không nên làm

- chỉ annotate các case đẹp
- chỉ annotate các case model đã đúng
- annotate quá rộng khiến gần như mọi node liên quan đều thành gold

## 6. Metric nào sẽ dùng từ annotation

Từ annotation, repo hiện tính:

- `evidence_precision`
- `evidence_recall`
- `evidence_f1`
- `evidence_set_coverage`
- `contradiction_exposure_rate`

Ý nghĩa:

- `evidence_precision`: hệ thống chọn đúng evidence đến đâu
- `evidence_recall`: hệ thống bỏ sót evidence cần thiết nhiều hay ít
- `evidence_f1`: cân bằng precision/recall
- `evidence_set_coverage`: hệ thống có chọn được một tập đủ hay không
- `contradiction_exposure_rate`: hệ thống có bị hút vào evidence mâu thuẫn hay không

## 7. Cỡ mẫu khuyến nghị cho paper

Nếu nguồn lực hạn chế:

- annotate ít nhất 50-100 mẫu

Nếu muốn chắc hơn:

- annotate 100-200 mẫu

Nếu có nhiều annotator:

- nên có một tập giao nhau để đo agreement

## 8. Câu viết gợi ý cho paper

Bạn có thể viết theo kiểu:

> We complement automatic grounding proxies with a manually annotated evidence benchmark. For each example, annotators identify gold supporting nodes, sufficient support sets, and contradiction nodes. This allows us to evaluate not only whether the system answers correctly, but whether it answers with the right evidence.

Đây là điểm rất có giá trị học thuật vì nó giúp paper chứng minh:

- hệ thống đúng vì grounding tốt hơn
- không chỉ đúng vì model đoán tốt hơn
