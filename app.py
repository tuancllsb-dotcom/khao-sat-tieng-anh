import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from gtts import gTTS
import re
import io
import base64
import time

# Thiết lập cấu hình phòng khảo thí thực chiến quy chuẩn chuyên nghiệp
st.set_page_config(
    page_title="Hệ Thống Khảo Sát Năng Lực Tiếng Anh VSTEP Giáo Viên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KHO DỮ LIỆU ĐỀ THI ĐA PHÂN HỆ M MÃ HÓA CẤU TRÚC 3 DÒNG INTERLINEAR TUYỆT ĐỐI TỪ GỐC
VSTEP_EXAM_DB = {
    "1️⃣ VSTEP Nghe": [
        {
            "id": 1,
            "type": "Part 1: Thông báo ngắn (Short Announcement)",
            "correct": "D",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: How many languages are taught at Hanoi International Language School?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: haʊ ˈmɛni ˈlæŋɡwɪdʒɪz ɑː(r) tɔːt æt ˌhæˈnɔɪ ˌɪntə(r)ˈnæʃnəl ˈlæŋɡwɪdʒ skuːl/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Có bao nhiêu ngôn ngữ được giảng dạy tại Trường Ngôn ngữ Quốc tế Hà Nội?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. 1<br><small><font color="#4B5563">🎵 IPA: /eɪ. wʌn/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: 1 ngôn ngữ</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. 2<br><small><font color="#4B5563">🎵 IPA: /biː. tuː/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: 2 ngôn ngữ</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. 3<br><small><font color="#4B5563">🎵 IPA: /siː. θriː/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: 3 ngôn ngữ</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. 4<br><small><font color="#4B5563">🎵 IPA: /diː. fɔː(r)/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: 4 ngôn ngữ</font></i>"""
            },
            "raw_script": "Welcome to Hanoi International Language School. This semester, our institution is proud to offer official certification courses in four distinct languages: English, French, Japanese, and Korean.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Welcome to Hanoi International Language School. This semester, our institution is proud to offer official certification courses in four distinct languages: English, French, Japanese, and Korean.<br>
<small><font color="#4B5563">🎵 IPA: /ˈwɛlkəm tuː ˌhæˈnɔɪ ˌɪntə(r)ˈnæʃnəl ˈlæŋɡwɪdʒ skuːl. ðɪs sɪˈmɛstə(r), ˈaʊə(r) ˌɪnstɪˈtjuːʃn̩ ɪz praʊd tuː ˈɒfə(r) əˈfɪʃl ˌsɜːtɪfɪˈkeɪʃn̩ ˈkɔːsɪz ɪn fɔː(r) dɪˈstɪŋkt ˈlæŋɡwɪdʒɪz: ˈɪŋŋlɪʃ, frɛntʃ, ˌdʒæpəˈniːz, ənd kəˈriːən./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Chào mừng đến với Trường Ngôn ngữ Quốc tế Hà Nội. Học kỳ này, cơ sở của chúng tôi tự hào cung cấp các khóa học chứng chỉ chính thức bằng bốn ngôn ngữ riêng biệt: Tiếng Anh, Tiếng Pháp, Tiếng Nhật và Tiếng Hàn.</font></i>"""
        },
        {
            "id": 2,
            "type": "Part 1: Hướng dẫn bay (Airport Announcement)",
            "correct": "B",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: What is the boarding time of Flight VN178?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: wɒt ɪz ðə ˈbɔːdɪŋ taɪm ɒv flaɪt viː-ɛn-wʌn-sɛvən-eɪt/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Giờ lên máy bay của Chuyến bay VN178 là mấy giờ?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. 3:30<br><small><font color="#4B5563">🎵 IPA: /eɪ. θriː ˈθɜːti/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: 3 giờ 30 phút</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. 3:45<br><small><font color="#4B5563">🎵 IPA: /biː. θriː fɔːti-faɪv/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: 3 giờ 45 phút</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. 4:15<br><small><font color="#4B5563">🎵 IPA: /siː. fɔː(r) fɪfˈtiːn/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: 4 giờ 15 phút</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. 4:45<br><small><font color="#4B5563">🎵 IPA: /diː. fɔː(r) fɔːti-faɪv/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: 4 giờ 45 phút</font></i>"""
            },
            "raw_script": "Attention all passengers traveling on Flight VN178 to Ho Chi Minh City. Due to the late arrival of the incoming aircraft, the boarding time has been rescheduled from 3:30 to 3:45. Please gather at Gate 4 immediately.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Attention all passengers traveling on Flight VN178 to Ho Chi Minh City. Due to the late arrival of the incoming aircraft, the boarding time has been rescheduled from 3:30 to 3:45. Please gather at Gate 4 immediately.<br>
<small><font color="#4B5563">🎵 IPA: /əˈtɛnʃn̩ ɔːl ˈpæsɪndʒəz ˈtrævəlɪŋ ɒn flaɪt viː-ɛn-wʌn-sɛvən-eɪt tuː hoʊ tʃiː mɪn ˈsɪti. djuː tuː ðə leɪt əˈraɪvl ɒv ði ˈɪnˌkʌmɪŋ ˈeəkrɑːft, ðə ˈbɔːdɪŋ taɪm hæz biːn ˌriːˈʃɛdjuːld frɒm θriː θɜːti tuː θriː fɔːti-faɪv. pliːz ˈɡæðə(r) æt ɡeɪt fɔː(r) ɪˈmiːdiətli./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Xin chú ý tất cả hành khách đi trên Chuyến bay VN178 đến Thành phố Hồ Chí Minh. Do máy bay đến muộn, giờ lên máy bay đã được thay đổi từ 3:30 sang 3:45. Xin vui lòng tập trung tại Cửa số 4 ngay lập tức.</font></i>"""
        },
        {
            "id": 3,
            "type": "Part 2: Hội thoại học thuật (Academic Conversation)",
            "correct": "D",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: What will be happening in Lecture hall 4 next Monday?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: wɒt wɪl biː ˈhæpənɪŋ ɪn ˈlɛktʃə hɔːl fɔː nɛkst ˈmʌndeɪ/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Điều gì sẽ xảy ra tại Giảng đường 4 vào thứ Hai tới?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. An art workshop<br><small><font color="#4B5563">🎵 IPA: /eɪ. ən ɑːt ˈwɜːkʃɒp/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: Một buổi hội thảo nghệ thuật</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. An art exhibition<br><small><font color="#4B5563">🎵 IPA: /biː. ən ɑːt ˌɛksɪˈbɪʃn̩/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: Một cuộc triển lãm nghệ thuật</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. A history lesson<br><small><font color="#4B5563">🎵 IPA: /siː. ə ˈhɪstri ˈlɛsn̩/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: Một tiết học lịch sử</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. A talk about history of art<br><small><font color="#4B5563">🎵 IPA: /diː. ə tɔːk əˈbaʊt ˈhɪstri ɒv ɑːt/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: Một bài nói chuyện về lịch sử nghệ thuật</font></i>"""
            },
            "raw_script": "Please note that next Monday's history lesson has been moved. Instead, Lecture hall 4 will host a special talk about the history of art given by Professor Evans.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Please note that next Monday's history lesson has been moved. Instead, Lecture hall 4 will host a special talk about the history of art given by Professor Evans.<br>
<small><font color="#4B5563">🎵 IPA: /pliːz noʊt ðæt nɛkst ˈmʌndeɪz ˈhɪstri ˈlɛsn̩ hæz biːn muːvd. ɪnˈstɛd, ˈlɛktʃə hɔːl fɔː wɪl hoʊst ə ˈspɛʃl tɔːk əˈbaʊt ðə ˈhɪstri ɒv ɑːt ˈɡɪvən baɪ prəˈfɛsər ˈɛvənz./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Xin lưu ý rằng tiết học lịch sử thứ Hai tới đã bị dời lại. Thay vào đó, Giảng đường 4 sẽ tổ chức một buổi nói chuyện đặc biệt về lịch sử nghệ thuật do Giáo sư Evans trình bày.</font></i>"""
        },
        {
            "id": 4,
            "type": "Part 2: Thông báo nội bộ trường học (Staff Notice)",
            "correct": "B",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: Where should the teachers park their vehicles tomorrow?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: weə(r) ʃʊd ðə ˈtiːtʃəz pɑːk ðeə(r) ˈvɪəkəlz təˈmɒroʊ/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Các giáo viên nên đỗ xe của họ ở đâu vào ngày mai?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. In the main school yard<br><small><font color="#4B5563">🎵 IPA: /eɪ. ɪn ðə meɪn skuːl jɑːd/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Trong sân trường chính</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. Behind the science building<br><small><font color="#4B5563">🎵 IPA: /biː. bɪˈhaɪnd ðə ˈsaɪəns ˈbɪldɪŋ/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Phía sau tòa nhà khoa học</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. At the public stadium<br><small><font color="#4B5563">🎵 IPA: /siː. æt ðə ˈpʌblɪk ˈsteɪdiəm/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Tại sân vận động công cộng</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. Along the main road<br><small><font color="#4B5563">🎵 IPA: /diː. əˈlɒŋ ðə meɪn roʊd/ </font></small><br><i><font color="#059669">🇻🇳 VIE: Dọc theo đường chính</font></i>"""
            },
            "raw_script": "Attention all staff members. Due to the construction work in the main school yard tomorrow, please park your vehicles behind the science building until further notice.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Attention all staff members. Due to the construction work in the main school yard tomorrow, please park your vehicles behind the science building until further notice.<br>
<small><font color="#4B5563">🎵 IPA: /əˈtɛnʃn̩ ɔːl stɑːf ˈmɛmbəz. djuː tuː ðə kənˈstrʌkʃn̩ wɜrk ɪn ðə meɪn skuːl jɑːd təˈmɒroʊ, pliːz pɑːk jɔː(r) ˈvɪəkəlz bɪˈhaɪnd ðə ˈsaɪəns ˈbɪldɪŋ ʌnˈtɪl ˈfɜːðə(r) ˈnoʊtɪs./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Xin chú ý toàn thể nhân viên. Do công tác xây dựng ở sân trường chính vào ngày mai, vui lòng đỗ xe của bạn phía sau tòa nhà khoa học cho đến khi có thông báo mới.</font></i>"""
        }
    ],
    "2️⃣ VSTEP Đọc": [
        {
            "id": 1,
            "type": "Passage 1: Y học & Đời sống (Epidemics Analysis)",
            "correct": "C",
            "raw_passage": "Diseases are a natural part of life on Earth. If there were no diseases, the human population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%.",
            "passage_html": """<b><font color="#1E3A8A">ENG:</font></b> Context: Diseases are a natural part of life on Earth. If there were no diseases, the human population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%.<br>
<small><font color="#4B5563">🎵 IPA: /ˈkɒntɛkst: dɪˈziːzɪz ɑː(r) ə ˈnætʃrəl pɑːt ɒv laɪf ɒn ɜːθ. ɪf ðeə(r) wɜː(r) noʊ dɪˈziːzɪz, ðə ˈhjuːmən ˌpɒpjuˈleɪʃn̩ wʊd ɡroʊ tuː ˈkwɪkli, ənd ðeə(r) wʊd nɒt biː ɪˈnʌf fuːd. ðə sɪˈvɪə(r) ˈmɑːbɜːɡ ˈvaɪərəs, dɪˈskʌvəd ɪn ˈnaɪntiːn sɪksti-sɛvən, hæz ən ɪkˈstriːmli ˈdeɪndʒərəs fəˈtælɪti reɪt ɒv ˈsɛvənti tuː ˈeɪti pəˈsɛnt./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Ngữ cảnh: Bệnh tật là một phần tự nhiên của cuộc sống trên Trái đất. Nếu không có bệnh tật, dân số loài người sẽ phát triển quá nhanh và sẽ không có đủ lương thực. Loại virus Marburg nghiêm trọng, được phát hiện vào năm 1967, có tỷ lệ tử vong cực kỳ nguy hiểm là 70-80%.</font></i>""",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: According to Passage 1, what is the exact fatality rate of the Marburg virus?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: əˈkɔːdɪŋ tuː ˈpæsɪdʒ wʌn, wɒt ɪz ði ɪɡˈzækt fəˈtælɪti reɪt ɒv ðə ˈmɑːbɜːɡ ˈvaɪərəs?/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Theo Đoạn văn 1, tỷ lệ tử vong chính xác của virus Marburg là bao nhiêu?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. 19%<br><small><font color="#4B5563">🎵 IPA: /eɪ. ˌnaɪnˈtiːn pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: 19 phần trăm</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. 67%<br><small><font color="#4B5563">🎵 IPA: /biː. ˌsɪksti-ˈsɛvən pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: 67 phần trăm</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. 70-80%<br><small><font color="#4B5563">🎵 IPA: /siː. ˈsɛvənti tuː ˈeɪti pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: 70-80 phần trăm</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. Over 90%<br><small><font color="#4B5563">🎵 IPA: /diː. ˈoʊvə(r) ˈnaɪnti pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: Trên 90 phần trăm</font></i>"""
            }
        },
        {
            "id": 2,
            "type": "Passage 1: Y học & Đời sống (Epidemics Analysis)",
            "correct": "B",
            "raw_passage": "Diseases are a natural part of life on Earth. If there were no diseases, the human population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%.",
            "passage_html": """<b><font color="#1E3A8A">ENG:</font></b> Context: Diseases are a natural part of life on Earth. If there were no diseases, the human population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%.<br>
<small><font color="#4B5563">🎵 IPA: /ˈkɒntɛkst: dɪˈziːzɪz ɑː(r) ə ˈnætʃrəl pɑːt ɒv laɪf ɒn ɜːθ. ɪf ðeə(r) wɜː(r) noʊ dɪˈziːzɪz, ðə ˈhjuːmən ˌpɒpjuˈleɪʃn̩ wʊd ɡroʊ tuː ˈkwɪkli, ənd ðeə(r) wʊd nɒt biː ɪˈnʌf fuːd. ðə sɪˈvɪə(r) ˈmɑːbɜːɡ ˈvaɪərəs, dɪˈskʌvəd ɪn ˈnaɪntiːn sɪksti-sɛvən, hæz ən ɪkˈstriːmli ˈdeɪndʒərəs fəˈtælɪti reɪt ɒv ˈsɛvənti tuː ˈeɪti pəˈsɛnt./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Ngữ cảnh: Bệnh tật là một phần tự nhiên của cuộc sống trên Trái đất. Nếu không có bệnh tật, dân số loài người sẽ phát triển quá nhanh và sẽ không có đủ lương thực. Loại virus Marburg nghiêm trọng, được phát hiện vào năm 1967, có tỷ lệ tử vong cực kỳ nguy hiểm là 70-80%.</font></i>""",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: What is the primary natural function of diseases mentioned in the text?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: wɒt ɪz ðə ˈpraɪməri ˈnætʃrəl ˈfʌŋkʃn̩ ɒv dɪˈziːzɪz ˈmɛnʃnd ɪn ðə tɛkst/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Chức năng tự nhiên cốt lõi của bệnh tật được nhắc đến trong đoạn văn là gì?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. To eliminate all food resources<br><small><font color="#4B5563">🎵 IPA: /eɪ. tuː ɪˈlɪmɪneɪt ɔːl fuːd rɪˈzɔːsɪz/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: Để xóa sổ mọi nguồn lương thực</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. To act as a natural check on population growth<br><small><font color="#4B5563">🎵 IPA: /biː. tuː ækt æz ə ˈnætʃrəl tʃɛk ɒn ˌpɒpjuˈleɪʃn̩ ɡroʊθ/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: Để đóng vai trò như một sự kiềm chế tự nhiên đối với sự gia tăng dân số</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. To improve medical laboratory statistics<br><small><font color="#4B5563">🎵 IPA: /siː. tuː ɪmˈpruːv ˈmɛdɪkl ləˈbɒrətəri stəˈtɪstɪks/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: Để cải thiện số liệu thống kê của phòng thí nghiệm y tế</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. To encourage urban migration<br><small><font color="#4B5563">🎵 IPA: /diː. tuː ɪnˈkʌrɪdʒ ˈɜːbən maɪˈɡreɪʃn̩/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: Để khuyến khích di cư đô thị</font></i>"""
            }
        },
        {
            "id": 3,
            "type": "Passage 2: Văn hóa & Trang phục (Japanese Dress Culture)",
            "correct": "B",
            "raw_passage": "Kimonos came to Japan from China originally as an undergarment. It later evolved into a traditional T-shaped outer robe. This traditional clothing is securely fastened around the waist with a wide decorative sash known as the Obi belt.",
            "passage_html": """<b><font color="#1E3A8A">ENG:</font></b> Context: Kimonos came to Japan from China originally as an undergarment. It later evolved into a traditional T-shaped outer robe. This traditional clothing is securely fastened around the waist with a wide decorative sash known as the Obi belt.<br>
<small><font color="#4B5563">🎵 IPA: /ˈkɒntɛkst: kɪˈmoʊnoʊz keɪm tuː dʒəˈpæn frɒm ˈtʃaɪnə əˈrɪdʒənəli æz ân ˈʌndə(r)ˌɡɑːmənt. ɪt ˈleɪtər ɪˈvɒlvd ˈɪntuː ə trəˈdɪʃənl tiː-ʃeɪpt ˈaʊtə(r) roʊb. ðɪs trəˈdɪʃənl ˈkloʊðɪŋ ɪz sɪˈkjuə(r)li ˈfɑːsnd əˈraʊnd ðə weɪst wɪð ə waɪd ˈdɛkərətɪv sæʃ noʊn æz ði ˈoʊbi bɛlt./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Ngữ cảnh: Kimono đến Nhật Bản từ Trung Quốc ban đầu như một loại áo lót. Sau đó nó phát triển thành một loại áo choàng ngoài hình chữ T truyền thống. Trang phục truyền thống này được thắt chặt an toàn quanh eo bằng một chiếc khăn thắt lưng trang trí rộng bản được gọi là thắt lưng Obi.</font></i>""",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: Where did the Kimono dress originally come from before evolving in Japan?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: weə(r) dɪd ðə kɪˈmoʊnoʊ drɛs əˈrɪdʒənəli kʌm frɒm bɪˈfɔː(r) ɪˈvɒlvɪŋ ɪn dʒəˈpæn?/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Trang phục Kimono ban đầu đến từ đâu trước khi phát triển ở Nhật Bản?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. Japan<br><small><font color="#4B5563">🎵 IPA: /eɪ. dʒəˈpæn/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: Nhật Bản</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. China<br><small><font color="#4B5563">🎵 IPA: /biː. ˈtʃaɪnə/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: Trung Quốc</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. Korea<br><small><font color="#4B5563">🎵 IPA: /siː. kəˈriːə/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: Hàn Quốc</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. Austria<br><small><font color="#4B5563">🎵 IPA: /diː. ˈɒstriə/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: Áo</font></i>"""
            }
        },
        {
            "id": 4,
            "type": "Passage 2: Văn hóa & Trang phục (Japanese Dress Culture)",
            "correct": "C",
            "raw_passage": "Kimonos came to Japan from China originally as an undergarment. It later evolved into a traditional T-shaped outer robe. This traditional clothing is securely fastened around the waist with a wide decorative sash known as the Obi belt.",
            "passage_html": """<b><font color="#1E3A8A">ENG:</font></b> Context: Kimonos came to Japan from China originally as an undergarment. It later evolved into a traditional T-shaped outer robe. This traditional clothing is securely fastened around the waist with a wide decorative sash known as the Obi belt.<br>
<small><font color="#4B5563">🎵 IPA: /ˈkɒntɛkst: kɪˈmoʊnoʊz keɪm tuː dʒəˈpæn frɒm ˈtʃaɪnə əˈrɪdʒənəli æz ân ˈʌndə(r)ˌɡɑːmənt. ɪt ˈleɪtər ɪˈvɒlvd ˈɪntuː ə trəˈdɪʃənl tiː-ʃeɪpt ˈaʊtə(r) roʊb. ðɪs trəˈdɪʃənl ˈkloʊðɪŋ ɪz sɪˈkjuə(r)li ˈfɑːsnd əˈraʊnd ðə weɪst wɪð ə waɪd ˈdɛkərətɪv½ sæʃ noʊn æz ði ˈoʊbi bɛlt./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Ngữ cảnh: Kimono đến Nhật Bản từ Trung Quốc ban đầu như một loại áo lót. Sau đó nó phát triển thành một loại áo choàng ngoài hình chữ T truyền thống. Trang phục truyền thống này được thắt chặt an toàn quanh eo bằng một chiếc khăn thắt lưng trang trí rộng bản được gọi là thắt lưng Obi.</font></i>""",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> Question: What is the primary mechanical function of the wide Obi belt?<br>
<small><font color="#4B5563">🎵 IPA: /ˈkwɛstʃən: wɒt ɪz ðə ˈpraɪməri mɪˈkænɪkl ˈfʌŋkʃn̩ ɒv ðə waɪd ˈoʊbi bɛlt?/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Câu hỏi: Chức năng cơ học chính của chiếc thắt lưng Obi bản rộng là gì?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> A. To keep the neck area warm<br><small><font color="#4B5563">🎵 IPA: /eɪ. tuː kiːp ðə nɛk ˈeəriə wɔːm/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án A: Để giữ ấm cho vùng cổ</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> B. To cover the wearer's head<br><small><font color="#4B5563">🎵 IPA: /biː. tuː ˈkʌvə(r) ðə ˈweərəz hɛd/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án B: Để che đầu người mặc</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> C. To securely fasten the T-shaped robe around the waist<br><small><font color="#4B5563">🎵 IPA: /siː. tuː sɪˈkjuə(r)li ˈfɑːsnd ðə tiː-ʃeɪpt roʊb əˈraʊnd ðə weɪst/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án C: Để thắt chặt an toàn chiếc áo choàng hình chữ T quanh eo</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> D. To serve exclusively as an inner garment<br><small><font color="#4B5563">🎵 IPA: /diː. tuː sɜːv ɪkˈskluːsɪvli æz ân ˈɪnə(r) ˈɡɑːmənt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Phương án D: Để phục vụ duy nhất như một trang phục bên trong</font></i>"""
            }
        }
    ],
    "3️⃣ VSTEP Viết": [
        {
            "id": 1,
            "type": "Task 1: Viết thư hồi đáp công việc (Informal Email Interaction)",
            "prompt_html": """<b><font color="#1E3A8A">ENG:</font></b> Prompt: You received an email from Jane asking about your friend An, who is planning to take a short English summer course in London. Write a reply email to provide details about his accommodation arrangements and arrival schedule.<br>
<small><font color="#4B5563">🎵 IPA: /prɒmpt: juː rɪˈsiːvd ân ˈiːmeɪl frɒm dʒeɪn ˈɑːskɪŋ əˈbaʊt jɔː(r) frɛnd æn, huː ɪz ˈplænɪŋ tuː teɪk ə ʃɔːt ˈɪŋɡlɪʃ ˈsʌmər kɔːs ɪn ˈlʌndən. raɪt ə rɪˈplaɪ ˈiːmeɪl tuː prəˈvaɪd ˈdiːteɪlz əˈbaʊt hɪz əˌkɒməˈdeɪʃn̩ əˈreɪndʒmənts ənd əˈraɪvl ˈʃɛdjuːl./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Đề bài: Bạn đã nhận được một email từ Jane hỏi về người bạn của bạn tên An, người đang lên kế hoạch tham gia một khóa học hè tiếng Anh ngắn hạn ở Luân Đôn. Hãy viết một email trả lời để cung cấp chi tiết về việc sắp xếp chỗ ở và lịch trình đến của anh ấy.</font></i>""",
            "template": "Dear Jane,\n\nI am writing to inform you that An has finalized his summer course plan...\n\nBest regards,\n[Your Name]"
        }
    ],
    "4️⃣ VSTEP Nói": [
        {
            "id": 1,
            "type": "Part 1: Tương tác xã hội phản xạ (Social Interaction)",
            "prompt_html": """<b><font color="#1E3A8A">ENG:</font></b> Prompt: Let's talk about your free time activities. What TV channels do you prefer to watch? Do you like reading books in your spare time? Why or why not?<br>
<small><font color="#4B5563">🎵 IPA: /prɒmpt: lɛts tɔːk əˈbaʊt jɔː(r) friː taɪm ækˈtɪvətiz. wɒt ˌtiːˈviː ˈtʃænlz duː juː prɪˈfɜː(r) tuː wɒtʃ? duː juː laɪk ˈriːdɪŋ bʊks ɪn jɔː(r) speə(r) taɪm? waɪ ɔː(r) nɒt/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Đề bài: Hãy trò chuyện về các hoạt động lúc rảnh rỗi của bạn. Bạn thích xem những kênh truyền hình nào hơn? Bạn có thích đọc sách vào thời gian rảnh rỗi không? Tại sao có hoặc tại sao không?</font></i>"""
        }
    ]
}

