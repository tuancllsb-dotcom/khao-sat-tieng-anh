import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
import time

# ✨ Thiết lập cấu hình phòng khảo thí VSTEP thực chiến, tối ưu hóa giao diện.
st.set_page_config(
    page_title="Hệ Thống Luyện Thi VSTEP Giáo Viên - Phiên Bản Tối Cao",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧠 BỘ NÃO AI TỔNG HỢP: CHUYÊN GIA KHẢO THÍ VSTEP, NHÀ NGÔN NGỮ HỌC VÀ HUẤN LUYỆN NÃO BỘ
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the world-class "Interactive VSTEP Master Trainer" with 20+ years of pedagogical experience in high-stakes teacher proficiency assessment. You look at test items through the lens of a linguist and cognitive scientist. You address the user respectfully as "thầy cô".

# CRITICAL VISUAL FORMATTING RULE (ANTI-COLLAPSE MECHANICAL FIX)
To prevent sentences from running into each other, you MUST render ALL English text material, sentences, questions, and examples using a hard HTML layout with explicit `<br>` break tags. Follow this strict 3-line format EXACTLY:
<b>[📦 ENG]</b> <English text sample here><br>
<i>[🎵 IPA]</i> <Standard IPA transcription with / for rhythmic pause chunks><br>
<b>[🇻🇳 VIE]</b> <Contextual Vietnamese translation bám sát bản chất sư phạm>

# MULTIPLE-CHOICE OPTIONS FORMAT
For Section 1 and Section 2, immediately list the choices clearly below the 3-line block, each on its own line:
A. <Option A text>
B. <Option B text>
C. <Option C text>
D. <Option D text>

# SEQUENTIAL TASK DELIVERY & SYSTEM ARCHITECTURE
- Deliver questions ONE BY ONE strictly based on active state parameters.
- Hide answer keys and cognitive explanations until the teacher types/submits their answer or records audio.
- POST-SUBMISSION COGNITIVE BREAKDOWN: Once an answer is received, instantly unlock the complete analysis layout:
  1. Provide the structural correctness status (Correct/Incorrect).
  2. <b>[🎯 PHÂN TÍCH XÁC SUẤT RA ĐỀ & TRỌNG TÂM]</b>: Explain the likelihood of this structural pattern appearing in the real VSTEP exam. Dissect the precise grammar traps, vocabulary distractors, or auditory illusions.
  3. <b>[🧠 MẸO HUẤN LUYỆN NÃO BỘ]</b>: Give a memory anchoring technique (mnemonic or neuro-linguistic hack) to internalize the rule instantly under time pressure.

# SMART AUDIO FILTRATION & MICROPHONE JUDGEMENT
- When analyzing user speech, function as an advanced audio-linguistic filter. Transcribe ONLY words that are HEARD CLEARLY and with intelligible confidence. Omit mumbling, stumbling, or heavy background noise entirely from the text transcription.
- Compare clearly heard words against the target sentences. Render using HTML style blocks:
  * Correct words: dark green/black (`.txt-correct`).
  * Wrong or skipped words: bright RED (`.txt-wrong`) with correct standard IPA inserted directly underneath (`.ipa-practice`).

# VERBATIM EMBEDDED SYLLABUS DOCUMENT DATA BANK
Extract, simulate, and adapt core question frameworks directly from:
- LISTENING.doc & de-mau-02-khao-sat-nang-luc-tieng-anh-giao-vien-2026.pdf: "How many languages are taught at Hanoi International Language School?" (A. 1 | B. 2 | C. 3 | D. 4), "What is the boarding time of Flight VN178?" (A. 3.30 | B. 3.45 | C. 4.15 | D. 4.45).
- READING.doc: Passage 1 (Pandemics / Marburg virus statistics), Passage 2 (Kimonos text / China origin / T-shape / Obi belt).
- WRITING.doc & ĐỀ MẪU KHẢO SÁT NĂNG LỰC GIÁO VIÊN TIẾNG ANH.docx: Task 1 (Letter to Jane regarding friend An's summer course in London), Task 2 (Tourism impacts on local communities or City vs Countryside living analysis).
- SPEAKING.doc & cau-truc-bai-thi-khao-sat-tieng-anh-giao-vien.pdf: Part 1 (Free time / TV channels / Reading habits), Part 2 (Solution discussion: Trip from Danang to Hanoi via Train/Plane/Coach), Part 3 (Topic development: Reading habits among teenagers).

# AUDIO REGENERATION TAGS
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

# 📂 QUẢN LÝ HỆ THỐNG ĐA MÃ ĐỀ LUYỆN TẬP THEO TÀI LIỆU GỐC
st.sidebar.markdown("### 📁 BỘ CHỌN MÃ ĐỀ LUYỆN THI")
selected_de = st.sidebar.selectbox(
    "Chọn Mã đề thi thực chiến:",
    ["Mã đề VSTEP-2026-A (Đề Minh Họa Chuẩn)", "Mã đề VSTEP-2026-B (Đề Phát Triển Biến Thể)", "Mã đề VSTEP-2026-C (Đề Nâng Cao Chuyên Sâu)"]
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
st.sidebar.markdown("### 🧭 ĐIỀU HƯỚNG TIẾN LÙI ĐA CHIỀU (QUAY LẠI TỰ DO)")

# ĐIỀU CHỈNH QUAY LẠI TỰ DO THEO YÊU CẦU THỰC CHIẾN CỦA GIÁO VIÊN (KHÁC VỚI ĐỀ THI KHÓA CỨNG BAN ĐẦU)
col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    if st.button("⏮️ CÂU TRƯỚC", use_container_width=True):
        st.session_state.current_q = max(st.session_state.current_q - 1, 1)
        nav_action = f"Hành động quay lại câu trước: Đang ở mã đề {selected_de}. Hãy đưa ra câu hỏi số {st.session_state.current_q} của phần thi hiện tại. Yêu cầu bắt buộc hiển thị đầy đủ câu hỏi, 4 phương án trắc nghiệm A,B,C,D rõ ràng và tuân thủ ngắt dòng HTML cứng (<br>)."

with col_next:
    if st.button("⏭️ CÂU TIẾP", use_container_width=True):
        st.session_state.current_q = min(st.session_state.current_q + 1, 12)
        st.session_state.score = min(st.session_state.score + 5, 100)
        nav_action = f"Hành động tiến câu tiếp theo: Đang ở mã đề {selected_de}. Hãy đưa ra câu hỏi số {st.session_state.current_q} của phần thi hiện tại. Yêu cầu bắt buộc hiển thị đầy đủ câu hỏi, 4 phương án trắc nghiệm A,B,C,D rõ ràng và tuân thủ ngắt dòng HTML cứng (<br>)."

if st.sidebar.button("🔄 KHỞI ĐỘNG LẠI PHÒNG THI", use_container_width=True):
    st.session_state.current_q = 1
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    nav_action = f"VỀ MENU CHÍNH CHÀO MỪNG CỦA MÃ ĐỀ {selected_de}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 PHẦN THI NÓI - THU ÂM")
audio_data = st.sidebar.audio_input("Bấm nút tròn bên dưới để thu âm bài nói trực tiếp:")

# 🏛️ KHÔNG GIAN KHẢO THÍ SỐ HÓA VSTEP
st.title("🎓 SIÊU ỨNG DỤNG KHẢO SÁT TIẾNG ANH VSTEP")
st.caption(f"Đang vận hành cấu trúc: {selected_de} | Chuẩn hóa Cú pháp & Tách dòng Interlinear Tuyệt đối bám sát tài liệu gốc")
st.markdown("---")

# 📊 THANH TRẠNG THÁI TIẾN ĐỘ KHẢO SÁT VÀ BẢNG ĐIỂM SỐ CHI TIẾT
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
        
        3. [PHẦN GIẢI THÍCH SÂU & BIỂU DIỄN DÒNG BIỆT LẬP TUYỆT ĐỐI HHTML]: Ngay bên dưới khối HTML, hãy xuất ra phần chấm điểm, phần giải thích phân tích xác suất ra đề & trọng tâm bám sát, mẹo huấn luyện não bộ ghi nhớ và bắt buộc áp dụng thẻ ngắt dòng <br> cho cấu trúc interlinear:
           <b>[📦 ENG]</b> <Câu Anh mẫu tiếng><br>
           <i>[🎵 IPA]</i> <Phiên chuẩn cụm quốc tế âm><br>
           <b>[🇻🇳 VIE]</b> <Bản Việt bám cảnh dịch nghĩa ngữ sát đề>
           
        4. [TÁI SINH NÚT PHÁT ÂM THANH]: Đảm bảo sao chép lại câu tiếng Anh chuẩn bọc trong cặp thẻ [AUDIO_START] Câu tiếng Anh chuẩn [AUDIO_END] đặt ở cuối để giữ bộ phát âm thanh hoạt động.
        """
        send_exam_data(vstep_speech_command, audio_file=audio_data)

# 📝 KHUNG TIẾP NHẬN ĐÁP ÁN TRẮC NGHIỆM VÀ BÀI LUẬN TỰ LUẬN VSTEP
if text_input := st.chat_input("Nhập đáp án (A,B,C,D), số câu/phần hoặc đoạn văn viết tự luận tại đây..."):  
    if text_input.strip() in ["1", "2", "3", "4"]:
        send_exam_data(text_input.strip(), is_nav=True)
    else:
        send_exam_data(f"Tôi nộp câu trả lời/đáp án bài làm tại mã đề {selected_de} là: {text_input}. Bạn hãy thực hiện chấm điểm ngay, bung phần giải thích mô tả chi tiết sâu sắc sau đáp án (bao gồm lý do đúng/sai, bẫy từ vựng cần tránh, mẹo huấn luyện não bộ ghi nhớ lâu) và biểu diễn cấu trúc câu chuẩn theo phong cách thiết kế 3 dòng interlinear ngắt dòng bằng thẻ <br> tuyệt đối biệt lập từng dòng. Đồng thời nhúng mã [AUDIO_START] câu tiếng Anh chuẩn [AUDIO_END] ở cuối.")
