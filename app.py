# app.py - UPDATED FOR RENDER.COM
import sys
import os

# ============================================================================
# ENVIRONMENT CONFIGURATIONS - MUST BE AT THE VERY TOP
# ============================================================================
print(f"🚀 Starting LearnSphere Backend")
print(f"🔍 Environment: {os.environ.get('RENDER', 'PYTHONANYWHERE' if 'PYTHONANYWHERE_DOMAIN' in os.environ else 'LOCAL')}")

# Set working directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

# ============================================================================
# NORMAL IMPORTS
# ============================================================================
import json
# Add this near the top of app.py
try:
    from pydantic import BaseModel
    PYDANTIC_V2 = True
except ImportError:
    # Fallback for pydantic v1
    from pydantic import BaseModel
    PYDANTIC_V2 = False
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from openai import OpenAI

from database import Base, engine, get_db
from models import (
    UserDB, User,
    AuthRequest, SettingsRequest, XPRequest, BonusRequest,
    DashboardRequest, LessonRequest, ChatRequest, TriviaRequest
)

# ============================================================================
# OPENROUTER CONFIGURATION - UPDATED FOR RENDER
# ============================================================================
def get_openrouter_key():
    """
    Load OpenRouter API key in order of priority:
    1. RENDER: Environment variable
    2. PythonAnywhere: Key file in home directory
    3. Local: .env file
    """
    
    # 1. Check for Render environment variable
    if 'RENDER' in os.environ:
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if api_key:
            print("✅ Loaded OpenRouter API key from Render environment variable")
            return api_key
    
    # 2. Check for PythonAnywhere
    elif 'PYTHONANYWHERE_DOMAIN' in os.environ:
        home_dir = os.path.expanduser('~')
        key_file_path = os.path.join(home_dir, '.learnsphere_openrouter_key.txt')
        
        print(f"🔍 Looking for API key at: {key_file_path}")
        
        if os.path.exists(key_file_path):
            try:
                with open(key_file_path, 'r') as f:
                    api_key = f.read().strip()
                if api_key:
                    print(f"✅ Loaded OpenRouter API key from {key_file_path}")
                    return api_key
            except Exception as e:
                print(f"⚠️ Error reading key file: {e}")
    
    # 3. Local development
    else:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                print("✅ Loaded OpenRouter API key from .env file")
                return api_key
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ Error loading from .env: {e}")
    
    # No key found
    print("⚠️ WARNING: No OpenRouter API key found")
    print("   AI features will use fallback data")
    return None

# Get the API key
OPENROUTER_API_KEY = get_openrouter_key()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "deepseek/deepseek-r1-0528"

# Initialize OpenRouter client if we have a key
client = None
if OPENROUTER_API_KEY:
    try:
        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        print("✅ OpenRouter client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OpenRouter client: {e}")
        client = None