# CHỈ THỊ ÉP ĐỊNH DẠNG TUYỆT ĐỐI 3 DÒNG INTERLINEAR CHO HỆ THỐNG PHÂN TÍCH
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the elite "VSTEP Master Trainer" specialized in rapid remediation for learners who lost their English roots (người mất gốc). Address the user respectfully as "thầy cô".

# UNIVERSAL COMPACT INTERLINEAR RULE (CRITICAL ABSOLUTE MANDATE)
Every single piece of English text, sample sentence, example, correction text, or alternative reference question that you output MUST strictly follow this 3-line interlinear layout with hard `<br>` break tags. No running text or inline English words allowed without transcription and translation:
<b><font color="#1E3A8A">ENG:</font></b> [English Text]<br>
<small><font color="#4B5563">🎵 IPA: /[Standard International Phonetic Alphabet chunk pauses]/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: [Dịch Nghĩa Tiếng Việt Bình Dân Dễ Hiểu Nhất]</font></i>

# EXPANDER DIEN_GIAI PACKAGING PROTOCOL WITH MANDATORY INTERLINEAR REFERENCES
You MUST bundle your entire feedback analytical breakdown strictly inside `[DIEN_GIAI_START]` and `[DIEN_GIAI_END]` tags. Inside, render this exact scannable structure:

