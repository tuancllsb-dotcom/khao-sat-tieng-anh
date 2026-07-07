import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
import tempfile  # ✨ Lời chúc "Thuận buồm xuôi gió" - Thư viện tạo file tạm thời an toàn
import os        # ✨ Lời chúc "Vạn sự hanh thông" - Thư viện dọn dẹp bộ nhớ hệ thống

# ✨ "Hiền tài là nguyên khí của quốc gia." - Chúc thầy cô luôn tràn đầy năng lượng và niềm vui sư phạm!
st.set_page_config(
    page_title="Hệ Thống Khảo Sát Tiếng Anh Cho Giáo Viên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧠 "Muốn biết phải hỏi, muốn giỏi phải học." - Hệ thống tư duy giải phẫu 4 Hộp luôn đồng hành cùng thầy cô chinh phục đỉnh cao ngôn ngữ.
MASTER_PROMPT = """
# ROLE & PERSONALITY
You are the official interactive "English Proficiency Assessment Application for Teachers", inheriting 20+ years of expertise in Applied Linguistics, Language Pedagogy, and Cognitive Psychology. Your absolute objective is to train the teacher (addressed respectfully as "thầy cô") to effortlessly pass their 4-skill standardized exam within an intensive timeline using Reverse Engineering, Pareto 80/20, Chunking, and Real-Time Multimodal Feedback.

# MANDATORY OUTPUT STRUCTURE & FORMATS
For EVERY concept, reading text, listening transcript, question, or template phrase you introduce, you MUST strictly generate the output using these two structural components:

### [🧠 LINEAR MINDMAP STRUCTURAL FLOW]
Display a step-by-step visual text flow diagram using text-blocks, numbers, and arrows (e.g., Intro -> Reason 1 -> Example -> Conclusion) to illustrate exactly how ideas are logically sequenced before diving into details.

### [四 4-BOX ANATOMY GENERATOR]
1. [📦 BẢN GỐC & DỊCH NGHĨA]: Full English text + Contextual Vietnamese translation.
2. [🎵 PHIÊN ÂM QUỐC TẾ IPA]: Standard IPA phonetic transcription broken into rhythmic semantic chunks using the / symbol for proper pausing and intonation.
3. [🧬 GIẢI PHẪU NGỮ PHÁP CÚ PHÁP]: Granular grammatical and syntactic breakdown in Vietnamese. Explain: Why is this sentence written like this? Why does this specific word sit at this exact position? What is its dynamic relationship with surrounding words? How does this structural combination fulfill Level 4 (B2) criteria?
4. [💼 ỨNG DỤNG THỰC CHIẾN GIAO TIẾP]: Explicitly demonstrate how the teacher can instantly adapt this exact pattern, phrase, or sentence to speak or write in real-life classroom management, school administration, or daily professional communication.

# AUDIO SYNCHRONIZATION TAGS
Every time you generate English audio content meant for the Listening section or as an oral speech template, you MUST explicitly wrap that specific segment between [AUDIO_START] and [AUDIO_END] tags. The underlying Streamlit code converts everything inside these tags into high-quality spoken audio dynamically.

# EMBEDDED EXAM BANK & LESSON PROGRESSION (DE 1 TO DE 4)
You must guide the user strictly through the official exam content gathered from source materials:
- SECTION 1: LISTENING (12 Questions): 
  * Part 1: Short situations (Topics: families/neighbors/coworkers; Locations: bank/supermarket/police station/driver's bureau; Actions: buying dress/suit).
  * Part 2: Long conversation (Questions 4-7: Sandra Harrington talk at the Book Fair, ticket delivery methods via email/post/text/fax, transport from city center).
  * Part 3: Long lecture (Questions 8-12: Sally leading an Olympic site tour, historical buildings transformation from industrial to offices/shops, residents' demands, and station construction contracts).
- SECTION 2: READING (12 Questions): 
  * Passage 1: Practical Text (300-350 words) on "Diseases and Pandemics" (1918 Flu virus outbreak, Marburg virus vs. pandemic criteria, SARS close monitoring).
  * Passage 2: Academic Text (450-500 words) on "History and Evolution of Japanese Kimonos" (China origins, Heian period, straight-line cutting by seamstresses, fabric costs, and its role as a cultural icon).
- SECTION 3: WRITING & SPEAKING (Opinion Paragraph): 
  * Topic A: Living in a city vs. Countryside (Job opportunities, conveniences, environment, quality of life, community relationships).
  * Topic B: Reading habits should be encouraged among teenagers (Increases knowledge, reduces stress, improves memory).

# COGNITIVE MUTATION & PROGRESSION CHECKPOINT
- FIXED CORE FRAMEWORKS: You must keep the academic connecting sentence frames (e.g., "It is widely believed that...", "First and foremost...", "In addition, spending time on... plays an important role in...", "If they did not..., they would...", "In conclusion, taking everything into consideration...") 100% CONSTANT across all generated modules so they lock into the user's muscle memory.
- VARIABLE CONTEXT FIELDS: Dynamically mutate vocabulary nouns, reading prompts, and listening scenarios when the user moves from Đề 1 to Đề 4 based on the embedded bank themes.
- At the end of each session, always prompt the user with: "Thầy/Cô đã thành thạo nội dung này chưa? [1] Đã thành thạo (Chuyển bước tiếp theo) | [2] Chưa thành thạo (Luyện tập lại phần này với biến thể từ vựng mới)".

# INITIALIZATION EXECUTION
Boot up immediately as an interactive exam software interface. Do not provide meta-commentary, chatting, or prefaces. Display the greeting sequence in Vietnamese:
"Hệ thống Khảo Sát Tiếng Anh Thực Chiến Dành Cho Giáo Viên đã sẵn sàng. 
[SƠ ĐỒ TƯ DUY LỘ TRÌNH]
10 Ngày Học ──> Master 6 Khung xương vạn năng cố định ──> Biến đổi đề thích ứng (Đề 1 đến Đề 4) ──> Giải phẫu cú pháp 4 Hộp ──> Chinh phục kỳ thi & Giao tiếp thực tế.

Vui lòng chọn tính năng bên Bản điều hướng phòng thi hoặc nhập số tương ứng (`1`, `2`, `3`) để bắt đầu luyện tập phản xạ ngay lập tức."
"""

# ⚙️ "Muốn sang thì bắc cầu Kiều, muốn con hay chữ thì yêu lấy thầy." - Thanh công cụ điều hướng thông minh hỗ trợ thầy cô làm chủ phòng thi.
st.sidebar.title("⚙️ BẢN ĐIỀU HƯỚNG PHÒNG THI")

# 🔒 "Thuận buồm xuôi gió" - Tự động gọi mã Key bảo mật từ hệ thống Secrets để thầy cô không phải nhập tay mỗi lần mở app
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password")

font_size = st.sidebar.slider("2. NÚT CHỮ T (Kích thước chữ)", 14, 24, 16)

# 🔤 "Chữ nổi trí thông, lòng sáng trí suốt." - Tự động tối ưu hóa kích thước hiển thị giúp bảo vệ đôi mắt ngọc ngà của thầy cô.
st.markdown(f"<style>.stMarkdown, p, li, .stChatMessage {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)

st.sidebar.markdown("### 🛠️ CHUYỂN PHẦN THI")
nav_action = None
col_nav1, col_nav2 = st.sidebar.columns(2)
with col_nav1:
    if st.sidebar.button("⏮️ QUAY LẠI", use_container_width=True):
        nav_action = "QUAY LẠI PHẦN TRƯỚC"
    if st.sidebar.button("🔄 LÀM LẠI", use_container_width=True):
        nav_action = "LUYỆN TẬP LẠI ĐỀ NÀY"
with col_nav2:
    if st.sidebar.button("▶️ TIẾP THEO", use_container_width=True):
        nav_action = "CHUYỂN PHẦN TIẾP THEO"
    if st.sidebar.button("🏠 MENU", use_container_width=True):
        nav_action = "VỀ MENU CHÍNH"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 PHẦN THI NÓI - THU ÂM")
audio_data = st.sidebar.audio_input("Bấm nút tròn để ghi âm trực tiếp:")
uploaded_file_data = st.sidebar.file_uploader("Hoặc tải tệp âm thanh bài nói lên tại đây:", type=["mp3", "wav", "m4a", "webm"])

# 💾 "Tre già măng mọc, học hỏi không ngừng." - Khởi tạo cấu trúc bộ nhớ đệm giúp lưu giữ trọn vẹn từng khoảnh khắc tiến bộ của thầy cô.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=MASTER_PROMPT)
        st.session_state.chat_session = model.start_chat(history=[])
        init_res = st.session_state.chat_session.send_message("START_APPLICATION")
        st.session_state.messages.append({"role": "assistant", "content": init_res.text})
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối hệ thống: {e}")

# 🏛️ "Vì lợi ích mười năm thì phải trồng cây, vì lợi ích trăm năm thì phải trồng người." - Chào mừng thầy cô đến với giảng đường số hóa thông minh.
st.title("🎓 ỨNG DỤNG KHẢO SÁT TIẾNG ANH CHO GIÁO VIÊN")
st.caption("Giao diện tối ưu Cloud Run & Win.exe - Chống lỗi mất tiếng và tràn bố cục")
st.markdown("---")

# 🎵 "Thánh thót như tiếng đàn cầm." - Bộ giải mã âm thanh cao cấp chuyển chữ thành giọng đọc bản xứ truyền cảm hứng.
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
                audio_html = f'<audio controls autoplay src="data:audio/mp3;base64,{b64_audio}" style="width: 100%; margin-top: 10px;"></audio>'
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Lỗi tự động phát âm thanh: {e}")

# 📜 "Học đi đôi với hành, ôn cố nhi tri tân." - Tái hiện dòng lịch sử hội thoại, giúp thầy cô dễ dàng hệ thống hóa kiến thức đã qua.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            play_audio_safely(message["content"])

# 🚀 "Đường đi không khó vì ngăn sông cách núi, mà khó vì lòng người ngại núi e sông." - Hàm chuyển tiếp luồng tư duy sư phạm sang siêu trí tuệ nhân tạo.
def send_exam_data(payload):
    if "chat_session" in st.session_state:
        if isinstance(payload, str):
            st.session_state.messages.append({"role": "user", "content": payload})
            with st.chat_message("user"):
                st.markdown(payload)
        else:
            st.session_state.messages.append({"role": "user", "content": "🔄 Đã nộp tệp tin ghi âm bài thi Nói."})
            with st.chat_message("user"):
                st.markdown("🔄 Đã nộp tệp tin ghi âm bài thi Nói.")
        
        with st.chat_message("assistant"):
            with st.spinner("Hệ thống đang phân tích ngữ pháp..."):
                res = st.session_state.chat_session.send_message(payload)
                st.markdown(res.text)
                play_audio_safely(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
    else:
        st.sidebar.warning("Thầy/cô vui lòng điền mã API Key ở góc trái hoặc cấu hình Secrets để bắt đầu kích hoạt bài thi!")

# 🧭 "Đi một ngày đàng, học một sàng khôn." - Lắng nghe mệnh lệnh từ thanh điều hướng (Đã dọn dẹp lệnh trùng lặp giúp chạy siêu tốc).
if nav_action:
    send_exam_data(f"Thực hiện lệnh điều hướng phần thi: {nav_action}")

# 🎤 "Chim khôn kêu tiếng rảnh rang, người khôn nói tiếng dịu dàng dễ nghe." - Gom nguồn âm thanh từ cả hai cổng và đẩy lên đám mây bảo mật.
active_audio = audio_data if audio_data is not None else uploaded_file_data

if active_audio is not None:
    if st.sidebar.button("🚀 NỘP BÀI THI NÓI", use_container_width=True):
        bytes_data = active_audio.getvalue()
        file_suffix = os.path.splitext(active_audio.name)[1] if hasattr(active_audio, 'name') and active_audio.name else ".webm"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
            tmp_file.write(bytes_data)
            tmp_file_path = tmp_file.name
        
        try:
            uploaded_file = genai.upload_file(path=tmp_file_path, mime_type=active_audio.type)
            send_exam_data([uploaded_file, "Đây là file ghi âm bài nói của tôi. Hãy phân tích phát âm và hiển thị cấu trúc 4 Hộp giải phẫu."])
            os.unlink(tmp_file_path)
        except Exception as e:
            st.sidebar.error(f"Lỗi xử lý luồng âm thanh đám mây: {e}")

# 📝 "Chữ viết là tiếng nói của tâm hồn và trí tuệ." - Hộp thoại tương tác chữ cố định tại đáy màn hình, luôn sẵn sàng đón nhận những ý tưởng xuất sắc của thầy cô.
if text_input := st.chat_input("Nhập đáp án hoặc bài viết của thầy cô tại đây..."):  
    send_exam_data(text_input)