else:
    print("⚠️ OpenRouter client NOT initialized - AI features will use fallback")

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# KEEP ALL YOUR EXISTING CODE BELOW - NO CHANGES NEEDED
# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_enhanced_fallback_lesson(topic, language):
    """Return an engaging fallback lesson with rich formatting"""
    
    if language.lower() == "arabic":
        return {
            "lesson": f"""# 🎯 {topic}: دليل شامل للدراسة الذاتية

## 📖 المقدمة
مرحبًا بك في رحلة التعلم الذاتي حول **{topic}**! هذا الدرس مصمم ليكون تفاعليًا وسهل المتابعة.

## 🎓 المفاهيم الأساسية

### 🔍 الفكرة الرئيسية الأولى
- **الشرح**: فهم الأساسيات والمبادئ الرئيسية
- **المثال**: تطبيق عملي يوضح المفهوم
- **💡 نصيحة احترافية**: خذ وقتك في فهم الأساسيات قبل التقدم

### 🔍 الفكرة الرئيسية الثانية  
- **الشرح**: كيفية تطبيق هذه المعرفة
- **المثال**: سيناريو من الحياة الواقعية
- **💡 نصيحة احترافية**: تدرب بانتظام لترسيخ المعرفة

## 🛠️ التطبيق العملي

### 🎯 جربها بنفسك
**التمرين**: فكر في كيفية تطبيق {topic} في حياتك اليومية واكتب ثلاثة أمثلة.

### 🌍 مثال من الواقع
كيف يستخدم المحترفون {topic} في مجال العمل؟

## 📊 مرجع سريع
| المفهوم | التعريف | المثال |
|---------|----------|--------|
| الأساسيات | المبادئ الرئيسية | [أمثلة] |
| التطبيق | كيفية الاستخدام | [أمثلة] |

## 🤔 فحص المعرفة

### ❓ أسئلة التفكير
1. ما هو الجانب الأكثر إثارة للاهتمام في {topic}؟
2. كيف يمكنك تطبيق هذا في مشاريعك المستقبلية؟

### 🎯 التقييم الذاتي
- [ ] أفهم المفاهيم الأساسية
- [ ] أستطيع شرحها لشخص آخر
- [ ] أستطيع تطبيقها عمليًا

## 🚀 الخطوات التالية
- ابحث عن مشاريع عملية لتطبيق ما تعلمته
- انضم إلى مجتمعات التعلم ذات الصلة
- واصل التعلم من خلال الموارد الإضافية

*✨ استمر في رحلة التعلم الرائعة!*"""
        }
    else:
        return {
            "lesson": f"""# 🎯 {topic}: Comprehensive Self-Study Guide

## 📖 Introduction  
Welcome to your interactive learning journey about **{topic}**! This lesson is designed to be engaging and practical.

## 🎓 Key Concepts

### 🔍 Core Concept 1
- **Explanation**: Understanding the fundamental principles
- **Example**: Practical application scenario
- **💡 Pro Tip**: Master the basics before advancing

### 🔍 Core Concept 2
- **Explanation**: How to apply this knowledge  
- **Example**: Real-world use case
- **💡 Pro Tip**: Practice regularly to reinforce learning

## 🛠️ Practical Application

### 🎯 Try It Yourself
**Exercise**: Think about how you can apply {topic} in your daily life and write down three examples.

### 🌍 Real-World Connection
How do professionals use {topic} in their work?

## 📊 Quick Reference
| Concept | Definition | Example |
|---------|------------|---------|
| Fundamentals | Core principles | [Examples] |
| Application | Practical usage | [Examples] |

## 🤔 Knowledge Check

### ❓ Reflection Questions
1. What's the most interesting aspect of {topic}?
2. How can you apply this to your future projects?

### 🎯 Self-Assessment
- [ ] I understand the basic concepts
- [ ] I can explain it to someone else
- [ ] I can apply it in practice

## 🚀 Next Steps
- Find practical projects to apply your knowledge
- Join relevant learning communities  
- Continue learning with additional resources

*✨ Keep up the amazing learning journey!*"""
        }

def get_fallback_trivia(language):
    """Return fallback trivia questions in the specified language"""
    if language.lower() == "arabic":
        return {
            "quiz": [
                {
                    "q": "ما هي عاصمة فرنسا؟",
                    "options": ["لندن", "برلين", "باريس", "مدريد"],
                    "answer": "باريس"
                },
                {
                    "q": "كم عدد الكواكب في نظامنا الشمسي؟",
                    "options": ["7", "8", "9", "10"],
                    "answer": "8"
                },
                {
                    "q": "ما هو أكبر حيوان ثديي في العالم؟",
                    "options": ["الفيل", "الحوت الأزرق", "الزرافة", "الدب القطبي"],
                    "answer": "الحوت الأزرق"
                },
                {
                    "q": "في أي سنة انتهت الحرب العالمية الثانية؟",
                    "options": ["1944", "1945", "1946", "1947"],
                    "answer": "1945"
                },
                {
                    "q": "من رسم لوحة الموناليزا؟",
                    "options": ["فان جوخ", "بيكاسو", "ليوناردو دافنشي", "مونيه"],
                    "answer": "ليوناردو دافنشي"
                }
            ]
        }
    else:
        return {
            "quiz": [
                {
                    "q": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "answer": "Paris"
                },
                {
                    "q": "How many planets are in our solar system?",
                    "options": ["7", "8", "9", "10"],
                    "answer": "8"
                },
                {
                    "q": "What is the largest mammal?",
                    "options": ["Elephant", "Blue Whale", "Giraffe", "Polar Bear"],
                    "answer": "Blue Whale"
                },
                {
                    "q": "What year did World War II end?",
                    "options": ["1944", "1945", "1946", "1947"],
                    "answer": "1945"
                },
                {
                    "q": "Who painted the Mona Lisa?",
                    "options": ["Van Gogh", "Picasso", "Da Vinci", "Monet"],
                    "answer": "Da Vinci"
                }
            ]
        }