<b>[🎯 ĐÁP ÁN ĐÚNG / ĐÁNH GIÁ CHUYÊN GIA]</b>: <Provide score alignment or grammatical evaluation in 1 clear sentence>

<b>[🎧 CỤM TỪ VÀNG CẦN CHÚ Ý - VSTEP KEYWORDS]</b>
• <b>[Keyword/Phrase]</b>: [Nghĩa Việt] -> [Concise neuro-linguistic anchoring explanation].

<b>[🧠 SƠ ĐỒ TƯ DUY CẤU TRÚC - MIND MAP]</b>
📌 CẤU TRÚC CÂU GỐC
├── 🔑 Từ khóa cốt lõi: [Từ] -> [Nghĩa]
└── 🧱 Thành phần ngữ pháp chính:
    ├── S (Chủ ngữ): [Từ]
    ├── V (Động từ): [Từ]
    └── O (Tân ngữ): [Từ]

<b>[⚠️ BẪY ĐỀ THI - MẤT GỐC CẦN TRÁNH]</b>: <Explain traps concisely using simple rules>
<b>[⏳ TRA CỨU THÌ QUÁ KHỨ - GỐC TỪ]</b>: <Map past verbs to infinitive form: "• <b>past_verb</b> là quá khứ của <b>infinitive_verb</b> (nghĩa)">

