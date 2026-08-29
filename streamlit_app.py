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
        padding: 10px 14px;
        margin-bottom: 6px;
        width: 100%;
        display: flex;
        justify-content: flex-start !important;
        text-align: left !important;
    }
    section[data-testid="stSidebar"] .stButton button p {
        text-align: left !important;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Vimeo 영상 정보 ----
VIMEO_VIDEO_ID = "1221651006"
VIMEO_HASH = "ecf1d87214"

# ---- 카테고리 데이터 (영상 흐름 순서대로) ----
# start_seconds: 해당 구간이 시작되는 영상 내 시점
# summary: 마크다운 형식 (코드블록 포함 가능)
CATEGORIES = [
    {
        "icon": "🗂️", "title": "수업 운영 안내", "start_seconds": 0,
        "time_label": "00:00:00",
        "summary": """
강사는 수업 시작과 함께 화면과 음성이 정상적으로 전달되는지부터 확인하고, **Discord를 이번 과정의 공식 소통 채널**로 지정합니다.

- 이해도 체크 규칙: 강사가 안내 사항을 올리면 수강생은 이해했으면 **O**, 애매하면 **물음표(?)**, 잘 모르겠으면 **X**로 반응을 남기는 방식으로 진행됩니다.
- 아직 Discord에 가입하지 않았거나 체크를 완료하지 않은 수강생이 절반 가까이 되어, 1교시 안에는 반드시 가입과 체크를 마쳐달라고 여러 차례 강조합니다.
- 설치나 세팅이 어려운 수강생을 위해 1교시가 끝난 뒤 약 20~30분간 원격으로 개별 지원을 하겠다고 안내합니다.
""",
    },
    {
        "icon": "📚", "title": "커리큘럼 소개", "start_seconds": 309,
        "time_label": "00:05:09",
        "summary": """
이번 과정은 총 **160시간**으로 구성되며, 사전에 공유된 커리큘럼은 확정본이 아니라 초안이라는 점을 분명히 합니다.

- 실제 진도는 수강생들의 이해 속도에 맞춰 유동적으로 조절될 예정이며, 진도가 빠르면 추가 주제를 더 다룰 수 있다고 언급합니다.
- 학습 순서는 기본 개념(터미널 사용, 파일 구조 등)을 먼저 다진 뒤, 여기에 AI 기능을 점진적으로 얹어가는 방식으로 설계되어 있습니다.
- 왕초보 수강생들을 배려해 사전에 Claude Code로 직접 제작한 학습 자료를 준비했다고 소개하며, 오리엔테이션 동안 관련 체크리스트를 함께 완료해나갈 것을 권장합니다.
""",
    },
    {
        "icon": "🛠️", "title": "필요 도구 준비", "start_seconds": 511,
        "time_label": "00:08:31",
        "summary": """
수업에 필요한 계정과 도구를 미리 준비하도록 안내하는 구간입니다.

- **AI 서비스**: ChatGPT, Claude, Gemini는 필수로 계정을 만들어 두어야 하며, 이미 쓰고 있다면 넘어가도 됩니다. Qwen 등 중국계 AI 서비스는 개인정보가 해당국 정부 통제 하에 놓일 수 있다는 우려 때문에 필수가 아닌 **선택사항**으로 소개됩니다.
- **개발·협업 도구**: GitHub와 Notion 계정 가입이 필수로 요구됩니다. Notion은 이번 과정에서 처음 사용해보는 수강생들도 있어, 기본 사용법까지 함께 다룰 예정이라고 안내합니다.
- 강사는 한 가지 AI 서비스만 고집하지 말고 상황에 따라 비교해가며 사용해볼 것을 권장하며, 본인도 Claude Code와 Claude, 가끔 Gemini까지 병행해서 쓴다고 언급합니다.
""",
    },
    {
        "icon": "🙋", "title": "자기소개 & 팀 빌딩", "start_seconds": 3693,
        "time_label": "01:01:33",
        "summary": """
수강생들이 관심 있는 서비스·앱 분야, 만들어보고 싶은 프로덕트, 좋아하는 음식 등을 자유로운 형식으로 자기소개하는 시간입니다.

- 이 시간의 목적은 단순 친목이 아니라, **추후 진행될 팀 프로젝트 매칭을 위한 사전 파악**입니다.
- 강사는 처음에는 관심사가 겹치는 수강생들을 어느 정도 묶어주겠지만, 이후 팀 프로젝트에서는 누군가 아이디어를 제안하면 다른 수강생들이 지원하는 방식으로 팀이 구성된다고 설명합니다.
- 전체 160시간 과정 동안 처음에는 각자 혼자 힘으로 프로덕트를 완성해보는 경험을 먼저 쌓고, 이후 단계에서 팀워크를 통해 사용자 테스트나 리서치처럼 혼자서는 하기 어려운 작업을 함께 해보는 흐름으로 진행됩니다.
""",
    },
    {
        "icon": "💻", "title": "터미널 · VS Code 설치", "start_seconds": 8141,
        "time_label": "02:15:41",
        "summary": """
개발 환경의 기초가 되는 터미널과 VS Code를 설치하는 구간입니다.

- 터미널을 사용하는 이유와 장점(가벼움, 여러 작업을 동시에 다루기 쉬움 등)을 설명하며, 수강생들과 함께 터미널을 처음 실행해봅니다.
- 이어서 VS Code 설치를 진행하며, 설치 과정에서 함께 따라오는 여러 확장 프로그램들에 대해서도 간단히 언급합니다.
- 설치 중간에 막히는 수강생들이 나오자, 강사는 어려움을 겪는 경우 개인적으로 도와주겠다고 안내하며 진도를 조절합니다.
""",
    },
    {
        "icon": "🤖", "title": "Claude Code 설치 & 실습", "start_seconds": 10709,
        "time_label": "02:58:29",
        "summary": """
Node.js와 Claude Code를 설치하고, 첫 실습(간단한 웹페이지 만들기)까지 진행하는 구간입니다. Windows와 Mac 환경을 번갈아 시연하며, 최근에는 Node.js 없이 Claude Code만 단독 설치하는 방법도 생겼다는 점을 언급합니다.

첨부해주신 Windows 설치 가이드 기준으로 핵심을 정리하면 다음과 같습니다.

**왜 Node.js가 필요한가**
Claude Code는 원래 npm(자바스크립트 패키지 관리자)을 통해 배포되던 도구라, npm으로 설치하려면 Node.js가 필요합니다. 다만 최근에는 Node.js 없이 실행 파일만 받아 바로 쓰는 **네이티브 설치** 방식도 공식 지원됩니다. 두 방식 모두 결국 실행되는 건 동일한 실행 파일(binary)이며, npm은 그것을 받아오는 방법 중 하나일 뿐입니다.

**1) Node.js 설치 (Windows, PowerShell)**
```powershell
winget install OpenJS.NodeJS.LTS
```
설치 후 PowerShell을 재시작해야 PATH가 반영됩니다. 아래 명령으로 설치를 확인합니다.
```powershell
node --version
npm --version
```
최신 Claude Code는 Node.js 22 이상을 요구합니다.

**2) PowerShell 실행 정책 오류 대처**
`npm --version` 실행 시 Windows 기본 실행 정책(Restricted)으로 스크립트 실행이 막히는 경우가 있습니다. 아래 명령으로 현재 계정 범위에서만 정책을 완화해 해결할 수 있습니다 (관리자 권한 불필요).
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
적용 후 터미널을 재시작해야 반영됩니다.

**3) Claude Code 설치**
- npm 방식: `npm install -g @anthropic-ai/claude-code`
- 네이티브 방식(권장): `irm https://claude.ai/install.ps1 | iex`

설치 후 `claude --version`으로 확인하고, 프로젝트 폴더에서 `claude` 명령으로 실행 및 인증을 진행합니다.

**실습**: 설치를 마친 수강생들은 실제로 간단한 웹페이지(예: 벽돌깨기 게임)를 Claude Code로 직접 만들어보는 시간을 갖습니다.
""",
    },
    {
        "icon": "🏁", "title": "실습 결과 & 마무리", "start_seconds": 16724,
        "time_label": "04:38:44",
        "summary": """
실습 결과를 함께 확인하고 수업을 마무리하는 구간입니다.

- index.html이 무엇인지 몰라 결과물이 실행되지 않는 등, 기초 개념 부족으로 어려움을 겪는 수강생들을 강사가 화면 공유를 통해 개별적으로 도와줍니다.
- 강사는 "AI에게 막연한 명령을 그대로 입력하는 것이 아니라, 원하는 결과를 구체적으로 설명할 수 있어야 방향을 잘 잡아줄 수 있다"는 **프롬프트 엔지니어링의 중요성**을 반복해서 강조합니다. 기본 지식이 없으면 AI가 일반적인 결과물만 만들어주는 데 그친다고 설명합니다.
- 배포(Vercel 등과 연결해 지속적인 URL 만들기)는 다음 단계 과제로 남기고, 이번 시간에는 로컬 설치와 첫 실습 완료 여부를 확인하며 수업을 마무리합니다.
- 앞으로 3개월(160시간) 동안 개인 프로젝트 → 팀 프로젝트 순으로 실전 경험을 쌓아갈 예정임을 다시 한 번 안내합니다.
""",
    },
]

# ---- 세션 상태 초기화 ----
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 사이드바: 카테고리 목록 (왼쪽 정렬, 시간 표시 없음) =================
with st.sidebar:
    st.markdown("## 🎬 강의 목차")
    st.caption("260826_2기 인공지능 특급")
    st.write("")
    for i, cat in enumerate(CATEGORIES):
        label = f'{cat["icon"]}  {cat["title"]}'
        if st.button(label, key=f"cat_{i}", use_container_width=True):
            st.session_state.selected_cat = i

# ================= 메인 화면 =================
cat = CATEGORIES[st.session_state.selected_cat]

st.markdown(f'<div class="cat-header">{cat["icon"]} {cat["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<span class="cat-time">▶ {cat["time_label"]} 부터 자동 재생</span>', unsafe_allow_html=True)

# ---- Vimeo 임베드 (선택한 구간 시작 시점부터 자동재생) ----
# 자동재생은 브라우저 정책상 음소거(muted) 상태에서만 안정적으로 동작합니다.
embed_url = (
    f'https://player.vimeo.com/video/{VIMEO_VIDEO_ID}?h={VIMEO_HASH}'
    f'&autoplay=1&muted=1#t={cat["start_seconds"]}s'
)
components.iframe(embed_url, height=420)
st.caption("🔇 자동재생은 브라우저 정책상 음소거로 시작됩니다. 플레이어의 음소거 버튼을 눌러 소리를 켜주세요.")

# ---- 핵심 요약 ----
with st.container(border=True):
    st.markdown("**📝 이 구간 핵심 요약**")
    st.markdown(cat["summary"])

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
        f'[{c["time_label"]} {c["title"]}]\n{c["summary"]}' for c in CATEGORIES
    )
    SYSTEM_PROMPT = (
        "당신은 '260826_2기 인공지능 특급' 강의 영상 내용에 대해 답변하는 도우미입니다. "
        "아래는 강의를 구간별로 정리한 상세 요약입니다. 이 정보를 바탕으로 사용자의 질문에 답하세요. "
        "설치 명령어를 물어보면 요약에 포함된 코드를 정확히 안내하세요. "
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