def serialize_user(db_user: UserDB):
    return {
        "id": db_user.id,
        "username": db_user.username,
        "avatar": db_user.avatar,
        "total_xp": db_user.total_xp,
        "level": db_user.level,
        "rank": db_user.rank,
        "topics_completed": db_user.topics_completed,
        "completed_topics_in_rank": db_user.get_completed_topics(),
        "school": db_user.school,
        "description": db_user.description,
    }

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://learn-sphere-adventures.vercel.app",
        # Remove "*" for production - only for testing
        # "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTH ROUTES
# ============================================================================
@app.post("/api/auth/signup")
def signup(data: AuthRequest, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = UserDB(
        username=data.username,
        password=data.password,
        avatar="default_url",
        total_xp=0,
        level=1,
        rank="Beginner",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user": serialize_user(new_user), "message": "Success"}


@app.post("/api/auth/signin")
def signin(data: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"user": serialize_user(user), "message": "Success"}

# ============================================================================
# USER DASHBOARD
# ============================================================================
@app.post("/api/user/dashboard")
def dashboard(data: DashboardRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": serialize_user(user)}

# ============================================================================
# USER SETTINGS
# ============================================================================
@app.post("/api/user/settings")
def update_settings(data: SettingsRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.avatar:
        user.avatar = data.avatar
    if data.school:
        user.school = data.school
    if data.description:
        user.description = data.description
    if data.newPassword:
        user.password = data.newPassword

    db.commit()
    return {"user": serialize_user(user), "message": "Updated"}

# ============================================================================
# GAME LOGIC: XP
# ============================================================================
RANKS = ["Beginner", "Rare", "Epic", "Mythic", "Legendary"]

@app.post("/api/user/xp")
def update_xp(data: XPRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Increase XP
    user.total_xp += data.score

    # Track topics
    completed = user.get_completed_topics()
    if data.topic not in completed:
        completed.append(data.topic)
    user.set_completed_topics(completed)
    user.topics_completed = len(completed)

    # Rank Promotion
    if len(completed) >= 10:
        current_index = RANKS.index(user.rank)
        if current_index < len(RANKS) - 1:
            user.rank = RANKS[current_index + 1]
            user.set_completed_topics([])
            user.topics_completed = 0

    # Level logic
    user.level = min(3, 1 + user.total_xp // 300)

    db.commit()

    return {
        "message": "XP Updated",
        "new_xp": user.total_xp,
        "new_level": user.level,
        "rank": user.rank
    }

# ============================================================================
# BONUS XP
# ============================================================================
@app.post("/api/bonus")
def bonus(data: BonusRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.total_xp += data.score
    db.commit()

    return {
        "message": "Bonus Applied",
        "new_xp": user.total_xp
    }

# ============================================================================
# AI — ASSISTED LESSON (OpenRouter)
# ============================================================================
@app.post("/api/lesson/assisted")
def assisted_lesson(data: LessonRequest):
    try:
        print(f"🔍 DEBUG: Received lesson request - topic: {data.topic}, rank: {data.rank}")
        
        # Check if OpenRouter client is available
        if not client:
            print("❌ ERROR: OpenRouter client is not initialized")
            raise HTTPException(status_code=500, detail="AI service not available")
        
        prompt = f"""You are an educational AI tutor. Create a short lesson about '{data.topic}' for a {data.rank} level student.

LESSON REQUIREMENTS:
- Create a brief, engaging lesson (2-3 paragraphs)
- Include exactly 3 multiple-choice questions about the lesson
- Difficulty level: {data.level}
- Language: {data.language}

RESPONSE FORMAT - RETURN ONLY VALID JSON, NO OTHER TEXT:
{{
  "lesson": "Lesson content here...",
  "quiz": [
    {{
      "q": "Question 1?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }},
    {{
      "q": "Question 2?", 
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option B"
    }},
    {{
      "q": "Question 3?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option C"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanations."""

        print("🔄 DEBUG: Sending request to OpenRouter API...")
        
        # OpenRouter API call
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an educational AI tutor that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  # Request JSON response
        )
        
        print(f"✅ DEBUG: OpenRouter response received")
        
        # Get the response text
        response_text = response.choices[0].message.content
        
        print(f"📝 DEBUG: Response text: {response_text}")
        
        # Clean the response
        cleaned_text = response_text.strip()
        
        # Try to parse the response
        try:
            result = json.loads(cleaned_text)
            print("✅ DEBUG: JSON parsed successfully")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ DEBUG: JSON parse error: {e}")
            # Return fallback data
            return {
                "lesson": f"This is a fallback lesson about {data.topic}.",
                "quiz": [
                    {
                        "q": f"What is {data.topic}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": "Option A"
                    },
                    {
                        "q": f"Why learn {data.topic}?",
                        "options": ["Reason 1", "Reason 2", "Reason 3", "All"],
                        "answer": "All"
                    },
                    {
                        "q": f"Where is {data.topic} used?",
                        "options": ["Everywhere", "Nowhere", "Somewhere", "Anywhere"],
                        "answer": "Everywhere"
                    }
                ]
            }
            
    except Exception as e:
        print(f"❌ DEBUG: Exception in assisted_lesson: {str(e)}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# ============================================================================
# AI — SELF-STUDY LESSON (OpenRouter)
# ============================================================================
@app.post("/api/lesson/self")
def self_lesson(data: LessonRequest):
    try:
        print(f"🔍 DEBUG: Received self-learning request - topic: {data.topic}")
        
        if not client:
            print("❌ ERROR: OpenRouter client is not initialized")
            return get_enhanced_fallback_lesson(data.topic, data.language)
        
        prompt = f"""
Create an engaging, interactive self-study lesson about '{data.topic}' in {data.language}.

STUDENT PROFILE:
- Level: {data.rank}
- Difficulty: {data.level}
- Language: {data.language}

LESSON REQUIREMENTS:
1. Use RICH MARKDOWN formatting with headers, bullet points, tables, and emphasis
2. Include interactive elements like "Try It Yourself" sections
3. Add practical examples and real-world applications
4. Include knowledge checks and reflection questions
5. Make it visually appealing and easy to follow

FORMAT USING THIS MARKDOWN STRUCTURE:
# 🎯 {data.topic}: Comprehensive Guide

## 📖 Introduction
[Engaging introduction with emojis]

## 🎓 Key Concepts
### 🔍 Main Idea 1
- **Explanation**: [Clear description]
- **Example**: [Practical example]
- **💡 Pro Tip**: [Helpful hint]

### 🔍 Main Idea 2  
- **Explanation**: [Clear description]
- **Example**: [Practical example]
- **💡 Pro Tip**: [Helpful hint]

## 🛠️ Practical Application
### 🎯 Try It Yourself
[Interactive exercise or thought experiment]

### 🌍 Real-World Example
[How this is used in real life]

## 📊 Quick Reference
| Concept | Definition | Example |
|---------|------------|---------|
[Table with key concepts]

## 🤔 Knowledge Check
### ❓ Reflection Questions
1. [Thought-provoking question 1]
2. [Thought-provoking question 2]

### 🎯 Self-Assessment
- [ ] I understand the basic concepts
- [ ] I can explain it to someone else  
- [ ] I can apply it in practice

## 🚀 Next Steps
[Suggestions for further learning]

Make the lesson engaging, use emojis appropriately, and include interactive elements throughout.
"""

        print("🔄 DEBUG: Sending self-learning request to OpenRouter API...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an educational AI tutor that creates engaging lessons."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        
        lesson_content = response.choices[0].message.content
        return {"lesson": lesson_content}
            
    except Exception as e:
        print(f"❌ DEBUG: Exception in self_lesson: {str(e)}")
        return get_enhanced_fallback_lesson(data.topic, data.language)

# ============================================================================
# AI — CHAT TUTOR (OpenRouter)
# ============================================================================
@app.post("/api/chat")
def chat(data: ChatRequest):
    try:
        print("🔍 DEBUG: Received chat request")
        
        if not client:
            return {"reply": "AI service is currently unavailable. Please try again later."}
        
        last_msg = data.messages[-1].content if data.messages and len(data.messages) > 0 else "Hello"

        prompt = f"""
You are a friendly and helpful tutor. Use this lesson for context:
{data.lessonContent if data.lessonContent else "No specific lesson context provided."}

Student's message: "{last_msg}"
Language: {data.language}

Provide a helpful, educational response. Keep it clear and engaging.
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a friendly educational tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        return {"reply": response.choices[0].message.content}
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in chat: {str(e)}")
        return {"reply": "I'm having trouble responding right now. Please try asking your question again in a moment."}

# ============================================================================
# AI — TRIVIA (OpenRouter)
# ============================================================================
@app.post("/api/trivia")
def trivia(data: TriviaRequest):
    try:
        print(f"🔍 DEBUG: Received trivia request - language: {data.language}")
        
        if not client:
            return get_fallback_trivia(data.language)
        
        if data.language.lower() == "arabic":
            prompt = """أنشئ 5 أسئلة trivial ممتعة وتعليمية.

أعد JSON فقط:
{{
  "quiz": [
    {{
      "q": "السؤال 1؟",
      "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
      "answer": "الخيار أ"
    }}
    // 4 أسئلة أخرى
  ]
}}"""
        else:
            prompt = f"""Generate 5 trivia questions in {data.language}.

Return ONLY JSON:
{{
  "quiz": [
    {{
      "q": "Question 1?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }}
    // 4 more questions
  ]
}}"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        result = json.loads(response_text)
        return result
            
    except Exception as e:
        print(f"❌ DEBUG: Exception in trivia: {str(e)}")
        return get_fallback_trivia(data.language)

# ============================================================================
# ABOUT INFORMATION
# ============================================================================
class TeamMember(BaseModel):
    name: str
    role: str
    photo: str

class AboutRequest(BaseModel):
    language: str

class AboutResponse(BaseModel):
    school_description: str
    team: List[TeamMember]

@app.post("/api/about", response_model=AboutResponse)
def get_about_info(data: AboutRequest):
    # Team data with Multiavatar URLs - exactly matching your frontend fallback
    team_data = [
        {"name": "Mr. Bassem Bin Salah", "role": "Super Teacher 🎓", "photo": "https://api.multiavatar.com/Teacher.svg"},
        {"name": "Alex", "role": "Code Wizard 💻", "photo": "https://api.multiavatar.com/Alex.svg"},
        {"name": "Sarah", "role": "Design Artist 🎨", "photo": "https://api.multiavatar.com/Sarah.svg"},
        {"name": "Omar", "role": "Bug Hunter 🐞", "photo": "https://api.multiavatar.com/Omar.svg"},
        {"name": "Lina", "role": "Storyteller 📚", "photo": "https://api.multiavatar.com/Lina.svg"}
    ]
    
    # Language-specific descriptions
    if data.language == "ar":
        description = "مدرستنا مخصصة لجعل التعلم تجربة سحرية من خلال منصة تعليمية مدعومة بالذكاء الاصطناعي. نحن نؤمن بقوة التعليم التفاعلي والتكنولوجيا في تحفيز العقول الشابة."
    else:
        description = "Our school is dedicated to making learning a magical experience through AI-powered education. We believe in the power of interactive learning and technology to inspire young minds."
    
    return AboutResponse(
        school_description=description,
        team=team_data
    )

# ============================================================================
# SYSTEM TEST
# ============================================================================
@app.get("/api/test")
def test():
    return {"message": "pong", "status": "healthy", "ai_provider": "OpenRouter"}

@app.get("/")
def root():
    return {
        "message": "LearnSphere Backend API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/api/test - Health check",
            "/api/auth/signup - User registration",
            "/api/auth/signin - User login",
            "/api/lesson/assisted - AI-assisted lessons",
            "/api/lesson/self - Self-study lessons",
            "/api/chat - AI chat tutor",
            "/api/trivia - Fun trivia"
        ]
    }

# ============================================================================
# PYTHONANYWHERE WSGI COMPATIBILITY
# ============================================================================

application = app