<b>[📚 CÂU HỎI THAM KHẢO PHÁT TRIỂN NĂNG LỰC - PRACTICE VARIANT MATRIX]</b>
Provide exactly 2 parallel practice questions relevant to the target context. 
CRITICAL RULES FOR PRACTICE QUESTIONS:
1. You MUST enclose the English question stem inside `[AUDIO_START] ... [AUDIO_END]` tags to trigger an independent media player directly under the question stem.
2. Every question stem (including labels like Question:) and all multiple-choice options (A, B, C, D) MUST follow the strict 3-line interlinear format (ENG, IPA, VIE) independently with hard <br> breaks.
3. Explicitly state the correct answer key and a 1-sentence translation guide.
"""

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

MODEL_NAME = "gemini-2.5-flash"

# HỆ THỐNG QUẢN LÝ TRẠNG THÁI KHẢO THÍ TOÀN DIỆN (PERSISTENT STATE ENGINE)
if "current_section" not in st.session_state:
    st.session_state.current_section = "1️⃣ VSTEP Nghe"
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "mic_key" not in st.session_state:
    st.session_state.mic_key = 0
if "submitted_state" not in st.session_state:
    st.session_state.submitted_state = {}
if "saved_explanations" not in st.session_state:
    st.session_state.saved_explanations = {}

# THÀNH PHẦN ĐIỀU HÀNH BÊN SƯỜN GIAO DIỆN (NẠP LỆNH RERUN KHÓA CHỐNG ĐƠ)
st.sidebar.title("🎓 TRUNG TÂM ĐIỀU HÀNH VSTEP")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Nhập mã truy cập hệ thống:", type="password")

st.sidebar.markdown("### 📁 BỘ CHỌN MÃ ĐỀ LUYỆN THI")
selected_de = st.sidebar.selectbox(
    "Chọn Mã đề thi thực chiến:",
    ["Mã đề VSTEP-2026-A (Đề Minh Họa Chuẩn)", "Mã đề VSTEP-2026-B (Biến Thể Song Song)", "Mã đề VSTEP-2026-C (Nâng Cao Chuyên Sâu)"]
)

font_size = st.sidebar.slider("Kích thước chữ hiển thị", 14, 24, 16)
st.markdown(f"<style>.stMarkdown, p, li, .stChatMessage {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)

st.sidebar.markdown("### 🔢 PHẦN THI CHUYÊN BIỆT")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.sidebar.button("1️⃣ VSTEP Nghe", use_container_width=True):
        st.session_state.current_section = "1️⃣ VSTEP Nghe"
        st.session_state.current_q_idx = 0
        st.rerun()
with col_s2:
    if st.sidebar.button("2️⃣ VSTEP Đọc", use_container_width=True):
        st.session_state.current_section = "2️⃣ VSTEP Đọc"
        st.session_state.current_q_idx = 0
        st.rerun()
col_s3, col_s4 = st.sidebar.columns(2)
with col_s3:
    if st.sidebar.button("3️⃣ VSTEP Viết", use_container_width=True):
        st.session_state.current_section = "3️⃣ VSTEP Viết"
        st.session_state.current_q_idx = 0
        st.rerun()
with col_s4:
    if st.sidebar.button("4️⃣ VSTEP Nói", use_container_width=True):
        st.session_state.current_section = "4️⃣ VSTEP Nói"
        st.session_state.current_q_idx = 0
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 ĐIỀU HƯỚNG CÂU HỎI (TIẾN LÙI TỰ DO)")

questions_list = VSTEP_EXAM_DB[st.session_state.current_section]
max_questions = len(questions_list)

col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    if st.button("⏮️ CÂU TRƯỚC", use_container_width=True):
        st.session_state.current_q_idx = max(st.session_state.current_q_idx - 1, 0)
        st.rerun()
with col_next:
    if st.button("⏭️ CÂU TIẾP", use_container_width=True):
        st.session_state.current_q_idx = min(st.session_state.current_q_idx + 1, max_questions - 1)
        st.rerun()

if st.sidebar.button("🔄 KHỞI ĐỘNG LẠI PHÒNG THI", use_container_width=True):
    st.session_state.current_section = "1️⃣ VSTEP Nghe"
    st.session_state.current_q_idx = 0
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.messages = []
    st.session_state.mic_key += 1
    st.session_state.submitted_state.clear()
    st.session_state.saved_explanations.clear()
    st.rerun()

# KHÔNG GIAN KHẢO THÍ SỐ HÓA VSTEP CHÍNH DIỆN
st.title("🎓 HỆ THỐNG KHẢO SÁT NĂNG LỰC TIẾNG ANH VSTEP")
st.caption(f"Cơ sở hạ tầng Master Blueprint quy chuẩn | Đang vận hành: {selected_de}")
st.markdown("---")

# ĐỒNG HỒ ĐẾM NGƯỢC VÀ THANH TIẾN ĐỘ THỰC TẾ TRÊN GIAO DIỆN
elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(50 * 60 - elapsed_time, 0)
mins, secs = divmod(int(remaining_time), 60)

dash_col1, dash_col2, dash_col3 = st.columns(3)
with dash_col1:
    st.markdown(f"**📊 PHẦN THI HIỆN TẠI: {st.session_state.current_section}**")
    st.progress((st.session_state.current_q_idx + 1) / max_questions)
    st.caption(f"Tiến độ: Câu {st.session_state.current_q_idx + 1} trên tổng số {max_questions} mục tiêu.")
with dash_col2:
    st.metric(label="💯 Điểm Số Đạt Được", value=f"{st.session_state.score} Điểm")
with dash_col3:
    st.metric(label="⏳ Đồng Hồ Đếm Ngược", value=f"{mins:02d}:{secs:02d} Phút")

st.markdown("---")

# TRÍCH XUẤT ĐỐI TƯỢNG ĐỀ BÀI HIỆN TẠI TỪ CƠ SỞ DỮ LIỆU PYTHON
active_q = questions_list[st.session_state.current_q_idx]
q_key = f"{selected_de}_{st.session_state.current_section}_{active_q['id']}"
is_submitted = q_key in st.session_state.submitted_state

# LUỒNG HIỂN THỊ TỰ ĐỘNG KÍCH HOẠT VÀ NẠP THANH PHÁT AUDIO LUYỆN ĐỌC/NGHE ĐỘC LẬP
if st.session_state.current_section == "1️⃣ VSTEP Nghe":
    st.info("🎧 **Nội dung nghe ghi âm mẫu chuyên nghiệp:**")
    tts_main = gTTS(text=active_q["raw_script"], lang='en', tld='com')
    fp_main = io.BytesIO()
    tts_main.write_to_fp(fp_main)
    fp_main.seek(0)
    st.audio(fp_main, format="audio/mp3")
    
    if is_submitted:
        st.success("=== VĂN BẢN BÓC BĂNG ÂM THANH (AUDIO SCRIPT) CHUẨN 3 DÒNG TỐI CAO ===")
        st.markdown(active_q["script_html"], unsafe_allow_html=True)
        st.markdown("=========================================================")

    st.markdown("**Nội dung câu hỏi khảo thí:**")
    st.markdown(active_q["question_html"], unsafe_allow_html=True)

elif st.session_state.current_section == "2️⃣ VSTEP Đọc":
    st.success("=== ĐOẠN VĂN NỀN ĐỌC HIỂU HOÀN CHỈNH (PASSAGE CONTEXT) CHUẨN 3 DÒNG ===")
    st.markdown(active_q["passage_html"], unsafe_allow_html=True)
    st.markdown("=========================================================")
    
    # KÍCH HOẠT THANH PHÁT NHẠC LUYỆN ĐỌC PHÂN HỆ ĐỌC ĐÚNG THEO CHỈ THỊ
    st.info("🎵 **Thành phần hỗ trợ luyện đọc - Hãy bấm nút phát nhạc bên dưới để nghe mẫu và đối chiếu chính xác:**")
    tts_read = gTTS(text=active_q["raw_passage"], lang='en', tld='com')
    fp_read = io.BytesIO()
    tts_read.write_to_fp(fp_read)
    fp_read.seek(0)
    st.audio(fp_read, format="audio/mp3")
    st.markdown("---")
    
    st.markdown("**Nội dung câu hỏi khảo thí:**")
    st.markdown(active_q["question_html"], unsafe_allow_html=True)

elif st.session_state.current_section in ["3️⃣ VSTEP Viết", "4️⃣ VSTEP Nói"]:
    st.warning("📊 **Yêu cầu phân hệ khảo sát tự luận:**")
    st.markdown(active_q["prompt_html"], unsafe_allow_html=True)
    if st.session_state.current_section == "3️⃣ VSTEP Viết":
        with st.expander("💡 Khung cấu trúc câu gợi ý (Sentence Scaffolding Templates)"):
            st.code(active_q.get("template", ""), language="markdown")
        if not is_submitted:
            user_essay = st.text_area("Nhập nội dung bài viết tự luận của thầy cô tại đây:", height=250, key=f"write_area_{active_q['id']}")
            if st.button("🚀 XÁC NHẬN NỘP BÀI TỰ LUẬN", use_container_width=True):
                if not api_key:
                    st.sidebar.error("Vui lòng nhập mã truy cập hệ thống.")
                else:
                    st.session_state.submitted_state[q_key] = user_essay
                    eval_prompt = f"Học viên nộp bài tự luận viết cho đề bài. Hãy sửa sai cấu trúc và xuất khối [DIEN_GIAI] chuẩn 3 dòng có kèm bộ câu hỏi luyện tập có audio đầy đủ."
                    with st.spinner("Hệ thống đang thẩm định..."):
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(MODEL_NAME, system_instruction=MASTER_PROMPT, safety_settings=SAFETY_SETTINGS)
                        response = model.generate_content(eval_prompt)
                        try:
                            res_text = response.candidates[0].content.parts[0].text
                        except:
                            res_text = "⚠️ Trục trặc kết nối, vui lòng thử lại."
                        st.session_state.saved_explanations[q_key] = res_text
                        st.rerun()
        else:
            st.info("Bài làm tự luận đã được ghi nhận trên hệ thống.")
            st.markdown(f"> *{st.session_state.submitted_state[q_key]}*")

# THUẬT TOÁN ĐỒ HỌA HOÁN ĐỔI MÀU SẮC ĐÁP ÁN ĐÚNG SANG XANH LỤC SAU KHI CLICK CHỌN (KHÔNG CẦN NÚT TRUNG GIAN)
if st.session_state.current_section in ["1️⃣ VSTEP Nghe", "2️⃣ VSTEP Đọc"]:
    options_keys = list(active_q["options_html"].keys())
    
    if not is_submitted:
        st.markdown("---")
        st.markdown("**Mời thầy cô xem chi tiết nội dung các phương án lựa chọn bên dưới (ENG - IPA - VIE):**")
        for key, html_val in active_q["options_html"].items():
            st.markdown(f"<div style='background-color:#F8FAFC; border-left:4px solid #1E3A8A; padding:8px; border-radius:4px; margin-bottom:12px;'>{html_val}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        selected_option = st.radio(
            "Đánh dấu vào ô tròn phía trước chữ cái tương ứng để đưa ra câu trả lời:",
            ["-- Hãy chọn một đáp án / Select your option --"] + options_keys,
            format_func=lambda x: x if x == "-- Hãy chọn một đáp án / Select your option --" else f"Chọn phương án {x}",
            key=f"radio_mcq_{active_q['id']}"
        )
        
        if selected_option != "-- Hãy chọn một đáp án / Select your option --":
            st.session_state.submitted_state[q_key] = selected_option
            is_correct = (selected_option == active_q["correct"])
            score_tag = "[SCORE_UP]" if is_correct else ""
            
            eval_prompt = f"""
            Học viên đang làm đề {selected_de}, kỹ năng {st.session_state.current_section}, câu hỏi id {active_q['id']}.
            Đáp án đúng của hệ thống là: {active_q['correct']}. Học viên chọn phương án: {selected_option}.
            Hãy xuất ra kết quả phân tích chuẩn hóa. Nếu đúng chèn thẻ {score_tag}.
            Áp dụng quy tắc cưỡng bách 3 dòng interlinear cho toàn bộ văn bản giải thích.
            Đóng gói phần bóc tách sơ đồ tư duy, từ khóa vàng định vị thính giác và phần CÂU HỎI THAM KHẢO BIẾN THỂ (mỗi câu bọc trong cặp thẻ AUDIO_START và AUDIO_END để tạo audio phát âm) vào cặp thẻ [DIEN_GIAI_START] và [DIEN_GIAI_END]. Mọi dòng chữ tiếng Anh xuất hiện trong bài tập bổ sung, kể cả các nhãn dạng 'Question:', phải có phiên âm và dịch nghĩa 3 dòng tuyệt đối với thẻ <br> cứng.
            """
            
            if not api_key:
                st.sidebar.error("Vui lòng cung cấp mã truy cập hệ thống tại thanh bên dọc.")
            else:
                with st.spinner("Hệ thống đang đối chiếu dữ liệu..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(MODEL_NAME, system_instruction=MASTER_PROMPT, safety_settings=SAFETY_SETTINGS)
                        response = model.generate_content(eval_prompt)
                        res_text = response.candidates[0].content.parts[0].text
                        
                        if "[SCORE_UP]" in res_text:
                            if "scored_questions" not in st.session_state:
                                st.session_state.scored_questions = set()
                            if q_key not in st.session_state.scored_questions:
                                st.session_state.score += 10
                                st.session_state.scored_questions.add(q_key)
                                
                        st.session_state.saved_explanations[q_key] = res_text
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi truyền tải phân tích: {e}")
    else:
        st.markdown("**Trạng thái đối chiếu phương án đồ hóa sau khi nộp:**")
        for key, html_val in active_q["options_html"].items():
            if key == active_q["correct"]:
                st.markdown(f"<div style='border:2px solid #2E7D32; background-color:#E8F5E9; padding:10px; border-radius:5px; margin-bottom:10px;'><b>✔ PHƯƠNG ÁN ĐÚNG CHUẨN XÁC:</b><br>{html_val}</div>", unsafe_allow_html=True)
            elif key == st.session_state.submitted_state[q_key] and st.session_state.submitted_state[q_key] != active_q["correct"]:
                st.markdown(f"<div style='border:2px solid #D32F2F; background-color:#FFEBEE; padding:10px; border-radius:5px; margin-bottom:10px;'><b>✘ LỰA CHỌN CỦA THẦY CÔ:</b><br>{html_val}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='border:1px solid #E5E7EB; padding:10px; border-radius:5px; margin-bottom:10px;'><b>Phương án {key}:</b><br>{html_val}</div>", unsafe_allow_html=True)

st.markdown("---")

# THUẬT TOÁN ĐIỀU HÀNH CHUYỂN ĐỔI MÃ AUDIO NỘI HÀM THÀNH THANH PHÁT TRỰC QUAN CHUYÊN BIỆT
def process_inline_audio(text):
    pattern = r"\[AUDIO_START\](.*?)\[AUDIO_END\]"
    matches = re.findall(pattern, text)
    for match in matches:
        phrase = match.strip()
        if phrase:
            try:
                clean_phrase = re.sub('<[^<]+?>', '', phrase)
                clean_phrase = clean_phrase.replace("ENG:", "").replace("IPA:", "").replace("VIE:", "").strip()
                clean_phrase = clean_phrase.replace("Question:", "").replace("Question Context:", "").strip()
                tts = gTTS(text=clean_phrase, lang='en', tld='com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                b64_audio = base64.b64encode(fp.read()).decode()
                audio_html = f'<audio controls src="data:audio/mp3;base64,{b64_audio}" style="width: 100%; max-width: 340px; display: block; margin-top: 6px; margin-bottom: 12px;"></audio>'
                text = text.replace(f"[AUDIO_START]{match}[AUDIO_END]", audio_html)
            except Exception as e:
                text = text.replace(f"[AUDIO_START]{match}[AUDIO_END]", f"*(Trục trặc tải âm thanh: {e})*")
    return text

def render_custom_vstep_message(content):
    clean_content = content
    dien_giai_text = ""
    if "[DIEN_GIAI_START]" in content and "[DIEN_GIAI_END]" in content:
        start_dg = content.find("[DIEN_GIAI_START]")
        end_dg = content.find("[DIEN_GIAI_END]")
        dien_giai_text = content[start_dg + len("[DIEN_GIAI_START]"):end_dg].strip()
        clean_content = content.replace(content[start_dg:end_dg + len("[DIEN_GIAI_END]")], "")
    
    visible_content = clean_content.replace("[SCORE_UP]", "")
    visible_content = process_inline_audio(visible_content)
    st.markdown(visible_content, unsafe_allow_html=True)
    
    if dien_giai_text:
        dien_giai_text = process_inline_audio(dien_giai_text)
        with st.expander("=== THÀNH PHẦN MỞ RỘNG: SƠ ĐỒ TƯ DUY, CỤM TỪ VÀNG & CÂU HỎI THAM KHẢO ==="):
            st.markdown(dien_giai_text, unsafe_allow_html=True)

# LUỒNG HIỂN THỊ LẠI TOÀN BỘ THÔNG TIN BÀI GIẢI VÀ THÀNH PHẦN MỞ RỘNG KHI ĐÃ QUA LƯỢT NỘP
if is_submitted and q_key in st.session_state.saved_explanations:
    st.markdown("### 🔔 KẾT QUẢ KIỂM ĐỊNH TỪ HỆ THỐNG CHUYÊN GIA:")
    render_custom_vstep_message(st.session_state.saved_explanations[q_key])

# THUẬT TOÁN THU ÂM VÀ XỬ LÝ PHÂN HỆ NÓI TRỰC TIẾP TỪ THANH BÊN (SỬ DỤNG PHƯƠNG THỨC PHẲNG NHỊ PHÂN)
audio_data = st.sidebar.audio_input(
    "Ghi âm trực tiếp bài nói phản xạ:",
    key=f"mic_widget_{st.session_state.mic_key}"
)

if audio_data is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI VSTEP", use_container_width=True):
        if not api_key:
            st.sidebar.error("Vui lòng điền mã trực lưu hệ thống.")
        else:
            vstep_speech_command = f"Đây là file ghi âm bài nói micro của tôi tại câu số {active_q['id']} phần {st.session_state.current_section}. Hãy bóc băng âm thanh và xuất khối diễn giải 3 dòng interlinear bao gồm cả ma trận câu hỏi tham khảo phụ có phiên âm đầy đủ."
            with st.spinner("Hệ thống đang phân tách ngôn ngữ thính giác..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(MODEL_NAME, system_instruction=MASTER_PROMPT, safety_settings=SAFETY_SETTINGS)
                    contents = [{"mime_type": audio_data.type or "audio/wav", "data": audio_data.getvalue()}, vstep_speech_command]
                    response = model.generate_content(contents=contents)
                    res_text = response.candidates[0].content.parts[0].text
                    
                    st.session_state.submitted_state[q_key] = "Đã nộp dữ liệu âm thanh thành công."
                    st.session_state.saved_explanations[q_key] = res_text
                    st.session_state.mic_key += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Trục trặc xử lý tệp âm thanh đầu vào: {e}")
