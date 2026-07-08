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

# KHO DỮ LIỆU ĐỀ THI CỐ ĐỊNH ĐÃ ĐƯỢC MÃ HÓA 3 DÒNG INTERLINEAR TUYỆT ĐỐI TỪ GỐC
VSTEP_EXAM_DB = {
    "1️⃣ VSTEP Nghe": [
        {
            "id": 1,
            "type": "Part 1: Thông báo ngắn (Short Announcement)",
            "correct": "D",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> How many languages are taught at Hanoi International Language School?<br>
<small><font color="#4B5563">🎵 IPA: /haʊ ˈmɛni ˈlæŋɡwɪdʒɪz ɑː(r) tɔːt æt ˌhæˈnɔɪ ˌɪntə(r)ˈnæʃnəl ˈlæŋɡwɪdʒ skuːl/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Có bao nhiêu ngôn ngữ được giảng dạy tại Trường Ngôn ngữ Quốc tế Hà Nội?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> 1<br><small><font color="#4B5563">🎵 IPA: /wʌn/</font></small><br><i><font color="#059669">🇻🇳 VIE: 1 ngôn ngữ</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> 2<br><small><font color="#4B5563">🎵 IPA: /tuː/</font></small><br><i><font color="#059669">🇻🇳 VIE: 2 ngôn ngữ</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> 3<br><small><font color="#4B5563">🎵 IPA: /θriː/</font></small><br><i><font color="#059669">🇻🇳 VIE: 3 ngôn ngữ</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> 4<br><small><font color="#4B5563">🎵 IPA: /fɔː(r)/</font></small><br><i><font color="#059669">🇻🇳 VIE: 4 ngôn ngữ</font></i>"""
            },
            "raw_script": "Welcome to Hanoi International Language School. This semester, our institution is proud to offer official certification courses in four distinct languages: English, French, Japanese, and Korean.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Welcome to Hanoi International Language School. This semester, our institution is proud to offer official certification courses in four distinct languages: English, French, Japanese, and Korean.<br>
<small><font color="#4B5563">🎵 IPA: /ˈwɛlkəm tuː ˌhæˈnɔɪ ˌɪntə(r)ˈnæʃnəl ˈlæŋɡwɪdʒ skuːl. ðɪs sɪˈmɛstə(r), ˈaʊə(r) ˌɪnstɪˈtjuːʃn̩ ɪz praʊd tuː ˈɒfə(r) əˈfɪʃl ˌsɜːtɪfɪˈkeɪʃn̩ ˈkɔːsɪz ɪn fɔː(r) dɪˈstɪŋkt ˈlæŋɡwɪdʒɪz: ˈɪŋɡlɪʃ, frɛntʃ, ˌdʒæpəˈniːz, ənd kəˈriːən./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Chào mừng đến với Trường Ngôn ngữ Quốc tế Hà Nội. Học kỳ này, cơ sở của chúng tôi tự hào cung cấp các khóa học chứng chỉ chính thức bằng bốn ngôn ngữ riêng biệt: Tiếng Anh, Tiếng Pháp, Tiếng Nhật và Tiếng Hàn.</font></i>"""
        },
        {
            "id": 2,
            "type": "Part 1: Hướng dẫn bay (Airport Announcement)",
            "correct": "B",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> What is the boarding time of Flight VN178?<br>
<small><font color="#4B5563">🎵 IPA: /wɒt ɪz ðə ˈbɔːdɪŋ taɪm ɒv flaɪt viː-ɛn-wʌn-sɛvən-eɪt/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Giờ lên máy bay của Chuyến bay VN178 là mấy giờ?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> 3:30<br><small><font color="#4B5563">🎵 IPA: /θriː ˈθɜːti/</font></small><br><i><font color="#059669">🇻🇳 VIE: 3 giờ 30 phút</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> 3:45<br><small><font color="#4B5563">🎵 IPA: /θriː fɔːti-faɪv/</font></small><br><i><font color="#059669">🇻🇳 VIE: 3 giờ 45 phút</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> 4:15<br><small><font color="#4B5563">🎵 IPA: /fɔː(r) fɪfˈtiːn/</font></small><br><i><font color="#059669">🇻🇳 VIE: 4 giờ 15 phút</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> 4:45<br><small><font color="#4B5563">🎵 IPA: /fɔː(r) fɔːti-faɪv/</font></small><br><i><font color="#059669">🇻🇳 VIE: 4 giờ 45 phút</font></i>"""
            },
            "raw_script": "Attention all passengers traveling on Flight VN178 to Ho Chi Minh City. Due to the late arrival of the incoming aircraft, the boarding time has been rescheduled from 3:30 to 3:45. Please gather at Gate 4 immediately.",
            "script_html": """<b><font color="#1E3A8A">ENG:</font></b> Attention all passengers traveling on Flight VN178 to Ho Chi Minh City. Due to the late arrival of the incoming aircraft, the boarding time has been rescheduled from 3:30 to 3:45. Please gather at Gate 4 immediately.<br>
<small><font color="#4B5563">🎵 IPA: /əˈtɛnʃn̩ ɔːl ˈpæsɪndʒəz ˈtrævəlɪŋ ɒn flaɪt viː-ɛn-wʌn-sɛvən-eɪt tuː hoʊ tʃiː mɪn ˈsɪti. djuː tuː ðə leɪt əˈraɪvl ɒv ði ˈɪnˌkʌmɪŋ ˈeəkrɑːft, ðə ˈbɔːdɪŋ taɪm hæz biːn ˌriːˈʃɛdjuːld frɒm θriː θɜːti tuː θriː fɔːti-faɪv. pliːz ˈɡæðə(r) æt ɡeɪt fɔː(r) ɪˈmiːdiətli./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Xin chú ý tất cả hành khách đi trên Chuyến bay VN178 đến Thành phố Hồ Chí Minh. Do máy bay đến muộn, giờ lên máy bay đã được thay đổi từ 3:30 sang 3:45. Xin vui lòng tập trung tại Cửa số 4 ngay lập tức.</font></i>"""
        }
    ],
    "2️⃣ VSTEP Đọc": [
        {
            "id": 1,
            "type": "Passage 1: Y học & Đời sống (Epidemics Analysis)",
            "correct": "C",
            "passage_html": """<b><font color="#1E3A8A">ENG:</font></b> Diseases are a natural part of life on Earth. If there were no diseases, the human population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%.<br>
<small><font color="#4B5563">🎵 IPA: /dɪˈziːzɪz ɑː(r) ə ˈnætʃrəl pɑːt ɒv laɪf ɒn ɜːθ. ɪf ðeə(r) wɜː(r) noʊ dɪˈziːzɪz, ðə ˈhjuːmən ˌpɒpjuˈleɪʃn̩ wʊd ɡroʊ tuː ˈkwɪkli, ənd ðeə(r) wʊd nɒt biː ɪˈnʌf fuːd. ðə sɪˈvɪə(r) ˈmɑːbɜːɡ ˈvaɪərəs, dɪˈskʌvəd ɪn ˈnaɪntiːn sɪksti-sɛvən, hæz ən ɪkˈstriːmli ˈdeɪndʒərəs fəˈtælɪti reɪt ɒv ˈsɛvənti tuː ˈeɪti pəˈsɛnt./</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Bệnh tật là một phần tự nhiên của cuộc sống trên Trái đất. Nếu không có bệnh tật, dân số loài người sẽ phát triển quá nhanh và sẽ không có đủ lương thực. Loại virus Marburg nghiêm trọng, được phát hiện vào năm 1967, có tỷ lệ tử vong cực kỳ nguy hiểm là 70-80%.</font></i>""",
            "question_html": """<b><font color="#1E3A8A">ENG:</font></b> According to Passage 1, what is the exact fatality rate of the Marburg virus?<br>
<small><font color="#4B5563">🎵 IPA: /əˈkɔːdɪŋ tuː ˈpæsɪdʒ wʌn, wɒt ɪz ði ɪɡˈzækt fəˈtælɪti reɪt ɒv ðə ˈmɑːbɜːɡ ˈvaɪərəs?/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: Theo Đoạn văn 1, tỷ lệ tử vong chính xác của virus Marburg là bao nhiêu?</font></i>""",
            "options_html": {
                "A": """<b><font color="#1E3A8A">ENG:</font></b> 19%<br><small><font color="#4B5563">🎵 IPA: /ˌnaɪnˈtiːn pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: 19 phần trăm</font></i>""",
                "B": """<b><font color="#1E3A8A">ENG:</font></b> 67%<br><small><font color="#4B5563">🎵 IPA: /ˌsɪksti-ˈsɛvən pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: 67 phần trăm</font></i>""",
                "C": """<b><font color="#1E3A8A">ENG:</font></b> 70-80%<br><small><font color="#4B5563">🎵 IPA: /ˈsɛvənti tuː ˈeɪti pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: 70-80 phần trăm</font></i>""",
                "D": """<b><font color="#1E3A8A">ENG:</font></b> Over 90%<br><small><font color="#4B5563">🎵 IPA: /ˈoʊvə(r) ˈnaɪnti pəˈsɛnt/</font></small><br><i><font color="#059669">🇻🇳 VIE: Trên 90 phần trăm</font></i>"""
            }
        }
    ],
    "3️⃣ VSTEP Viết": [
        {
            "id": 1,
            "type": "Task 1: Viết thư hồi đáp công việc (Informal Email Interaction)",
            "prompt": "You received an email from Jane asking about your friend An, who is planning to take a short English summer course in London. Write a reply email to provide details about his accommodation arrangements and arrival schedule.",
            "template": "Dear Jane,\n\nI am writing to inform you that An has finalized his summer course plan...\n\nBest regards,\n[Your Name]"
        }
    ],
    "4️⃣ VSTEP Nói": [
        {
            "id": 1,
            "type": "Part 1: Tương tác xã hội phản xạ (Social Interaction)",
            "prompt": "Let's talk about your free time activities. What TV channels do you prefer to watch? Do you like reading books in your spare time? Why or why not?"
        }
    ]
}

# CẤU TRÚC CHỈ THỊ ÉP ĐỊNH DẠNG TUYỆT ĐỐI 3 DÒNG INTERLINEAR CHO HỆ THỐNG PHÂN TÍCH
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
2. Every question stem and all multiple-choice options (A, B, C, D) MUST follow the strict 3-line interlinear format (ENG, IPA, VIE) independently with hard <br> breaks.
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

# THÀNH PHẦN ĐIỀU HÀNH BÊN SƯỜN GIAO DIỆN
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
with col_s2:
    if st.sidebar.button("2️⃣ VSTEP Đọc", use_container_width=True):
        st.session_state.current_section = "2️⃣ VSTEP Đọc"
        st.session_state.current_q_idx = 0
col_s3, col_s4 = st.sidebar.columns(2)
with col_s3:
    if st.sidebar.button("3️⃣ VSTEP Viết", use_container_width=True):
        st.session_state.current_section = "3️⃣ VSTEP Viết"
        st.session_state.current_q_idx = 0
with col_s4:
    if st.sidebar.button("4️⃣ VSTEP Nói", use_container_width=True):
        st.session_state.current_section = "4️⃣ VSTEP Nói"
        st.session_state.current_q_idx = 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 ĐIỀU HƯỚNG CÂU HỎI (TIẾN LÙI TỰ DO)")

questions_list = VSTEP_EXAM_DB[st.session_state.current_section]
max_questions = len(questions_list)

col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    if st.button("⏮️ CÂU TRƯỚC", use_container_width=True):
        st.session_state.current_q_idx = max(st.session_state.current_q_idx - 1, 0)
with col_next:
    if st.button("⏭️ CÂU TIẾP", use_container_width=True):
        st.session_state.current_q_idx = min(st.session_state.current_q_idx + 1, max_questions - 1)

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

# LUỒNG HIỂN THỊ TỰ ĐỘNG KÍCH HOẠT VÀ HIỂN THỊ VĂN BẢN TRÍCH XUẤT 3 DÒNG
if st.session_state.current_section == "1️⃣ VSTEP Nghe":
    st.info("🎧 **Thầy cô thực hiện nghe dữ liệu âm thanh dưới đây và xác định câu trả lời chuẩn xác:**")
    tts_main = gTTS(text=active_q["raw_script"], lang='en', tld='com')
    fp_main = io.BytesIO()
    tts_main.write_to_fp(fp_main)
    fp_main.seek(0)
    st.audio(fp_main, format="audio/mp3")
    
    if is_submitted:
        st.success("=== VĂN BẢN BÓC BĂNG ÂM THANH (AUDIO SCRIPT) CHUẨN 3 DÒNG TỐI CAO ===")
        st.markdown(active_q["script_html"], unsafe_allow_html=True)
        st.markdown("=========================================================")

    st.markdown("**Question Context:**")
    st.markdown(active_q["question_html"], unsafe_allow_html=True)

elif st.session_state.current_section == "2️⃣ VSTEP Đọc":
    st.success("=== ĐOẠN VĂN NỀN ĐỌC HIỂU HOÀN CHỈNH (PASSAGE CONTEXT) CHUẨN 3 DÒNG ===")
    st.markdown(active_q["passage_html"], unsafe_allow_html=True)
    st.markdown("=========================================================")
    st.markdown("**Question Context:**")
    st.markdown(active_q["question_html"], unsafe_allow_html=True)

elif st.session_state.current_section in ["3️⃣ VSTEP Viết", "4️⃣ VSTEP Nói"]:
    st.warning(f"📢 **Yêu cầu phân hệ tự luận:** {active_q['prompt']}")
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
                    eval_prompt = f"Học viên nộp bài tự luận viết cho đề bài: '{active_q['prompt']}'. Nội dung: '{user_essay}'. Hãy sửa sai cấu trúc và xuất khối [DIEN_GIAI] chuẩn 3 dòng."
                    with st.spinner("Hệ thống đang thẩm định..."):
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(MODEL_NAME, system_instruction=MASTER_PROMPT, safety_settings=SAFETY_SETTINGS)
                        response = model.generate_content(eval_prompt)
                        st.session_state.saved_explanations[q_key] = response.candidates[0].content.parts[0].text
                        st.rerun()
        else:
            st.info("Bài làm tự luận đã được ghi nhận trên hệ thống.")
            st.markdown(f"> *{st.session_state.submitted_state[q_key]}*")

# THUẬT TOÁN TỰ ĐỘNG CHẤM VÀ ĐỔI MÀU ĐỒ HỌA NGAY KHI ẤN CHỌN PHƯƠNG ÁN (KHÔNG CẦN ẤN NÚT NỘP)
if st.session_state.current_section in ["1️⃣ VSTEP Nghe", "2️⃣ VSTEP Đọc"]:
    if not is_submitted:
        options_keys = list(active_q["options_html"].keys())
        st.markdown("**Mời thầy cô lựa chọn phương án:**")
        
        # Tạo chuỗi hiển thị 3 dòng trực quan cho các nút chọn lựa radio
        selected_option = st.radio(
            "Đánh dấu vào ô tròn phía trước đáp án:",
            ["-- Hãy chọn một đáp án / Select your option --"] + options_keys,
            format_func=lambda x: x if x == "-- Hãy chọn một đáp án / Select your option --" else f"Phương án {x}",
            key=f"radio_mcq_{active_q['id']}"
        )
        
        # Kích hoạt tiến trình chấm điểm tự động ngay khi người học tương tác chọn đáp án hợp lệ
        if selected_option != "-- Hãy chọn một đáp án / Select your option --":
            st.session_state.submitted_state[q_key] = selected_option
            is_correct = (selected_option == active_q["correct"])
            score_tag = "[SCORE_UP]" if is_correct else ""
            
            # Bóc tách text thô của phương án để gửi lệnh so sánh
            raw_target_option = active_q["options_html"][selected_option]
            
            eval_prompt = f"""
            Học viên đang làm đề {selected_de}, kỹ năng {st.session_state.current_section}, câu hỏi id {active_q['id']}.
            Đáp án đúng của hệ thống là: {active_q['correct']}. Học viên chọn phương án: {selected_option}.
            Hãy xuất ra kết quả phân tích chuẩn hóa. Nếu đúng chèn thẻ {score_tag}.
            Áp dụng quy tắc cưỡng bách 3 dòng interlinear cho toàn bộ văn bản giải thích.
            Đóng gói phần bóc tách sơ đồ tư duy, từ khóa vàng định vị thính giác và phần CÂU HỎI THAM KHẢO BIẾN THỂ (mỗi câu bọc trong cặp thẻ AUDIO_START và AUDIO_END để tạo audio phát âm) vào cặp thẻ [DIEN_GIAI_START] và [DIEN_GIAI_END]. Mọi dòng chữ tiếng Anh xuất hiện trong bài tập bổ sung phải có phiên âm và dịch nghĩa 3 dòng tuyệt đối.
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
        st.markdown("**Trạng thái đối chiếu phương án đồ hóa:**")
        for key, html_val in active_q["options_html"].items():
            if key == active_q["correct"]:
                st.markdown(f"<div style='border:2px solid #2E7D32; background-color:#E8F5E9; padding:10px; border-radius:5px; margin-bottom:10px;'><b>✔ PHƯƠNG ÁN ĐÚNG:</b><br>{html_val}</div>", unsafe_allow_html=True)
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

# LUỒNG HIỂN THỊ KẾT QUẢ VÀ HỘP CÔNG CỤ DIỄN GIẢI SAU KHI HOÀN THÀNH BÀI KHẢO SÁT
if is_submitted and q_key in st.session_state.saved_explanations:
    st.markdown("### 🔔 KẾT QUẢ KIỂM ĐỊNH TỪ HỆ THỐNG CHUYÊN GIA:")
    render_custom_vstep_message(st.session_state.saved_explanations[q_key])

# THỰC THI THU ÂM VÀ XỬ LÝ PHÂN HỆ NÓI TRỰC TIẾP TỪ THANH BÊN
audio_data = st.sidebar.audio_input(
    "Ghi âm trực tiếp bài nói phản xạ:",
    key=f"mic_widget_{st.session_state.mic_key}"
)

if audio_data is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI VSTEP", use_container_width=True):
        if not api_key:
            st.sidebar.error("Vui lòng điền mã trực lưu hệ thống.")
        else:
            vstep_speech_command = f"Đây là file ghi âm bài nói micro của tôi tại câu số {active_q['id']} phần {st.session_state.current_section}. Hãy bóc băng âm thanh và xuất khối diễn giải 3 dòng interlinear."
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
