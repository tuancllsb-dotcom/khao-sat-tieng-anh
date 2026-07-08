import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
import time

# ✨ Thiết lập không gian phòng khảo thí chuyên nghiệp chuẩn VSTEP sư phạm.
st.set_page_config(
    page_title="Siêu Ứng Dụng VSTEP Thực Chiến Cho Giáo Viên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧠 BỘ NÃO AI TỔNG HỢP: GIÁO VIÊN LÃO LUYỆN, NHÀ NGÔN NGỮ HỌC VÀ CHUYÊN GIA HUẤN LUYỆN NÃO BỘ
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the world-class "Interactive VSTEP Master Trainer". Your core engine is built upon 20+ years of pedagogical experience, neuro-linguistic programming (NLP) for rapid adult language acquisition, and strategic cognitive training. You address the user respectfully as "thầy cô" and aim for 100% test-taking mastery.

# SYSTEM ARCHITECTURE: MULTIPLE TEST CODES & BACKTRACKING
You must adapt your target question database instantly based on the selected Test Code (Mã đề) and active numeric section from the application state:
- Mã đề VSTEP-2026-A (Đề Minh Họa Gốc): Extracts from LISTENING.doc, READING.doc, and de-mau-02-khao-sat-nang-luc-tieng-anh-giao-vien-2026.pdf.
- Mã đề VSTEP-2026-B (Đề Phát Triển 01): Focuses on parallel academic variants of equal VSTEP difficulty.
- Mã đề VSTEP-2026-C (Đề Nâng Cao 02): Focuses on complex continuous academic passages and intensive professional speaking modules.

# SEQUENTIAL QUESTION DELIVERY FLOW
1. Deliver questions ONE BY ONE. You must display the core question and its 4 multiple-choice options (A, B, C, D) immediately.
2. CRITICAL PRE-SUBMISSION RULE: Hide the answer key, hide the correct option, and hide all explanations until the teacher types/submits their choice or record input.
3. CRITICAL POST-SUBMISSION DEEP ANALYSIS: Once an answer is submitted, immediately unlock a deep cognitive breakdown:
   - Identify if the answer is Correct/Incorrect.
   - [🎯 CHUYÊN GIA GIẢI THÍCH]: Analyze why the correct option is right and decompose the specific distractors (bẫy từ vựng/ngữ pháp).
   - [🧠 HUẤN LUYỆN NÃO BỘ MẸO]: Provide a quick, memorable neuro-linguistic tip to retain this pattern permanently.

# STYLISTIC VISUAL FIX FOR LINE COLLAPSING (IMAGE_CB313F.PNG ERROR)
You must enforce strict line breaks using clear separation rows. Never bundle multiple structural components onto the same line. Format every single target model sentence using this explicit 3-line interlinear blueprint:
[📦 ENG] <English text sentence here>
[🎵 IPA] <Standard IPA transcription with / for rhythmic chunk pauses>
[🇻🇳 VIE] <Bản dịch nghĩa tiếng Việt bám sát bản chất ngữ cảnh>

# SMART MICROPHONE SPEECH FILTRATION (HEAR CLEARLY PROTOCOL)
When validating speaking audio from the teacher:
1. Only transcribe words that are HEARD CLEARLY and with intelligible confidence. Omit any mumbling or extreme environmental background noise completely from the text transcription.
2. Generate a custom HTML block matching the exact coloring code:
   - Correctly spoken terms: Render in dark green/black (`.txt-correct`).
   - Skipped or mispronounced targeted text: Render in bright RED (`.txt-wrong`) with its exact standard correct IPA guide appended directly underneath (`.ipa-practice`).

# AUDIO COMPLIANCE REGENERATION TAGS
Always duplicate the core clean English target sentence between `[AUDIO_START]` and `[AUDIO_END]` tags at the very end of your response block to keep the gTTS button active.
"""

# 💾 HỆ THỐNG QUAN TRẮC TRẠNG THÁI PHÒNG THI (STATE MANAGEMENT)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# ⚙️ BẢN ĐIỀU HÀNH PHÒNG THI SƯ PHẠM CAO CẤP (SIDEBAR CHUYÊN GIA)
st.sidebar.title("🎓 TRUNG TÂM ĐIỀU HÀNH VSTEP")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password")

# 📂 TÍNH NĂNG 1: QUAN LY HỆ THỐNG ĐA MÃ ĐỀ LUYỆN TẬP TỰ DO
st.sidebar.markdown("### 📁 BỘ CHỌN MÃ ĐỀ KHẢO SÁT")
selected_de = st.sidebar.selectbox(
    "Chọn Mã đề thi (Có thể đổi khi thành thạo):",
    ["Mã đề VSTEP-2026-A (Đề Minh Họa)", "Mã đề VSTEP-2026-B (Đề Phát Triển)", "Mã đề VSTEP-2026-C (Đề Nâng Cao)"]
)

font_size = st.sidebar.slider("Kích thước chữ (Nút chữ T)", 14, 24, 16)
st.markdown(f"<style>.stMarkdown, p, li, .stChatMessage {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)

# 🔢 PHÍM TẮT DI CHUYỂN PHẦN THI THEO HỒ SƠ TÀI LIỆU VSTEP
st.sidebar.markdown("### 🔢 PHẦN THI CHUYÊN BIỆT")
col_s1, col_s2 = st.sidebar.columns(2)
nav_action = None
with col_s1:
    if st.sidebar.button("1️⃣ VSTEP Nghe", use_container_width=True): nav_action = "1"
    if st.sidebar.button("3️⃣ VSTEP Viết", use_container_width=True): nav_action = "3"
with col_s2:
    if st.sidebar.button("2️⃣ VSTEP Đọc", use_container_width=True): nav_action = "2"
    if st.sidebar.button("4️⃣ VSTEP Nói", use_container_width=True): nav_action = "4"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 ĐIỀU HƯỚNG TIẾN LÙI ĐA CHIỀU")

# ĐIỀU CHỈNH QUAY LẠI TỰ DO THEO YÊU CẦU THỰC CHIẾN CỦA GIÁO VIÊN
col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    if st.button("⏮️ CÂU TRƯỚC", use_container_width=True):
        st.session_state.current_q = max(st.session_state.current_q - 1, 1)
        nav_action = f"Hành động quay lại: Đang ở mã đề {selected_de}. Hãy đưa ra câu hỏi số {st.session_state.current_q} của phần thi hiện tại. Yêu cầu bắt buộc hiển thị đầy đủ câu hỏi, 4 phương án trắc nghiệm A,B,C,D rõ ràng và tuân thủ ngắt dòng tuyệt đối."

with col_next:
    if st.button("⏭️ CÂU TIẾP", use_container_width=True):
        st.session_state.current_q = min(st.session_state.current_q + 1, 12)
        st.session_state.score = min(st.session_state.score + 5, 100)
        nav_action = f"Hành động tiến tiếp theo: Đang ở mã đề {selected_de}. Hãy đưa ra câu hỏi số {st.session_state.current_q} của phần thi hiện tại. Yêu cầu bắt buộc hiển thị đầy đủ câu hỏi, 4 phương án trắc nghiệm A,B,C,D rõ ràng và tuân thủ ngắt dòng tuyệt đối."

if st.sidebar.button("🔄 KHỞI ĐỘNG LẠI PHÒNG THI", use_container_width=True):
    st.session_state.current_q = 1
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    nav_action = f"VỀ MENU CHÍNH CHÀO MỪNG CỦA MÃ ĐỀ {selected_de}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 PHẦN THI NÓI - THU ÂM")
audio_data = st.sidebar.audio_input("Bấm nút tròn để tiến hành thu âm bài nói trực tiếp:")

# 🏛️ KHÔNG GIAN KHẢO THÍ SỐ HÓA VSTEP
st.title("🎓 SIÊU ỨNG DỤNG KHẢO SÁT TIẾNG ANH VSTEP")
st.caption(f"Đang vận hành cấu trúc: {selected_de} | Chuẩn hóa Cú pháp & Tách dòng Interlinear Tuyệt đối")
st.markdown("---")

# 📊 THANH TRẠNG THÁI TIẾN ĐỘ KHẢO SÁT VÀ BẢNG ĐIỂM SỐ CHỮ CHI TIẾT
elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(50 * 60 - elapsed_time, 0) 
mins, secs = divmod(int(remaining_time), 60)

dash_col1, dash_col2, dash_col3 = st.columns(3)
with dash_col1:
    st.markdown("**📊 THANH TRẠNG THÁI TIẾN ĐỘ KHẢO SÁT**")
    st.progress(st.session_state.current_q / 12)
    st.caption(f"Tiến độ thực tế: Câu {st.session_state.current_q} trên tổng số 12 câu mục tiêu.")
with dash_col2:
    st.metric(label="💯 Thang Điểm Ước Tính Hiện Tại", value=f"{st.session_state.score} / 100 Điểm")
with dash_col3:
    st.metric(label="⏳ Đồng Hồ Đếm Ngược", value=f"{mins:02d}:{secs:02d} Phút")

st.markdown("---")

# 🌟 TỰ ĐỘNG KHỞI TẠO PHÒNG THI KHI KÍCH HOẠT MÃ ĐỀ VÀ API KEY
if "initialized" not in st.session_state and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=MASTER_PROMPT)
        init_res = model.generate_content(f"START_APPLICATION_FOR_CODE_{selected_de}")
        st.session_state.messages.append({"role": "assistant", "content": init_res.text})
        st.session_state.initialized = True
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối bộ não AI: {e}")

# 🎵 TÁI SINH NÚT PHÁT ÂM THANH CHỦ ĐỘNG KHÔNG LỖI (TẮT AUTOPLAY)
def play_audio_safely(text_content):
    if "[AUDIO_START]" in text_content and "[AUDIO_END]" in text_content:
        try:
            start_idx = text_content.find("[AUDIO_START]") + len("[AUDIO_START]")
            end_idx = text_content.find("[AUDIO_END]")
            audio_text = text_content[start_idx:end_idx].strip()
            if audio_text:
                tts = gTTS(text=audio_text, lang='en', tld='com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                b64_audio = base64.b64encode(fp.read()).decode()
                audio_html = f'<audio controls src="data:audio/mp3;base64,{b64_audio}" style="width: 100%; margin-top: 12px; margin-bottom: 12px;"></audio>'
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Lỗi khởi tạo động cơ âm thanh gTTS: {e}")

# 📜 HIỂN THỊ DÒNG LỊCH SỬ KHẢO THÍ CHUẨN ĐỒ HỌA SƯ PHẠM
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        if message["role"] == "assistant":
            play_audio_safely(message["content"])

# 🚀 CỔNG TRUYỀN DỮ LIỆU ĐƯỜNG TRUYỀN HỎA TỐC BIÊN NGOÀI
def send_exam_data(prompt_text, audio_file=None, is_nav=False):
    if not api_key:
        st.sidebar.warning("Thầy/cô vui lòng điền mã API Key ở góc trái để bắt đầu kích hoạt bài thi!")
        return
        
    response_text = ""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=MASTER_PROMPT)
        
        if is_nav:
            st.session_state.messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"][-1:]
        
        formatted_contents = []
        for msg in st.session_state.messages[-4:]:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append({"role": role, "parts": [msg["content"]]})
        
        if audio_file is not None:
            st.session_state.messages.append({"role": "user", "content": f"🎤 [Thầy cô đã nộp tệp âm thanh Micro của mã đề {selected_de}]"})
            formatted_contents.append({
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": audio_file.type,
                            "data": audio_file.getvalue()
                        }
                    },
                    prompt_text
                ]
            })
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            formatted_contents.append({"role": "user", "parts": [prompt_text]})
        
        with st.chat_message("assistant"):
            with st.spinner("Hệ thống chuyên gia đang thẩm định bài làm và giải giải phẫu cú pháp..."):
                response = model.generate_content(contents=formatted_contents)
                response_text = response.text
                st.markdown(response_text, unsafe_allow_html=True)
                play_audio_safely(response_text)
                
    except Exception as e:
        st.error(f"❌ Đường truyền báo lỗi: {e}. Vui lòng kiểm tra lại thiết bị hoặc nhấn F5.")
        return

    # KÍCH HOẠT BIÊN NGOÀI KHỐI - Bẻ gãy bẫy lỗi đơ vòng lặp Streamlit
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

# Kích hoạt luồng chuyển dịch hành chính từ Sidebar
if nav_action:
    send_exam_data(nav_action, is_nav=True)

# 🚀 NỘP BÀI THI NÓI VSTEP - Thuật toán bộ lọc thính giác & Nhuộm đỏ lỗi phát âm từng từ
if audio_data is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI VSTEP", use_container_width=True):
        vstep_speech_command = f"""
        Đây là dữ liệu giọng nói của tôi từ microphone cho câu hỏi số {st.session_state.current_q} thuộc mã đề {selected_de}. Hãy xử lý nghiêm ngặt theo các bước sau:
        
        1. [DỰ ĐOÁN VÀ BÓC BĂNG PHÁN ĐOÁN AI]: Thực hiện vai trò bộ lọc thính giác NLP thông minh. CHỈ GHI RA những từ ngữ được phát âm rõ âm, rõ chữ và mạch lạc. Nếu từ nào thều thào, nói lắp, hoặc bị nhiễu hoàn toàn bởi tạp âm môi trường, tuyệt đối KHÔNG ĐƯỢC GHI RA text.
        
        2. [MÃ HTML ĐỒ HỌA SO SÁNH PHÁT ÂM]: So sánh đoạn từ nghe rõ được với câu chuẩn của đề thi VSTEP. Trả về một khối mã HTML duy nhất (không bọc trong ký tự dấu nháy ```html) áp dụng CSS sau:
           <style>
              .word-group { display: inline-block; text-align: center; margin-right: 14px; margin-bottom: 18px; vertical-align: top; }
              .txt-correct { font-size: 19px; color: #2e7d32; font-weight: bold; }
              .txt-wrong { font-size: 19px; color: #d32f2f; font-weight: bold; }
              .ipa-practice { font-size: 13px; color: #c62828; font-family: monospace; display: block; margin-top: 5px; }
           </style>
           - Từ phát âm CHUẨN: bọc trong <div class='word-group'><span class='txt-correct'>Từ_Gốc</span></div>
           - Từ phát âm SAI hoặc BỊ BỎ QUA từ câu mẫu chuẩn: Nhuộm màu ĐỎ rực rỡ bằng cách bọc trong <div class='word-group'><span class='txt-wrong'>Từ_Gốc</span><span class='ipa-practice'>/Phiên_Âm_Chuẩn/</span></div>
        
        3. [PHẦN GIẢI THÍCH SÂU & BIỂU DIỄN GIÀNH CHO GIÁO VIÊN]: Ngay bên dưới khối HTML, hãy xuất ra phần chấm điểm, phần giải thích ngữ pháp học thuật chi tiết, mẹo ghi nhớ cho não bộ ứng dụng và bố cục 3 dòng interlinear biệt lập:
           [📦 ENG] <Câu Anh mẫu tiếng>
           [🎵 IPA] <Phiên chuẩn cụm quốc tế âm>
           [🇻🇳 VIE] <Bản Việt bám cảnh dịch nghĩa ngữ sát đề>
           
        4. [TÁI SINH NÚT PHÁT ÂM THANH]: Đảm bảo sao chép lại câu tiếng Anh chuẩn bọc trong cặp thẻ [AUDIO_START] Câu tiếng Anh chuẩn [AUDIO_END] đặt ở cuối để giữ bộ phát âm thanh hoạt động.
        """
        send_exam_data(vstep_speech_command, audio_file=audio_data)

# 📝 KHUNG TIẾP NHẬN ĐÁP ÁN TRẮC NGHIỆM VÀ BÀI LUẬN TỰ LUẬN VSTEP
if text_input := st.chat_input("Nhập đáp án (A,B,C,D), số câu/phần hoặc đoạn văn viết tự luận tại đây..."):  
    if text_input.strip() in ["1", "2", "3", "4"]:
        send_exam_data(text_input.strip(), is_nav=True)
    else:
        send_exam_data(f"Tôi nộp câu trả lời/đáp án bài làm tại mã đề {selected_de} là: {text_input}. Bạn hãy thực hiện chấm điểm ngay, bung phần giải thích mô tả chi tiết sâu sắc sau đáp án (bao gồm lý do đúng/sai, bẫy từ vựng cần tránh, mẹo huấn luyện não bộ ghi nhớ lâu) và biểu diễn cấu trúc câu chuẩn theo phong cách thiết kế 3 dòng interlinear ngắt dòng tuyệt đối biệt lập từng dòng. Đồng thời nhúng mã [AUDIO_START] câu tiếng Anh chuẩn [AUDIO_END] ở cuối.")
