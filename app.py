import streamlit as st
import google.generativeai as genai
import random
import streamlit.components.v1 as components
import json
import re
import os

st.set_page_config(page_title="PHYSVERSE 8", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chalkboard+SE&family=Comfortaa:wght=500;700&display=swap');

    /* Responsive cho toàn bộ ứng dụng */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Comfortaa', cursive;
    }

    .main .block-container {
        font-family: 'Comfortaa', cursive;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
    }

    h1, h2, h3 {
        font-family: 'Comfortaa', cursive;
        font-weight: 700;
    }

    /* Bảng phấn viết tay cổ điển */
    .bang-phan {
        background-color: #14452F;
        color: #FFFFFF;
        border: 6px solid #8B5A2B;
        border-radius: 12px;
        padding: 20px;
        box-shadow: inset 0px 0px 20px rgba(0,0,0,0.5), 5px 5px 15px rgba(0,0,0,0.3);
        font-family: 'Chalkboard SE', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
    }

    /* Phòng Neon hiện đại rực rỡ */
    .phong-neon {
        background: #111;
        color: #fff;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #00f0ff;
        box-shadow: 0 0 15px #00f0ff, inset 0 0 15px #00f0ff;
    }

    /* Thẻ danh hiệu vinh danh cuốn hút */
    .the-danh-hieu {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0px 5px 15px rgba(255,215,0,0.4);
    }

    /* Tối ưu hóa hiển thị khung chat và thẻ dữ liệu trên thiết bị di động */
    @media (max-width: 768px) {
        .bang-phan {
            padding: 15px;
            font-size: 14px;
            border-width: 4px;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-2.5-flash"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Lỗi cấu hình API Key: {e}")

if "start_game" not in st.session_state: st.session_state.start_game = False
if "user_dream" not in st.session_state: st.session_state.user_dream = "Chưa chọn"
if "user_confession" not in st.session_state: st.session_state.user_confession = ""
if "user_coins" not in st.session_state: st.session_state.user_coins = 0
if "my_secret_room" not in st.session_state: st.session_state.my_secret_room = ["🚪 Căn Phòng Trống Yên Bình"]
if "saved_study_notes" not in st.session_state: st.session_state.saved_study_notes = "Chưa có ghi chú nào được ghi lại."
if "last_question" not in st.session_state: st.session_state.last_question = None
if "answered_current" not in st.session_state: st.session_state.answered_current = False
if "voice_active_text" not in st.session_state: st.session_state.voice_active_text = ""
if "wrong_attempts" not in st.session_state: st.session_state.wrong_attempts = 0
if "goi_y_nang_cao" not in st.session_state: st.session_state.goi_y_nang_cao = "" # Biến mới lưu trữ phần còn thiếu

TINH_HUONG_THUC_TE = [
    {"npc": "Bo Khù Khờ", "cau_hoi": "Tại sao khi tụi mình lặn xuống hồ bơi sâu một chút là tai lại bị ù và hơi đau vậy bạn?"},
    {"npc": "Bo Khù Khờ", "cau_hoi": "Tớ thấy người ta làm cái đập thủy điện thì cái chân đập ở dưới đáy lúc nào cũng to và dày hơn cái mặt đập ở trên. Sao không làm thẳng băng cho đẹp?"},
    {"npc": "Vy Chảnh Chọe", "cau_hoi": "Nè, một người lặn ở độ sâu 5m trong một cái hồ nhỏ với lặn ở độ sâu 5m ngoài biển khơi thì chỗ nào chịu áp suất lớn hơn? Trả lời sai tôi cười cho xem!"},
    {"npc": "Vy Chảnh Chọe", "cau_hoi": "Tôi đố bạn biết, tại sao khi bóp mạnh vào giữa một bịch sữa giấy đang mở miệng thì sữa lại bắn vọt thẳng lên trên? Áp suất truyền đi kiểu gì?"},
]

KHO_QUA_TANG = {
    "cao": ["👑 Huy Hiệu Kỹ Sư AI Xuất Sắc", "🥼 Áo Blouse Trắng Bác Sĩ Trưởng Khoa", "🧥 Áo Vest Tổng Biên Tập Thời Trang ", "🚀 Huy Hiệu Nhà Sáng Lập Ước Mơ"],
    "trung_binh": ["👓 Kính Mắt Thời Trang", "🎒 Ba Lô Công Nghệ Tích Hợp", "👟 Giày Sneakers Thiết Kế Giới Hạn"],
    "thap": ["🧢 Mũ Lưỡi Trai Vải Canvas", "🏅 Huy Hiệu Chăm Chỉ Vượt Khó", "📝 Sổ Tay Ghi Chú Ý Tưởng Thiên Tài"]
}

CỬA_HÀNG_NỘI_THẤT = {
    "📚 Bàn Học Gỗ Gổ Cổ Điển": 50,
    "💡 Đèn Bàn Phi Hành Gia Galaxy": 30,
    "🎸 Đàn Guitar Thùng Gỗ Sồi": 40,
    "🌱 Chậu Cây Tùng Bồng Lai": 20,
    "🖼️ Tranh Treo Tường": 15,
    "🔮 Quả Cầu Thủy Tinh Tuyết Trắng": 35,
    "🛋️ Ghế Sofa Lười Êm Ái": 45
}

def boc_cau_hoi_ngau_nhien():
    if st.session_state.questions_answered >= 4:
        st.session_state.current_scene = "summary"
    else:
        danh_sach_loc = [q for q in TINH_HUONG_THUC_TE if q["cau_hoi"] != st.session_state.last_question]
        if not danh_sach_loc: danh_sach_loc = TINH_HUONG_THUC_TE
        chon = random.choice(danh_sach_loc)
        st.session_state.last_question = chon["cau_hoi"]
        st.session_state.current_npc = chon["npc"]
        st.session_state.current_question = chon["cau_hoi"]
        st.session_state.current_emotion = "dang_hoi"
        st.session_state.answered_current = False
        st.session_state.wrong_attempts = 0
        st.session_state.goi_y_nang_cao = "" # Reset gợi ý nâng cao câu mới

if not st.session_state.start_game:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FF4B4B; text-shadow: 2px 2px 4px #000000;'>🎒 LỚP HỌC VẬT LÝ VUI NHỘN 📚</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #4A4A4A; font-weight: bold;'>Hóa thân thành Người bạn xuất sắc - Đập tan nỗi sợ Áp suất chất lỏng!</h3>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<div style='background-color: #F0F2F6; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B;'>", unsafe_allow_html=True)
        st.subheader("🌟 Bước 1: Thiết lập Hồ sơ ước mơ ")
        dream_choice = st.selectbox("Ước mơ lớn nhất của bạn là gì?",
                             ["🤖 Kỹ sư Trí tuệ nhân tạo", "🩺 Bác sĩ đa khoa chữa bệnh cứu người", "🎨 Nhà thiết kế thời trang", "🚀 Kỹ sư hàng không vũ trụ NASA", "✨ Khác..."])

        dream = st.text_input("✍️ Gõ ước mơ của bạn nếu chọn Khác:", placeholder="Ví dụ: Nhà tâm lý học...") if dream_choice == "✨ Khác..." else dream_choice
        confession = st.text_area("💬 Chia sẻ những điều khó nói, áp lực học tập hoặc kỳ vọng từ bố mẹ:", placeholder="Bố mẹ muốn con học giỏi môn...")
        st.markdown("</div><br>", unsafe_allow_html=True)

        if st.button("🚀 KÍCH HOẠT KHÔNG GIAN TỰ HỌC!!!", use_container_width=True):
            if not dream.strip(): st.error("💡 Bạn ơi, đừng bỏ trống ước mơ của mình nhé!")
            else:
                st.session_state.user_dream = dream
                st.session_state.user_confession = confession
                st.session_state.start_game = True
                st.rerun()
else:
    if "professor_chat_history" not in st.session_state: st.session_state.professor_chat_history = []
    if "classroom_chat_history" not in st.session_state: st.session_state.classroom_chat_history = []
    if "current_scene" not in st.session_state: st.session_state.current_scene = "onboarding"
    if "progress_score" not in st.session_state: st.session_state.progress_score = 0
    if "questions_answered" not in st.session_state: st.session_state.questions_answered = 0
    if "current_npc" not in st.session_state: st.session_state.current_npc = ""
    if "current_question" not in st.session_state: st.session_state.current_question = ""
    if "current_emotion" not in st.session_state: st.session_state.current_emotion = "dang_hoi"
    if "gift_opened" not in st.session_state: st.session_state.gift_opened = False
    if "unlocked_gift" not in st.session_state: st.session_state.unlocked_gift = None
    if "current_outfit" not in st.session_state: st.session_state.current_outfit = "🧍 Đồng phục Học Sinh Cơ Bản"

    if st.session_state.current_scene == "onboarding":
        st.title("🎒 MÀN HÌNH 1: KHÔNG GIAN NẠP KIẾN THỨC VẬT LÝ 8 ")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='bang-phan'>", unsafe_allow_html=True)
            st.subheader("📝 Tab 1: Cung Cấp Kiến Thức ")
            st.markdown("""
            **CHỦ ĐỀ CỐT LÕI: ÁP SUẤT CHẤT LỎNG**
            * **Công thức cốt lõi:** $p = d \\cdot h$
            * Trong đó:
               - $p$: Áp suất chất lỏng ($N/m^2$ hoặc $Pa$)
               - $d$: Trọng lượng riêng của chất lỏng ($N/m^3$)
               - $h$: Chiều sâu tính từ mặt thoáng chất lỏng đến điểm xét ($m$)
            * **Bản chất vật lý:** Càng xuống sâu ($h$ tăng) thì áp suất $p$ càng lớn. Tính $h$ từ đáy bình lên là SAI hoàn toàn!

            ---
            **⚖️ ĐỊNH LUẬT PASCAL**
            * **Nội dung định luật:** Áp suất tác dụng lên một chất lỏng chứa trong bình kín được chất lỏng truyền đi nguyên vẹn theo mọi hướng.
            * **Ý nghĩa thực tế:** Định luật Pascal cho phép truyền và khuếch đại lực thông qua chất lỏng. Chỉ cần tác dụng một lực nhỏ lên piston có diện tích nhỏ, ta có thể tạo ra lực lớn hơn nhiều ở piston có diện tích lớn!
            """)
            st.markdown("</div><br>", unsafe_allow_html=True)
            ghi_chu_tam_thoi = st.text_area("✍️ Tab 2: Take Note cá nhân:", placeholder="Tự tay cấu trúc lại kiến thức...")

            if st.button("MÌNH ĐÃ HIỂU RÕ BẢN CHẤT, SẴN SÀNG GIẢNG BÀI! 🚀"):
                if ghi_chu_tam_thoi.strip(): st.session_state.saved_study_notes = ghi_chu_tam_thoi
                st.session_state.questions_answered = 0
                st.session_state.progress_score = 0
                boc_cau_hoi_ngau_nhien()
                st.session_state.current_scene = "classroom"
                st.rerun()

        with col2:
            st.subheader("👨‍🏫 Hỏi Đáp Chất Vấn Giáo Sư Học Thuật AI")
            try:
                model_giao_su = genai.GenerativeModel(
                    model_name=MODEL_NAME,
                    system_instruction="Bạn là Giáo sư Vật lý AI thân thiện. Hãy giải thích ngắn gọn, dễ hiểu câu hỏi về áp suất chất lỏng."
                )

                for msg in st.session_state.professor_chat_history:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                giao_su_input = st.chat_input("Hỏi Giáo sư về điểm chưa rõ...")

                if giao_su_input:
                    with st.chat_message("user"):
                        st.write(giao_su_input)
                    st.session_state.professor_chat_history.append({"role": "user", "content": giao_su_input})

                    with st.chat_message("assistant"):
                        with st.spinner("Giáo sư đang trả lời..."):
                            formatted_history = [
                                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                                for m in st.session_state.professor_chat_history
                            ]
                            chat_session = model_giao_su.start_chat(history=formatted_history[:-1])
                            response = chat_session.send_message(giao_su_input)
                            st.write(response.text)

                    st.session_state.professor_chat_history.append({"role": "assistant", "content": response.text})
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Khung chat gặp sự cố kỹ thuật: {e}")

    elif st.session_state.current_scene == "classroom":
        st.title("🏫 MÀN HÌNH 2: ĐỊNH HÌNH, HỆ THỐNG LẠI KIẾN THỨC")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        col_stat1.metric("Số câu đã hỗ trợ các bạn", f"{st.session_state.questions_answered} / 4")
        col_stat2.metric("Điểm Uy Tín ", f"{st.session_state.progress_score} XP")
        col_stat3.metric("Ví Tiền Thưởng 💰", f"{st.session_state.user_coins} Coins")

        st.write("---")
        col_npc, col_chat = st.columns([1, 2])

        with col_npc:
            st.subheader("👤 Các bạn Của Bạn")
            if st.session_state.current_npc == "Bo Khù Khờ":
                if st.session_state.current_emotion == "khen_ngoi": st.success("🤩 **Bạn Bo Khù Khờ** đang tròn xoe mắt nể phục!")
                elif st.session_state.current_emotion == "gai_dau": st.warning("🧐 **Bạn Bo Khù Khờ** gãi đầu hoang mang...")
                else: st.warning("🤖 **Bạn Bo Khù Khờ** chờ bạn chỉ bài...")
            else:
                if st.session_state.current_emotion == "khen_ngoi": st.success("👑 **Bạn Vy Chảnh Chọe** đã gật gù bái phục!")
                elif st.session_state.current_emotion == "gai_dau": st.error("🙄 **Bạn Vy Chảnh Chọe** đang nhướng mày chê bai!")
                else: st.error("👑 **Bạn Vy Chảnh Chọe** đang thách thức bạn...")

            st.markdown(f"<div style='background-color:#FFF3CD; padding:15px; border-radius:10px; border:1px solid #FFA000;'><b>NPC Hỏi:</b> {st.session_state.current_question}</div>", unsafe_allow_html=True)

            # HỘP THOẠI GỢI Ý ĐÁP ÁN NÂNG CAO XUẤT HIỆN KHI ĐÚNG TRÊN 80% (>= 48 ĐIỂM NHƯNG CHƯA ĐẠT 60)
            if st.session_state.goi_y_nang_cao:
                st.info(f"💡 **GỢI Ý NÂNG CAO (Bạn đã đúng trên 80%):**\n\n{st.session_state.goi_y_nang_cao}")

            if st.session_state.wrong_attempts >= 1:
                st.write("")
                with st.popover("💡 Xem Gợi Ý Tư Duy Cơ Bản", use_container_width=True):
                    st.markdown("""
                    **🧐 Gợi ý kích thích tư duy cho bạn:**
                    * Hãy nhớ lại công thức cốt lõi: $p = d \\cdot h$. Yếu tố nào đang thay đổi trong tình huống này?
                    * Đối với câu hỏi về bịch sữa hoặc máy nén, hãy lưu ý cách áp suất truyền đi trong không gian kín (Định luật Pascal)!
                    * Áp suất chất lỏng phụ thuộc vào trọng lượng riêng và độ sâu ($h$). Biển và hồ nước ngọt có trọng lượng riêng $d$ giống nhau không?
                    * Càng lặn sâu, áp lực tác dụng lên tai thay đổi như thế nào? Sự chênh lệch áp suất ngoài mặt màng nhĩ và trong hòm nhĩ gây ra hiện tượng gì?
                    """)

            if st.session_state.answered_current:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("TIẾP TỤC GIÚP ĐỠ BẠN HỌC KHÁC ➡️", use_container_width=True):
                    st.session_state.questions_answered += 1
                    st.session_state.classroom_chat_history = []
                    st.session_state.answered_current = False
                    st.session_state.current_emotion = "dang_hoi"
                    st.session_state.voice_active_text = ""
                    st.session_state.wrong_attempts = 0
                    st.session_state.goi_y_nang_cao = ""
                    boc_cau_hoi_ngau_nhien()
                    st.rerun()

        with col_chat:
            st.subheader("💬 Lớp Học Tương Tác")
            for chat in st.session_state.classroom_chat_history:
                with st.chat_message(chat["role"]): st.write(chat["content"])

            custom_mic_component = components.html("""
            <div style="display: flex; align-items: center; gap: 10px; font-family: sans-serif;">
                <button id="start-record-btn" style="background-color: #FF4B4B; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                    🎤 Bấm để Nói (Giảng bài bằng Giọng nói)
                </button>
                <p id="status" style="color: #666; margin: 0; font-size: 14px;">Micro đang tắt</p>
            </div>
            <script>
                const startBtn = document.getElementById('start-record-btn');
                const statusText = document.getElementById('status');
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'vi-VN';
                    startBtn.addEventListener('click', () => { recognition.start(); statusText.innerText = "🔴 Đang nghe..."; startBtn.style.backgroundColor = "#28a745"; });
                    recognition.onresult = (event) => {
                        const resultText = event.results[0][0].transcript;
                        window.parent.postMessage({type: 'streamlit:set_widget_value', value: resultText, element_id: 'voice_bridge'}, '*');
                    };
                }
            </script>
            """, height=60)

            loi_giang_voice = st.text_input("", key="voice_bridge", label_visibility="collapsed")

            loi_giang_text = None
            if not st.session_state.answered_current:
                loi_giang_text = st.chat_input("Gõ lời giảng giải hoặc bổ sung tại đây...")

            loi_giang = ""
            if loi_giang_voice and loi_giang_voice != st.session_state.voice_active_text:
                loi_giang = loi_giang_voice
                st.session_state.voice_active_text = loi_giang_voice
            elif loi_giang_text:
                loi_giang = loi_giang_text

            if loi_giang:
                st.session_state.classroom_chat_history.append({"role": "user", "content": loi_giang})

                unified_prompt = f"""
                Bạn đang đóng vai nhân vật học sinh lớp 8 tên là {st.session_state.current_npc} để chấm điểm bài giảng Vật lý của người dùng dựa theo ĐỘ CHÍNH XÁC KHOA HỌC (Thang điểm tối đa là 60).

                Tính cách nhân vật phản hồi:
                - Bo Khù Khờ: Nam sinh ngây ngô, dễ mến. Nếu giảng đúng (>=48 điểm) thì nể phục. Nếu sai (<48 điểm) thì hoang mang gãi đầu hỏi lại.
                - Vy Chảnh Chọe: Nữ sinh kiêu kỳ. Nếu đúng (>=48 điểm) thì khen ngợi công nhận ước mơ {st.session_state.user_dream} của người dùng. Nếu sai thì mỉa mai sắc sảo.

                CÂU HỎI HIỆN TẠI: "{st.session_state.current_question}"
                LỜI GIẢNG MỚI NHẤT CỦA NGƯỜI DÙNG: "{loi_giang}"
                LỊCH SỬ TRANH LUẬN TRƯỚC ĐÓ: {st.session_state.classroom_chat_history}

                TIÊU CHÍ CHẤM ĐIỂM (Tối đa 60 điểm):
                - Hãy tính toán tỷ lệ % chính xác của câu trả lời dựa trên các từ khóa vật lý:
                  + Đạt 60 điểm (100%): Giải thích hoàn hảo toàn bộ cơ chế, có công thức hoặc bản chất chuẩn xác.
                  + Đạt từ 48 đến 59 điểm (Đã đúng trên 80%): Đã nói được ý chính cực tốt nhưng thiếu một vài chi tiết nhỏ để đạt điểm tối đa.
                  + Dưới 48 điểm (<80%): Chưa giải thích đúng bản chất khoa học hoặc gõ linh tinh.

                BẮT BUỘC TRẢ VỀ JSON THUẦN TÚY (TUYỆT ĐỐI không bao bọc trong ký tự ```json):
                {{
                    "ket_qua": "DUONG" (nếu diem_so >= 48) hoặc "SAI" (nếu diem_so < 48),
                    "diem_so": số điểm chính xác từ 0 đến 60 dựa trên độ hoàn thiện kiến thức,
                    "loi_thoai_npc": "Lời thoại phản hồi tương ứng dựa trên tính cách nhân vật",
                    "thong_tin_con_thieu": "Nếu diem_so đạt từ 48-59 (trên 80%), hãy chỉ rõ những từ khóa hoặc ý nhỏ nào người dùng cần bổ sung để ăn trọn 60 điểm. Nếu điểm dưới 48 hoặc bằng 60, hãy để trống chuỗi này "
                }}
                """

                phan_hoi_npc = "Tớ chưa hiểu lắm, bạn giảng giải kỹ hơn bằng bản chất khoa học được không?"
                diem_cong = 0

                with st.spinner("Học sinh AI đang phân tích bài giảng..."):
                    try:
                        model_unified = genai.GenerativeModel(model_name=MODEL_NAME)
                        response = model_unified.generate_content(unified_prompt)
                        raw_text = response.text.strip()

                        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                        if match:
                            clean_json = match.group(0)
                            data_eval = json.loads(clean_json)

                            diem_cong = int(data_eval.get("diem_so", 0))
                            con_thieu = data_eval.get("thong_tin_con_thieu", "").strip()

                            if data_eval.get("ket_qua") == "DUONG":
                                st.session_state.current_emotion = "khen_ngoi"
                                st.session_state.wrong_attempts = 0
                                st.session_state.answered_current = True

                                # Nếu đúng trên 80% nhưng chưa tối đa, lưu thông tin gợi ý nâng cao
                                if con_thieu:
                                    st.session_state.goi_y_nang_cao = con_thieu
                                else:
                                    st.session_state.goi_y_nang_cao = ""
                            else:
                                diem_cong = 0
                                st.session_state.current_emotion = "gai_dau"
                                st.session_state.wrong_attempts += 1
                                st.session_state.answered_current = False
                                st.session_state.goi_y_nang_cao = ""

                            phan_hoi_npc = data_eval.get("loi_thoai_npc", phan_hoi_npc)
                    except Exception as e:
                        diem_cong = 0
                        st.session_state.current_emotion = "gai_dau"
                        st.session_state.wrong_attempts += 1

                st.session_state.progress_score += diem_cong
                st.session_state.user_coins += int(diem_cong / 2)
                st.session_state.classroom_chat_history.append({"role": "assistant", "content": phan_hoi_npc})
                st.rerun()

    elif st.session_state.current_scene == "summary":
        st.title("🏆 MÀN HÌNH TỔNG KẾT: KHÔNG GIAN VINH DANH")
        st.balloons()

        cap_bac = "🥇 BẬC THẦY SƯ PHẠM " if st.session_state.progress_score >= 180 else ("🥈 GIA SƯ ĐỒNG HÀNH" if st.session_state.progress_score >= 90 else "🥉 TẬP SỰ CHĂM CHỈ")
        st.markdown(f"<div class='the-danh-hieu'><h2>{cap_bac}</h2><p>Hệ thống vinh danh năng lực học tập của bạn!</p></div>", unsafe_allow_html=True)

        st.markdown(f"### 🎉 Chúc mừng bạn đã hoàn thành xuất sắc nhiệm vụ! Mục tiêu: **{st.session_state.user_dream}**")
        st.info(f"📊 Kết quả: Tổng Điểm: **{st.session_state.progress_score} XP** | Tài sản: **{st.session_state.user_coins} Coins**")

        vung_chon = st.sidebar.radio("🧭 LỰA CHỌN KHÔNG GIAN:", ["🚪 Ngôi Nhà Của Tôi", "🏪 Cửa Hàng Nội Thất Thần Kỳ", "🎁 Mở Hộp Quà Danh Hiệu", "📓 Sổ Tay Nhật Ký Học Tập"])

        if vung_chon == "🚪 Ngôi Nhà Của Tôi":
            st.markdown("<div class='phong-neon'>", unsafe_allow_html=True)
            st.subheader("🏡 Không gian phản chiếu sự nỗ lực cá nhân")
            for item in st.session_state.my_secret_room: st.markdown(f"- **{item}**")
            st.caption(f"👔 Bộ đồ đang mặc: **{st.session_state.current_outfit}**")
            st.markdown("</div>", unsafe_allow_html=True)

        elif vung_chon == "🏪 Cửa Hàng Nội Thất Thần Kỳ":
            st.subheader("🏪 Cửa hàng nội thất thần kỳ")
            st.write(f"Số coins khả dụng của bạn: **{st.session_state.user_coins} Coins**")

            for item, cost in CỬA_HÀNG_NỘI_THẤT.items():
                col_item, col_buy = st.columns([2, 1])
                with col_item: st.write(f"{item} — 💰 giá: **{cost} Coins**")
                with col_buy:
                    if item in st.session_state.my_secret_room:
                        st.button("Đã sở hữu", disabled=True, key=f"owned_{item}")
                    else:
                        if st.button(f"Mua sắm 🛒", key=f"buy_{item}"):
                            if st.session_state.user_coins >= cost:
                                st.session_state.user_coins -= cost
                                st.session_state.my_secret_room.append(item)
                                st.success(f"Đã mua thành công {item}!")
                                st.rerun()
                            else:
                                st.error("❌ Bạn không đủ số Coins tích lũy! Hãy chăm chỉ chỉ bài để kiếm thêm thu nhập nhé.")

        elif vung_chon == "🎁 Mở Hộp Quà Danh Hiệu":
            st.subheader("🎁 Hộp quà danh hiệu")
            if not st.session_state.gift_opened:
                if st.button("🎁 BẤM ĐỂ MỞ HỘP QUÀ"):
                    danh_muc = "cao" if st.session_state.progress_score >= 150 else ("trung_binh" if st.session_state.progress_score >= 80 else "thap")
                    qua_tang = random.choice(KHO_QUA_TANG[danh_muc])
                    st.session_state.unlocked_gift = qua_tang
                    st.session_state.current_outfit = qua_tang
                    st.session_state.gift_opened = True
                    st.rerun()
            else:
                st.success(f"🎉 Bạn đã mở được phần quà danh hiệu: **{st.session_state.unlocked_gift}**")

        elif vung_chon == "📓 Sổ Tay Nhật Ký Học Tập":
            st.subheader("📓 Nhật Ký Học Tập Cá Nhân")
            st.markdown(f"<div style='background-color:#FFF; padding:20px; border-left:5px solid #28a745; color:#333;'><i>\"{st.session_state.saved_study_notes}\"</i></div>", unsafe_allow_html=True)

        st.write("---")
        if st.button("🔄 QUAY LẠI TỪ ĐẦU ĐỂ ÔN TẬP LÝ THUYẾT"):
            st.session_state.current_scene = "onboarding"
            st.session_state.professor_chat_history = []
            st.session_state.classroom_chat_history = []
            st.session_state.progress_score = 0
            st.session_state.user_coins = 0
            st.session_state.questions_answered = 0
            st.session_state.last_question = None
            st.session_state.answered_current = False
            st.session_state.voice_active_text = ""
            st.session_state.wrong_attempts = 0
            st.session_state.goi_y_nang_cao = ""
            st.rerun()
