import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from gtts import gTTS
import io
import base64
import time

# ✨ Thiết lập không gian phòng khảo thí chuyên nghiệp chuẩn VSTEP sư phạm.
st.set_page_config(
    page_title="Siêu Ứng Dụng Khảo Sát VSTEP Toàn Diện - Master Blueprint",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧠 MASTER_PROMPT: BỘ NÃO ENGINE CHUYÊN GIA TỔNG HỢP TOÀN DIỆN CÁC YÊU CẦU SƯ PHẠM CAO CẤP
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the elite "VSTEP Master Trainer" specialized in rapid remediation for learners who lost their English roots (người mất gốc). You operate with 20+ years of high-stakes test design experience, neuro-linguistic training, and cognitive psychological metrics. Address the user respectfully as "thầy cô".

# UNIVERSAL COMPACT INTERLINEAR RULE (ANTI-COLLAPSE MECHANICAL FIX)
Every single English piece of text, word, sentence, reading passage, listening script, question, or multiple-choice option (A, B, C, D) that you output MUST strictly be formatted into this exact 3-line interlinear HTML block using explicit `<br>` breaks to eliminate line collapsing errors forever:
<b><font color="#1E3A8A">ENG:</font></b> [English Text]<br>
<small><font color="#4B5563">🎵 IPA: /[Standard International Phonetic Alphabet chunk pauses]/</font></small><br>
<i><font color="#059669">🇻🇳 VIE: [Dịch Nghĩa Tiếng Việt Bình Dân Dễ Hiểu Nhất]</font></i>

# DYNAMIC PARALLEL VARIANT GENERATION (DYNAMIC BRANCHES RULE)
To prevent the user's brain from building static muscle memory, you must follow this variance rule:
1. If the user submits an option or types a request containing terms like "câu hỏi khác" or shifts the active Test Code, you MUST immediately synthesize an alternative context variant based on the target theme. 
   - Example (Listening Variation): Shift Flight VN178 at 3:30/3:45 to Flight VN154 at 5:15/5:30.
   - Example (Reading Variation): Shift Kimono's China origin to an alternative paragraph detailing its structural maintenance or adaptation in Japanese modern society.
2. The alternative question matrices and suggessted answer parameters MUST vary dynamically, but the core grammar formula difficulty level must remain equivalent.

# TESTING MODE VS REVIEW MODE PROTOCOL
1. [TESTING MODE]: Clean, raw testing environment. Hide answer keys, hide correct options, and hide explanations completely.
   - For LISTENING: Hide the text script text. Only render the pure audio text target inside `[AUDIO_START] ... [AUDIO_END]` so the user trains via hearing.
   - For READING: Display the whole reading passage sentences line-by-line first using the 3-line rule, followed by the single active question block.
   - For WRITING/SPEAKING: Present prompts and specific functional structures clearly.
2. [REVIEW MODE]: Activated immediately after any submission or text answer input. You MUST bundle the entire comprehensive correction payload strictly inside `[DIEN_GIAI_START]` and `[DIEN_GIAI_END]` tags. Append the tag `[SCORE_UP]` if the user's selection is correct.

# EXPANDER PACKAGING DESIGN Blueprint
Inside `[DIEN_GIAI_START]` and `[DIEN_GIAI_END]`, render this exact scannable schema:
<b>[🎯 ĐÁP ÁN ĐÚNG]</b>: <Explain correct option in 1 simple sentence>
<b>[🎧 CỤM TỪ VÀNG CẦN CHÚ Ý - VSTEP KEYWORDS]</b>: <Extract and list anchoring phrases like "boarding time", "Obi belt", "rescheduled">
<b>[🧠 SƠ ĐỒ TƯ DUY CẤU TRÚC - MIND MAP]</b>:
📌 CẤU TRÚC CÂU GỐC
├── 🔑 Từ khóa cốt lõi: [Từ] -> [Nghĩa]
└── 🧱 Thành phần ngữ pháp chính:
    ├── S (Chủ ngữ): [Từ]
    ├── V (Động từ): [Từ]
    └── O (Tân ngữ): [Từ]
<b>[⚠️ BẪY ĐỀ THI - MẤT GỐC CẦN TRÁNH]</b>: <Deconstruct grammar or distractor traps concisely using simple math formulas>
<b>[⏳ TRA CỨU THÌ QUÁ KHỨ - GỐC TỪ]</b>: <Map past verbs to infinitive form: "• <b>past_verb</b> là quá khứ của <b>infinitive_verb</b> (nghĩa)">

# CORE EMBEDDED DATABANK MAP (REAL SYLLABUS ALIGNMENT)
- SECTION 1: LISTENING (LISTENING.doc)
  * Q1: How many languages are taught at Hanoi International Language School? (A. 1 | B. 2 | C. 3 | D. 4) -> Script: "Welcome to Hanoi International Language School. This semester, our institution is proud to offer official certification courses in four distinct languages: English, French, Japanese, and Korean."
  * Q2: What is the boarding time of Flight VN178? (A. 3:30 | B. 3:45 | C. 4:15 | D. 4:45) -> Script: "Attention all passengers traveling on Flight VN178 to Ho Chi Minh City. Due to the late arrival of the incoming aircraft, the boarding time has been rescheduled from 3:30 to 3:45."
  * Q3: What will be happening in Lecture hall 4 next Monday? (A. An art workshop | B. An art exhibition | C. A history lesson | D. A talk about history of art) -> Script: "Please note that next Monday's history lesson has been moved. Instead, Lecture hall 4 will host a special talk about the history of art given by Professor Evans."
  * Q4: Where should the teachers park their vehicles tomorrow? (A. In the main school yard | B. Behind the science building | C. At the public stadium | D. Along the main road) -> Script: "Attention all staff members. Due to the construction work in the main school yard tomorrow, please park your vehicles behind the science building until further notice."

- SECTION 2: READING (READING.doc)
  * Q1 to Q2 (Passage 1 - Pandemics): "Diseases are a natural part of life on Earth. If there were no diseases, the population would grow too quickly, and there would not be enough food. The severe Marburg virus, discovered in 1967, has an extremely dangerous fatality rate of 70-80%."
  * Q3 to Q4 (Passage 2 - Japanese Dress Culture): "Kimonos came to Japan from China originally as an undergarment. It later evolved into a traditional T-shaped outer robe. This traditional clothing is securely fastened around the waist with a wide decorative sash known as the Obi belt."

- SECTION 3: WRITING (WRITING.doc) / SECTION 4: SPEAKING (SPEAKING.doc)

# AUDIO REGENERATION TAGS
Always duplicate the core clean English target sentence between `[AUDIO_START]` and `[AUDIO_END]` tags at the very end of your response block to keep the gTTS button active.
"""

# Cấu hình vượt lỗi bộ lọc an toàn cho các tệp ghi âm micro dính tạp âm
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

MODEL_NAME = "gemini-2.5-flash"

# 💾 HỆ THỐNG STATE MANAGEMENT PHÒNG THI KIÊN CỐ
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "mic_key" not in st.session_state:
    st.session_state.mic_key = 0  # Key động bẻ gãy lỗi dính tệp ghi âm cũ qua các vòng lặp

# ⚙️ SIDEBAR ĐIỀU HÀNH PHÒNG THI CHUYÊN GIA
st.sidebar.title("🎓 TRUNG TÂM ĐIỀU HÀNH VSTEP")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password")

st.sidebar.markdown("### 📁 BỘ CHỌN MÃ ĐỀ LUYỆN THI")
selected_de = st.sidebar.selectbox(
    "Chọn Mã đề thi thực chiến:",
    ["Mã đề VSTEP-2026-A (Đề Minh Họa Chuẩn)", "Mã đề VSTEP-2026-B (Đề Phát Triển Biến Thể)", "Mã đề VSTEP-2026-C (Đề Nâng Cao Chuyên Sâu)"]
)

font_size = st.sidebar.slider("Kích thước chữ (Nút chữ T)", 14, 24, 16)
st.markdown(f"<style>.stMarkdown, p, li, .stChatMessage {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)

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

def generate_nav_prompt(action_type, q_num):
    return f"""
    Hành động {action_type}: Đang ở {selected_de}. Hãy hiển thị nội dung câu hỏi độc lập số {q_num} của phần thi hiện tại.
    YÊU CẦU BẮT BUỘC KHÔNG ĐƯỢC QUÊN:
    1. Trích xuất đúng dữ liệu câu hỏi số {q_num} hoặc biến thể song song tương thích độ khó để thay đổi nội dung linh hoạt nếu được yêu cầu.
    2. Nếu đây là phần thi NGHE (LISTENING), bạn phải ghi lại toàn bộ đoạn văn ngữ cảnh bài nghe (Audio Script) độc lập tương ứng nằm ở giữa cặp thẻ [AUDIO_START] và [AUDIO_END] ngay đầu để dựng thanh audio.
    3. Nếu là phần thi ĐỌC (READING), hãy trích xuất đoạn văn nền (Passage Context) tương ứng lên trước câu hỏi.
    4. Hiển thị đầy đủ câu hỏi và 4 phương án trắc nghiệm A,B,C,D. TẤT CẢ các thành phần tiếng Anh xuất hiện (kể cả phương án lựa chọn) bắt buộc phải áp dụng triệt để cấu trúc interlinear 3 dòng ngắt hàng bằng thẻ <br> cứng (ENG - IPA - VIE).
    """

col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    if st.button("⏮️ CÂU TRƯỚC", use_container_width=True):
        st.session_state.current_q = max(st.session_state.current_q - 1, 1)
        nav_action = generate_nav_prompt("quay lại câu trước", st.session_state.current_q)

with col_next:
    if st.button("⏭️ CÂU TIẾP", use_container_width=True):
        st.session_state.current_q = min(st.session_state.current_q + 1, 4)
        nav_action = generate_nav_prompt("tiến câu tiếp theo", st.session_state.current_q)

if st.sidebar.button("🔄 KHỞI ĐỘNG LẠI PHÒNG THI", use_container_width=True):
    st.session_state.current_q = 1
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.mic_key += 1
    if "scored_questions" in st.session_state:
        st.session_state.scored_questions.clear()
    nav_action = f"VỀ MENU CHÍNH CHÀO MỪNG CỦA MÃ ĐỀ {selected_de}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 PHẦN THI NÓI - THU ÂM TRỰC TIẾP")
audio_data = st.sidebar.audio_input(
    "Bấm nút tròn bên dưới để thu âm bài nói trực tiếp:",
    key=f"mic_{st.session_state.mic_key}"
)

# 🏛️ KHÔNG GIAN KHẢO THÍ SỐ HÓA VSTEP
st.title("🎓 SIÊU ỨNG DỤNG KHẢO SÁT TIẾNG ANH VSTEP")
st.caption(f"Cơ sở hạ tầng Master Blueprint hoàn thiện | Đang vận hành: {selected_de}")
st.markdown("---")

# 📊 THANH TRẠNG THÁI TIẾN ĐỘ KHẢO SÁT VÀ BẢNG ĐIỂM SỐ ĐIỆN TỬ
elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(50 * 60 - elapsed_time, 0)
mins, secs = divmod(int(remaining_time), 60)

dash_col1, dash_col2, dash_col3 = st.columns(3)
with dash_col1:
    st.markdown("**📊 THANH TRẠNG THÁI TIẾN ĐỘ KHẢO SÁT**")
    st.progress(st.session_state.current_q / 4)
    st.caption(f"Tiến độ thực tế: Câu {st.session_state.current_q} trên tổng số 4 câu mục tiêu phân hệ.")
with dash_col2:
    st.metric(label="💯 Điểm Số Phòng Thi Hiện Tại", value=f"{st.session_state.score} Điểm")
with dash_col3:
    st.metric(label="⏳ Đồng Hồ Đếm Ngược", value=f"{mins:02d}:{secs:02d} Phút")

st.markdown("---")


def get_model():
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=MASTER_PROMPT,
        safety_settings=SAFETY_SETTINGS,
    )


def extract_text_safely(response):
    """
    Trích xuất văn bản an toàn từ API, bẻ gãy lỗi ẩn nấp im lặng khi bị bộ lọc chặn.
    """
    try:
        if not response.candidates:
            fb = getattr(response, "prompt_feedback", None)
            reason = getattr(fb, "block_reason", "không rõ")
            return None, f"⚠️ Gemini đã từ chối xử lý yêu cầu (block_reason: {reason}). Thầy/cô hãy thử ghi âm lại rõ hơn hoặc giảm tiếng ồn nền."

        candidate = response.candidates[0]
        finish_reason = getattr(candidate, "finish_reason", None)

        parts_text = []
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    parts_text.append(part.text)

        full_text = "".join(parts_text).strip()

        if not full_text:
            return None, f"⚠️ Không nhận được nội dung phản hồi hợp lệ (finish_reason: {finish_reason}). Vui lòng thử lại bằng cách nói to, rõ hơn."

        return full_text, None

    except Exception as e:
        return None, f"⚠️ Lỗi khi đọc phản hồi từ AI: {e}"


# 🚀 THUẬT TOÁN QUÉT VÀ ĐÓNG GÓI THẺ [DIEN_GIAI] THÀNH NÚT BẤM EXPANDER ĐỘNG TRÊN UI
def render_custom_vstep_message(content):
    clean_content = content
    dien_giai_text = ""
    
    if "[DIEN_GIAI_START]" in content and "[DIEN_GIAI_END]" in content:
        start_dg = content.find("[DIEN_GIAI_START]")
        end_dg = content.find("[DIEN_GIAI_END]")
        dien_giai_text = content[start_dg + len("[DIEN_GIAI_START]"):end_dg].strip()
        clean_content = content.replace(content[start_dg:end_dg + len("[DIEN_GIAI_END]")], "")
    
    visible_content = clean_content
    if "[AUDIO_START]" in clean_content and "[AUDIO_END]" in clean_content:
        s_aud = clean_content.find("[AUDIO_START]")
        e_aud = clean_content.find("[AUDIO_END]")
        visible_content = clean_content[:s_aud] + clean_content[e_aud + len("[AUDIO_END]"):]
        
    visible_content = visible_content.replace("[SCORE_UP]", "")
    st.markdown(visible_content, unsafe_allow_html=True)
    
    if dien_giai_text:
        with st.expander("📖 Bấm vào đây để xem CỤM TỪ VÀNG, SƠ ĐỒ TƯ DUY & TRA CỨU TỪ QUÁ KHỨ (Rút gọn)"):
            st.markdown(dien_giai_text, unsafe_allow_html=True)


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


# 🌟 KHỞI TẠO PHÒNG THI LẦN ĐẦU
if "initialized" not in st.session_state and api_key:
    try:
        model = get_model()
        init_res = model.generate_content(f"START_APPLICATION_FOR_CODE_{selected_de}")
        text, err = extract_text_safely(init_res)
        if text:
            st.session_state.messages.append({"role": "assistant", "content": text})
        elif err:
            st.session_state.messages.append({"role": "assistant", "content": err})
        st.session_state.initialized = True
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối bộ não AI: {e}")

# 📜 HIỂN THỊ LÒNG LỊCH SỬ KHẢO THÍ CHUẨN ĐỒ HỌA GIAO DIỆN CHAT
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_custom_vstep_message(message["content"])
            play_audio_safely(message["content"])
        else:
            st.markdown(message["content"], unsafe_allow_html=True)


def send_exam_data(prompt_text, audio_file=None, is_nav=False):
    if not api_key:
        st.sidebar.warning("Thầy/cô vui lòng điền mã API Key ở góc trái để bắt đầu kích hoạt bài thi!")
        return

    try:
        model = get_model()

        if is_nav:
            st.session_state.messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"][-1:]

        formatted_contents = []
        for msg in st.session_state.messages[-4:]:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append({"role": role, "parts": [msg["content"]]})

        if audio_file is not None:
            st.session_state.messages.append({
                "role": "user",
                "content": f"🎤 [Thầy cô đã nộp tệp âm thanh Micro của mã đề {selected_de}]"
            })
            # Sửa cấu trúc định dạng chuẩn phẳng không lồng inline_data cho SDK google-generativeai
            formatted_contents.append({
                "role": "user",
                "parts": [
                    {
                        "mime_type": audio_file.type or "audio/wav",
                        "data": audio_file.getvalue()
                    },
                    prompt_text
                ]
            })
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            formatted_contents.append({"role": "user", "parts": [prompt_text]})

        with st.chat_message("assistant"):
            with st.spinner("Hệ thống chuyên gia đang tính toán điểm và bóc tách dữ liệu..."):
                response = model.generate_content(contents=formatted_contents)
                response_text, err = extract_text_safely(response)

                final_text = response_text if response_text else err

                # Thuật toán tính điểm an toàn trực tiếp trên UI dựa trên tín hiệu [SCORE_UP]
                if response_text and "[SCORE_UP]" in response_text:
                    if "scored_questions" not in st.session_state:
                        st.session_state.scored_questions = set()
                    
                    q_key = f"{selected_de}_q_{st.session_state.current_q}"
                    if q_key not in st.session_state.scored_questions:
                        st.session_state.score += 10
                        st.session_state.scored_questions.add(q_key)

                render_custom_vstep_message(final_text)
                if response_text:
                    play_audio_safely(final_text)

        st.session_state.messages.append({"role": "assistant", "content": final_text})

        if audio_file is not None:
            st.session_state.mic_key += 1  # Làm mới hoàn toàn widget ghi âm tránh nộp trùng

        st.rerun()

    except Exception as e:
        st.error(f"❌ Đường truyền báo lỗi: {e}. Vui lòng làm tươi lại trang bằng phím F5.")


# Kích hoạt luồng điều hướng chuyển dịch câu hỏi từ Sidebar
if nav_action:
    send_exam_data(nav_action, is_nav=True)

# Nộp bài thi Nói / Thu âm phát âm từ Microphone trực tiếp
if audio_data is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI VSTEP", use_container_width=True):
        vstep_speech_command = f"""
        Đây là dữ liệu giọng nói của tôi từ microphone cho câu hỏi độc lập số {st.session_state.current_q} thuộc mã đề {selected_de}. Hãy xử lý nghiêm ngặt theo các bước sau:

        1. [BỘ LỌC THÍNH GIÁC]: Chỉ ghi ra text những từ tôi phát âm rõ ràng, tường minh. Nhuộm ĐỎ những từ sai kèm ký tự IPA sửa sai dưới chân.
        
        2. [UNIVERSAL COMPACT FORMAT]: TẤT CẢ các câu tiếng Anh xuất hiện trong phản hồi bắt buộc phải đi kèm phiên âm và dịch nghĩa nhỏ gọn, xếp tầng đẹp mắt bằng thẻ <br> cứng.

        3. [MÃ HÓA NÚT BẤM DIỄN GIẢI]: Đóng gói toàn bộ phần bóc tách [🎧 CỤM TỪ VÀNG CẦN CHÚ Ý], [🧠 SƠ ĐỒ TƯ DUY CẤU TRÚC - MIND MAP], bẫy đề thi và [⏳ TRA CỨU THÌ QUÁ KHỨ] vào bên trong cặp thẻ [DIEN_GIAI_START] và [DIEN_GIAI_END].

        4. [TÁI SINH NÚT PHÁT ÂM THANH]: Đặt mã [AUDIO_START] Câu tiếng Anh chuẩn [AUDIO_END] ở cuối cùng.
        """
        send_exam_data(vstep_speech_command, audio_file=audio_data)

# Ô nhập text nhận đáp án trắc nghiệm (A, B, C, D) hoặc bài viết tự luận viết
if text_input := st.chat_input("Nhập đáp án (A,B,C,D), số câu/phần hoặc đoạn văn viết tự luận tại đây..."):
    if text_input.strip() in ["1", "2", "3", "4"]:
        send_exam_data(text_input.strip(), is_nav=True)
    else:
        send_exam_data(f"Tôi nộp câu trả lời tại mã đề {selected_de} câu số {st.session_state.current_q} là: {text_input}. Bạn hãy thẩm định đúng/sai (nếu đúng chèn thẻ [SCORE_UP] để cộng điểm). BẮT BUỘC toàn bộ câu tiếng Anh giải thích, sửa sai hay phân tích kết quả bên ngoài hoặc bên trong cặp thẻ [DIEN_GIAI_START] và [DIEN_GIAI_END] đều phải tuân thủ cấu trúc interlinear 3 dòng ngắt hàng bằng thẻ <br> cứng (ENG - IPA - VIE). Nhúng kèm mã [AUDIO_START] câu mẫu [AUDIO_END] ở cuối cùng.")
