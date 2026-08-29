import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="🎬 강의 영상 도우미", page_icon="🎬", layout="wide")

# ---- 테마 CSS (보라/틸 톤) ----
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    section[data-testid="stSidebar"] * { color: #ede9fe !important; }
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 10px;
        text-align: left;
        padding: 10px 14px;
        margin-bottom: 6px;
        width: 100%;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.16);
        border-color: #a78bfa;
    }
    .cat-header {
        font-size: 22px; font-weight: 800; color: #312e81;
        margin-bottom: 4px;
    }
    .cat-time {
        display: inline-block; background: #ede9fe; color: #6d28d9;
        font-weight: 700; font-size: 13px; padding: 3px 10px;
        border-radius: 999px; margin-bottom: 14px;
    }
    .summary-box {
        background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 14px;
        padding: 18px 20px; margin-top: 14px;
    }
    .summary-box li { margin-bottom: 8px; line-height: 1.6; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Vimeo 영상 정보 ----
VIMEO_VIDEO_ID = "1221651006"
VIMEO_HASH = "ecf1d87214"

# ---- 카테고리 데이터 (영상 흐름 순서대로) ----
# start_seconds: 해당 구간이 시작되는 영상 내 시점
CATEGORIES = [
    {
        "icon": "🗂️", "title": "수업 운영 안내", "start_seconds": 0,
        "time_label": "00:00:00",
        "summary": [
            "Discord를 수업 소통 채널로 사용하며, 시작 전 화면과 음성이 잘 전달되는지부터 확인",
            "이해도 체크 방식 안내: 잘 이해됐으면 O, 애매하면 물음표, 잘 모르겠으면 X로 표시하도록 요청",
            "아직 Discord에 가입하지 않은 수강생이 많아, 1교시 안에 가입과 체크를 완료해달라고 당부",
        ],
    },
    {
        "icon": "📚", "title": "커리큘럼 소개", "start_seconds": 309,
        "time_label": "00:05:09",
        "summary": [
            "총 160시간 과정이며, 사전에 안내한 커리큘럼은 초안이라 진도에 따라 유동적으로 조정될 예정",
            "기본 개념부터 시작해 점차 AI 기능을 추가해나가는 방식으로 난이도를 확장",
            "왕초보 수강생을 위해 미리 준비한 사전학습 자료(Claude Code로 제작)를 소개",
        ],
    },
    {
        "icon": "🛠️", "title": "필요 도구 준비", "start_seconds": 511,
        "time_label": "00:08:31",
        "summary": [
            "ChatGPT, Claude, Gemini 계정은 필수, 중국계 AI 서비스는 정보보안 이슈로 선택사항으로 안내",
            "GitHub와 Notion 계정 가입을 필수로 안내 (Notion을 이번에 처음 써보는 수강생도 다수)",
            "여러 AI 서비스를 비교해서 써보며 본인에게 맞는 도구를 찾아볼 것을 권장",
        ],
    },
    {
        "icon": "🙋", "title": "자기소개 & 팀 빌딩", "start_seconds": 3693,
        "time_label": "01:01:33",
        "summary": [
            "수강생들이 관심 분야, 만들고 싶은 앱, 좋아하는 음식 등을 자유롭게 자기소개",
            "목적은 이후 팀 프로젝트 매칭 — 관심사가 비슷한 사람끼리 팀을 구성하기 위함",
            "처음에는 혼자 힘으로 만들어보는 경험을 먼저 쌓은 뒤, 이후 팀 프로젝트로 확장할 예정",
        ],
    },
    {
        "icon": "💻", "title": "터미널 · VS Code 설치", "start_seconds": 8141,
        "time_label": "02:15:41",
        "summary": [
            "터미널을 사용하는 이유와 장점을 설명하고, 첫 실행까지 함께 진행",
            "VS Code 설치와 관련 확장 프로그램 설치 방법 안내",
            "설치가 어려운 수강생은 별도로 개별 지원하겠다고 안내",
        ],
    },
    {
        "icon": "🤖", "title": "Claude Code 설치 & 실습", "start_seconds": 10709,
        "time_label": "02:58:29",
        "summary": [
            "Node.js와 Claude Code를 함께 설치 (최근에는 Claude Code 단독 설치도 가능해졌다고 언급)",
            "Windows와 Mac 환경을 번갈아 시연하며 CLI, Desktop, 웹 등 다양한 실행 방식을 소개",
            "실습으로 간단한 웹페이지(예: 벽돌깨기 게임)를 직접 만들어보는 시간을 진행",
        ],
    },
    {
        "icon": "🏁", "title": "실습 결과 & 마무리", "start_seconds": 16724,
        "time_label": "04:38:44",
        "summary": [
            "index.html 등 기본 개념을 몰라 실행에 어려움을 겪는 수강생들을 개별적으로 지원",
            "\"명령을 그대로 치는 게 아니라 원하는 결과를 구체적으로 설명하는\" 프롬프트 엔지니어링의 중요성을 강조",
            "배포(Vercel 연결 등)는 다음 단계 과제로 남기고 수업을 마무리하며, 앞으로 3개월간 팀워크·실전 프로젝트를 이어갈 예정임을 안내",
        ],
    },
]

# ---- 세션 상태 초기화 ----
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 사이드바: 카테고리 목록 =================
with st.sidebar:
    st.markdown("## 🎬 강의 목차")
    st.caption("260826_2기 인공지능 특급")
    st.write("")
    for i, cat in enumerate(CATEGORIES):
        label = f'{cat["icon"]}  {cat["title"]}  ·  {cat["time_label"]}'
        if st.button(label, key=f"cat_{i}", use_container_width=True):
            st.session_state.selected_cat = i

# ================= 메인 화면 =================
cat = CATEGORIES[st.session_state.selected_cat]

st.markdown(f'<div class="cat-header">{cat["icon"]} {cat["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<span class="cat-time">▶ {cat["time_label"]} 부터 재생</span>', unsafe_allow_html=True)

# ---- Vimeo 임베드 (선택한 구간 시작 시점부터) ----
embed_url = f'https://player.vimeo.com/video/{VIMEO_VIDEO_ID}?h={VIMEO_HASH}#t={cat["start_seconds"]}s'
components.iframe(embed_url, height=420)

# ---- 핵심 요약 ----
summary_items = "".join(f"<li>{s}</li>" for s in cat["summary"])
st.markdown(
    f"""
    <div class="summary-box">
        <b>📝 이 구간 핵심 요약</b>
        <ul>{summary_items}</ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ================= 강의 내용 Q&A 챗봇 (스트리밍) =================
st.subheader("💬 강의 내용 물어보기")

openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    openai_api_key = st.text_input(
        "OpenAI API Key", type="password",
        help="secrets.toml에 키를 등록하면 이 입력창은 표시되지 않습니다.",
    )

if not openai_api_key:
    st.info("강의 내용에 대해 질문하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    all_summary_text = "\n\n".join(
        f'[{c["time_label"]} {c["title"]}]\n' + "\n".join(f"- {s}" for s in c["summary"])
        for c in CATEGORIES
    )
    SYSTEM_PROMPT = (
        "당신은 '260826_2기 인공지능 특급' 강의 영상 내용에 대해 답변하는 도우미입니다. "
        "아래는 강의를 구간별로 정리한 요약입니다. 이 정보를 바탕으로 사용자의 질문에 답하세요. "
        "요약에 없는 세부 내용은 추측하지 말고 모른다고 답하세요.\n\n"
        f"{all_summary_text}"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("예: Claude Code 설치는 어떻게 진행됐나요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        stream = client.chat.completions.create(
            model="gpt-4o-mini", messages=api_messages, stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
