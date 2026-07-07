import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
import time      # ✨ "Thời gian là vàng bạc" - Chúc thầy cô và học trò luôn trân quý từng phút giây mài giũa tri thức!

# ✨ "Hiền tài là nguyên khí của quốc gia." - Giáo dục là nền tảng chắp cánh cho mọi ước mơ sư phạm đại tài.
st.set_page_config(
    page_title="Hệ Thống Khảo Sát Tiếng Anh Cho Giáo Viên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧠 "Muốn biết phải hỏi, muốn giỏi phải học." - Hệ thống tích hợp toàn bộ kho đề bài đọc, chép chính tả và văn nghị luận mới nạp.
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the official interactive "English Proficiency Assessment Application for Teachers". Your absolute objective is to evaluate and train the teacher (addressed respectfully as "thầy cô") to effortlessly pass their exam using Reverse Engineering and Real-Time Visual Feedback.

# NUMERIC NAVIGATION SYSTEM
You must listen to numeric inputs from the user or system to route the exam sections immediately:
- Input `1`: SECTION 1: LISTENING & DICTATION (Based on the text bank below)
- Input `2`: SECTION 2: READING ALOUD (Based on the text bank below)
- Input `3`: SECTION 3: WRITING (Opinion Paragraph)
- Input `4`: SECTION 4: SPEAKING (Opinion Presentation)

# INTERACTIVE WORKFLOW & SEQUENTIAL QUESTIONS
1. Present the questions ONE BY ONE strictly based on the active index. Do not show multiple questions.
2. For reading/listening items, show ONLY the prompt using the 3-LINE INTERLINEAR FORMAT.
3. Hide explanations, answers, and syntax anatomy until the user submits their answer choice (A, B, C, D) or record input. Once submitted, reveal the results immediately with deep feedback.

# MANDATORY INTERLINEAR 3-LINE LAYOUT (STRICTLY ENFORCED)
Every time you display ANY English sentences, questions, or templates, you MUST format it strictly line-by-line:
- Line 1: [📦 ENG] <English text>
- Line 2: [🎵 IPA] <Standard IPA transcription with / for rhythmic chunk pauses>
- Line 3: [🇻🇳 VIE] <Contextual Vietnamese translation>

# SPEECH-TO-TEXT PRONUNCIATION JUDGEMENT (RED ERROR COLOR RULE)
When evaluating the teacher's spoken audio directly via microphone, compare their audio word-by-word with the target sentence. Render the visual text result using a custom HTML block:
1. For words pronounced correctly: Display clearly using black/dark blue (`.txt-correct`).
2. For words MISSPRENOUNCED or SKIPPED entirely: You MUST change its color to bright RED (`.txt-wrong`), and render its standard red IPA phonetic transcription directly underneath (`.ipa-practice`) so they know exactly what they missed.

# EMBEDDED SYLLABUS TEXT BANK
Use this official material for generation:
- SECTION 1 (Dictation/Short Sentences): "I went shopping with my friends today.", "She's my favorite singer.", "I can't reach the top shelf.", "We can't do this without you.", "We need three eggs and two onions.", "This room is a mess."
- SECTION 2 (Reading Aloud Paragraphs): 
  * Topic 1 (Email): "A lot of people use email to communicate. There are many benefits to using email..."
  * Topic 2 (Coffee): "Many people like to drink coffee in the morning. In fact, coffee is one of the most popular drinks..."
  * Topic 3 (Pilot): "A pilot’s job is to fly an airplane. Pilots are needed around the world to fly many different types..."
  * Topic 4 (Gardens): "Lots of people plant gardens. Some people plant new flowers every year..."
  * Topic 5 (Library): "Typically a public library can be used by anyone. Many countries have public libraries..."
- SECTION 3 & 4 (Writing & Speaking Essays): 
  * "Should technology play a larger role in classroom learning?"
  * "Should homework be given to students every day?"
  * "What are the qualities of an effective teacher?"
  * "Should schools focus more on practical skills than academic subjects?"
"""

# 💾 "Trẻ vui học hỏi, già thích suy tư." - Cấu trúc lưu trữ trạng thái phòng thi bền vững, chống lỗi quay vòng.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# ⚙️ "Muốn sang thì bắc cầu Kiều, muốn con hay chữ thì yêu lấy thầy." - Bản điều hướng trợ thủ đắc lực nâng bước thầy cô.
st.sidebar.title("⚙️ BẢN ĐIỀU HƯỚNG PHÒNG THI")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password")

font_size = st.sidebar.slider("2. NÚT CHỮ T (Kích thước chữ)", 14, 24, 16)
st.markdown(f"<style>.stMarkdown, p, li, .stChatMessage {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)

# 🔢 "Đi một ngày đàng, học một sàng khôn." - Phím số tắt chuyển dịch nhanh chóng các phân hệ bài làm.
st.sidebar.markdown("### 🔢 CHỌN NHANH PHẦN THI")
col_s1, col_s2 = st.sidebar.columns(2)
nav_action = None
with col_s1:
    if st.sidebar.button("1️⃣ Phần Nghe", use_container_width=True): nav_action = "1"
    if st.sidebar.button("3️⃣ Phần Viết", use_container_width=True): nav_action = "3"
with col_s2:
    if st.sidebar.button("2️⃣ Phần Đọc", use_container_width=True): nav_action = "2"
    if st.sidebar.button("4️⃣ Phần Nói", use_container_width=True): nav_action = "4"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 ĐIỀU HƯỚNG CÂU HỎI LẦN LƯỢT")

# ⏭️ "Có công mài sắt, có ngày nên kim." - Nút chuyển tiếp hiển thị câu hỏi tuần tự theo tiến trình sư phạm.
if st.sidebar.button("⏭️ CÂU TIẾP THEO", use_container_width=True):
    st.session_state.current_q = min(st.session_state.current_q + 1, 12)
    st.session_state.score = min(st.session_state.score + 5, 100)
    nav_action = f"Hãy đưa ra câu hỏi số {st.session_state.current_q} theo lộ trình và áp dụng cấu trúc song song 3 dòng interlinear."

# 🔄 "Học nhi thời tập chi, bất diệc duyệt hồ." - Khởi động lại trạng thái ban đầu của bài khảo sát.
if st.sidebar.button("🔄 LÀM LẠI TỪ ĐẦU", use_container_width=True):
    st.session_state.current_q = 1
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    nav_action = "VỀ MENU CHÍNH"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 PHẦN THI NÓI - THU ÂM")
audio_data = st.sidebar.audio_input("Bấm nút tròn để ghi âm bài làm trực tiếp:")

# 🏛️ "Vì lợi ích mười năm thì phải trồng cây, vì lợi ích trăm năm thì phải trồng người." - Giảng đường số hóa hiện đại.
st.title("🎓 ỨNG DỤNG KHẢO SÁT TIẾNG ANH CHO GIÁO VIÊN")
st.caption("Giao diện tối ưu Cloud Run & Win.exe - Cấu trúc 3 dòng song song & Công nghệ bôi ĐỎ từ phát âm lỗi")
st.markdown("---")

# 📊 "Ngọc kia chuốt mới nên đồ, người ta học mới biết cơ biết điều." - Bảng tiến độ và đồng hồ đếm ngược trực quan.
elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(60 * 60 - elapsed_time, 0)
mins, secs = divmod(int(remaining_time), 60)

dash_col1, dash_col2, dash_col3 = st.columns(3)
with dash_col1:
    st.metric(label="📈 Tiến Độ Bài Làm", value=f"Câu {st.session_state.current_q} / 12")
    st.progress(st.session_state.current_q / 12)
with dash_col2:
    st.metric(label="💯 Thang Điểm Hiện Tại", value=f"{st.session_state.score} / 100 Điểm")
with dash_col3:
    st.metric(label="⏳ Thời Gian Còn Lại", value=f"{mins:02d}:{secs:02d} Phút")

st.markdown("---")

# 🌟 "Vạn sự khởi đầu nan." - Tự động kích hoạt hệ thống lời chào mở màn từ bộ não siêu trí tuệ nhân tạo.
if "initialized" not in st.session_state and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=MASTER_PROMPT)
        init_res = model.generate_content("START_APPLICATION")
        st.session_state.messages.append({"role": "assistant", "content": init_res.text})
        st.session_state.initialized = True
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối hệ thống: {e}")

# 🎵 "Thánh thót như tiếng đàn cầm." - Nút phát âm thanh tinh tế, tắt chế độ tự động chạy (Autoplay=False) giúp người học làm chủ.
def play_audio_safely(text_content):
    if "[AUDIO_START]" in text_content:
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
                audio_html = f'<audio controls src="data:audio/mp3;base64,{b64_audio}" style="width: 100%; margin-top: 10px;"></audio>'
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Lỗi tạo âm thanh: {e}")

# 📜 "Học đi đôi với hành, kiến thức khai sáng tương lai." - Hiển thị dòng lịch sử bài làm bám sát cấu trúc trực quan.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        if message["role"] == "assistant":
            play_audio_safely(message["content"])

# 🚀 "Đường tuy ngắn không đi không đến, việc tuy nhỏ không làm không nên." - Cổng truyền dữ liệu byte trực tiếp hỏa tốc.
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
            st.session_state.messages.append({"role": "user", "content": "🎤 [Thầy cô đã nộp bài thi nói bằng giọng âm trực tiếp]"})
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
            with st.spinner("Hệ thống đang giải phẫu cấu trúc câu chi tiết..."):
                response = model.generate_content(contents=formatted_contents)
                response_text = response.text
                st.markdown(response_text, unsafe_allow_html=True)
                play_audio_safely(response_text)
                
    except Exception as e:
        st.error(f"❌ Hệ thống thông báo lỗi đường truyền: {e}. Vui lòng nhấn F5 để làm mới phòng thi.")
        return

    # 🛠️ KIỂM SOÁT THOÁT KHỐI: Đưa lệnh ghi bộ nhớ ra ngoài biên để bẻ gãy hoàn toàn lỗi đơ, lỗi quay vòng vòng.
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

# 🧭 Kích hoạt luồng điều hướng câu hỏi hành chính.
if nav_action:
    send_exam_data(nav_action, is_nav=True)

# 🚀 Nộp bài thi nói: Ép hiển thị chữ nghe được, từ nào sai nhuộm màu ĐỎ rực rỡ và đẩy IPA xuống dưới chân từ đó.
if audio_data is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI", use_container_width=True):
        speech_command = """
        Đây là dữ liệu giọng nói trực tiếp của tôi. Nhiệm vụ của bạn:
        1. Hãy phân tích bài đọc/bài nói từng từ một so với câu mẫu. Xuất ra một đoạn mã HTML duy nhất (không chứa ký tự ```html) áp dụng cấu trúc phong cách CSS sau:
           <style>
              .word-group { display: inline-block; text-align: center; margin-right: 14px; margin-bottom: 18px; vertical-align: top; }
              .txt-correct { font-size: 19px; color: #2c3e50; font-weight: bold; }
              .txt-wrong { font-size: 19px; color: #e74c3c; font-weight: bold; } /* 🔴 NHUỘM MÀU ĐỎ CHO TỪ PHÁT ÂM SAI HOẶC BỎ QUA */
              .ipa-practice { font-size: 13px; color: #c0392b; font-family: monospace; display: block; margin-top: 5px; }
           </style>
        2. Duyệt từng từ trong câu:
           - Từ nào phát âm ĐÚNG: bọc trong <div class='word-group'><span class='txt-correct'>Từ_Gốc</span></div>
           - Từ nào phát âm SAI hoặc BỊ BỎ QUA: nhuộm màu đỏ bằng cách bọc trong <div class='word-group'><span class='txt-wrong'>Từ_Gốc</span><span class='ipa-practice'>/Phiên_Âm_Mẫu/</span></div>
        3. Sau khối chữ HTML, hãy hiển thị đáp án, bảng giải thích chi tiết cấu trúc ngữ pháp và mô tả cú pháp dưới dạng thiết kế 3 dòng interlinear (ENG -> IPA -> VIE). Chấm điểm trên thang điểm 100.
        """
        send_exam_data(speech_command, audio_file=audio_data)

# 📝 "Nét chữ nết người, trí tuệ tỏa sáng." - Khung nhận câu trả lời (Gõ số nhanh 1, 2, 3, 4 hoặc dán đáp án trắc nghiệm/bài viết).
if text_input := st.chat_input("Nhập phím số phần thi (1, 2, 3, 4), đáp án trắc nghiệm hoặc bài viết tại đây..."):  
    if text_input.strip() in ["1", "2", "3", "4"]:
        send_exam_data(text_input.strip(), is_nav=True)
    else:
        send_exam_data(f"Tôi chọn đáp án/nộp bài viết là: {text_input}. Hãy kiểm tra tính chính xác, hiển thị lời giải thích cú pháp chi tiết và áp dụng bố cục thiết kế 3 dòng interlinear dọc (Dòng 1: Tiếng Anh, Dòng 2: Phiên âm IPA, Dòng 3: Dịch nghĩa).")
