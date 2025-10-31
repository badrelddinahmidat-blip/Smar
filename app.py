"""
Smart Library Web Application
A Flask-based web app for managing and reading digital books with AI-powered search.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort, session, jsonify, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from functools import wraps
import json
try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    Image = None  # type: ignore
    PIL_AVAILABLE = False
try:
    import imghdr  # type: ignore
except Exception:
    imghdr = None  # type: ignore
# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Language support
LANGUAGES = {
    'ar': {
        'name': 'العربية',
        'dir': 'rtl',
        'code': 'ar'
    },
    'en': {
        'name': 'English',
        'dir': 'ltr',
        'code': 'en'
    }
}

# Default language is Arabic
DEFAULT_LANGUAGE = 'ar'

def get_current_language():
    """Get the current language from session or return default."""
    return session.get('language', DEFAULT_LANGUAGE)

def get_language_data():
    """Get language-specific data."""
    current_lang = get_current_language()
    return LANGUAGES[current_lang]

def get_translations():
    """Get translations for the current language."""
    current_lang = get_current_language()
    
    translations = {
        'ar': {
            'app_name': 'المكتبة الذكية',
            'home': 'الرئيسية',
            'add_book': 'إضافة كتاب',
            'ai_search': 'البحث الذكي',
            'login': 'تسجيل الدخول',
            'logout': 'تسجيل الخروج',
            'search_placeholder': 'البحث في الكتب...',
            'welcome_back': 'مرحباً بعودتك،',
            'welcome_to_library': 'مرحباً بك في المكتبة الذكية',
            'discover_books': 'اكتشف وأدر مجموعة الكتب الرقمية الخاصة بك. تصفح، ابحث، وحمل الكتب بصيغة PDF.',
            'add_new_book': 'إضافة كتاب جديد',
            'available_books': 'الكتب المتاحة',
            'no_books_available': 'لا توجد كتب متاحة',
            'start_building': 'ابدأ في بناء مكتبتك الذكية! أضف كتابك الأول للبدء.',
            'add_first_book': 'أضف كتابك الأول',
            'view_details': 'عرض التفاصيل',
            'download': 'تحميل',
            'added_on': 'أضيف في',
            'no_description': 'لا يوجد وصف متاح',
            'book_title': 'عنوان الكتاب',
            'author': 'المؤلف',
            'description': 'الوصف',
            'pdf_file': 'ملف PDF',
            'cancel': 'إلغاء',
            'save': 'حفظ',
            'enter_library': 'دخول المكتبة',
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'email': 'البريد الإلكتروني',
            'enter_first_name': 'أدخل اسمك الأول',
            'enter_last_name': 'أدخل اسم العائلة',
            'enter_email': 'أدخل بريدك الإلكتروني',
            'your_given_name': 'اسمك الشخصي',
            'your_family_name': 'اسم عائلتك',
            'we_never_share': 'لن نشارك بريدك الإلكتروني مع أي شخص آخر',
            'no_password_required': 'لا حاجة لكلمة مرور - فقط أدخل اسمك للبدء!',
            'what_you_can_do': 'ما يمكنك فعله',
            'browse_books': 'تصفح الكتب الرقمية',
            'search_books': 'البحث بالعنوان أو المؤلف',
            'download_books': 'تحميل كتب PDF',
            'add_books': 'إضافة كتب جديدة للمكتبة',
            'view_details_books': 'عرض تفاصيل الكتب',
            'personalized_experience': 'تجربة شخصية',
            'upload_guidelines': 'إرشادات الرفع',
            'only_pdf_accepted': 'يتم قبول ملفات PDF فقط',
            'max_file_size': 'الحد الأقصى لحجم الملف: 16 ميجابايت',
            'make_sure_readable': 'تأكد من أن ملف PDF قابل للقراءة وغير تالف',
            'provide_accurate_info': 'قدم معلومات دقيقة للعنوان والمؤلف',
            'ai_powered_search': 'البحث الذكي',
            'ask_ai_assistant': 'اسأل مساعدنا الذكي',
            'your_question': 'سؤالك أو استعلام البحث',
            'ask_anything': 'اسأل أي شيء عن الكتب، الأدب، أو احصل على توصيات قراءة شخصية!',
            'ask_placeholder': 'اسأل أي شيء عن الكتب، الأدب، أو احصل على توصيات قراءة شخصية...',
            'examples': 'أمثلة: "أوصي برواية غموض جيدة"، "ما هو موضوع روميو وجولييت؟"، "ابحث عن كتب استكشاف الفضاء"',
            'clear': 'مسح',
            'search_with_ai': 'البحث بالذكاء الاصطناعي',
            'ai_response': 'استجابة الذكاء الاصطناعي',
            'powered_by_openai': 'مدعوم من OpenAI ChatGPT',
            'copy_response': 'نسخ الاستجابة',
            'ai_thinking': 'الذكاء الاصطناعي يفكر...',
            'please_wait': 'يرجى الانتظار بينما يعالج مساعدنا الذكي استفسارك.',
            'quick_questions': 'الأسئلة السريعة',
            'book_recommendations': 'توصيات الكتب',
            'mystery_novels': 'روايات الغموض',
            'classic_literature': 'الأدب الكلاسيكي',
            'science_fiction': 'الخيال العلمي',
            'general_questions': 'الأسئلة العامة',
            'fiction_vs_nonfiction': 'الخيال مقابل الواقع',
            'reading_tips': 'نصائح القراءة',
            'benefits_reading': 'فوائد القراءة',
            'welcome_to_smart_library': 'مرحباً بك في المكتبة الذكية',
            'please_enter_name': 'يرجى إدخال اسمك للمتابعة',
            'book_added_successfully': 'تم إضافة الكتاب بنجاح!',
            'book_deleted_successfully': 'تم حذف الكتاب بنجاح!',
            'goodbye': 'وداعاً،',
            'you_have_been_logged_out': 'تم تسجيل خروجك.',
            'you_were_not_logged_in': 'لم تكن مسجلاً دخولاً.',
            'please_log_in': 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة',
            'no_file_selected': 'لم يتم اختيار ملف',
            'invalid_file_type': 'نوع ملف غير صالح. يُسمح فقط بملفات PDF.',
            'file_not_found': 'الملف غير موجود',
            'please_enter_search_query': 'يرجى إدخال استعلام البحث',
            'error_getting_ai_response': 'خطأ في الحصول على استجابة الذكاء الاصطناعي',
            'error_deleting_file': 'خطأ في حذف الملف',
            'book_deleted_from_database': 'تم حذف الكتاب من قاعدة البيانات، لكن الملف غير موجود.',
            'built_with_flask': 'تم البناء باستخدام Flask و Bootstrap.',
            'language': 'اللغة',
            'switch_to_english': 'التبديل إلى الإنجليزية',
            'switch_to_arabic': 'التبديل إلى العربية',
            'book_information': 'معلومات الكتاب',
            'quick_actions': 'الإجراءات السريعة',
            'view_all_books': 'عرض جميع الكتب',
            'delete': 'حذف',
            'search_results': 'نتائج البحث',
            'search_query': 'استعلام البحث',
            'found': 'تم العثور على',
            'book': 'كتاب',
            'no_books_found': 'لم يتم العثور على كتب',
            'no_books_found_message': 'لم يتم العثور على كتب تطابق',
            'try_different_search': 'جرب مصطلح بحث مختلف أو تصفح جميع الكتب.',
            'browse_all_books': 'تصفح جميع الكتب',
            'back_to_all_books': 'العودة إلى جميع الكتب',
            'search_again': 'البحث مرة أخرى',
            'search': 'بحث',
            'books': 'الكتب',
            'articles': 'المقالات',
            'digital_repositories': 'المستودعات الرقمية',
            'open_access_websites': 'مواقع الوصول الحر',
            'generate_abstract': 'إنشاء مستخلص',
            'abstract': 'المستخلص',
            'generating_abstract': 'جاري إنشاء المستخلص...',
            'abstract_generated': 'تم إنشاء المستخلص',
            'error_generating_abstract': 'خطأ في إنشاء المستخلص',
            'recently_added_books': 'الكتب المضافة حديثًا',
            'all_books': 'كل الكتب',
            'search_books_placeholder': 'ابحث في الكتب...',
            'sail_through_library': 'ابحر في مكتبتك الذكية',
            'generate_annotation': 'التهميش',
            'annotation': 'التهميش',
            'generating_annotation': 'جاري إنشاء التهميش...',
            'annotation_generated': 'تم إنشاء التهميش',
            'error_generating_annotation': 'خطأ في إنشاء التهميش',
            'book_cover_image': 'صورة غلاف الكتاب',
            'image_guideline': 'الصورة اختيارية (PNG/JPG/GIF/WEBP) بحجم أقصى 5 ميجابايت',
            'image_too_large': 'الصورة كبيرة جدًا. الحد الأقصى 5 ميجابايت',
            'invalid_image_file': 'ملف الصورة غير صالح',
            'invalid_image_type': 'نوع الصورة غير صالح. المسموح: PNG, JPG, GIF, WEBP',
            'image_required': 'صورة الغلاف مطلوبة لكل كتاب'
        },
        'en': {
            'app_name': 'Smart Library',
            'home': 'Home',
            'add_book': 'Add Book',
            'ai_search': 'AI Search',
            'login': 'Login',
            'logout': 'Logout',
            'search_placeholder': 'Search books...',
            'welcome_back': 'Welcome back,',
            'welcome_to_library': 'Welcome to Smart Library',
            'discover_books': 'Discover and manage your digital book collection. Browse, search, and download books in PDF format.',
            'add_new_book': 'Add New Book',
            'available_books': 'Available Books',
            'no_books_available': 'No Books Available',
            'start_building': 'Start building your smart library! Add your first book to get started.',
            'add_first_book': 'Add Your First Book',
            'view_details': 'View Details',
            'download': 'Download',
            'added_on': 'Added:',
            'no_description': 'No description available',
            'book_title': 'Book Title',
            'author': 'Author',
            'description': 'Description',
            'pdf_file': 'PDF File',
            'cancel': 'Cancel',
            'save': 'Save',
            'enter_library': 'Enter Library',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'enter_first_name': 'Enter your first name',
            'enter_last_name': 'Enter your last name',
            'enter_email': 'Enter your email address',
            'your_given_name': 'Your given name',
            'your_family_name': 'Your family name',
            'we_never_share': "We'll never share your email with anyone else",
            'no_password_required': 'No password required - just enter your name to get started!',
            'what_you_can_do': 'What You Can Do',
            'browse_books': 'Browse digital books',
            'search_books': 'Search by title or author',
            'download_books': 'Download PDF books',
            'add_books': 'Add new books to library',
            'view_details_books': 'View book details',
            'personalized_experience': 'Personalized experience',
            'upload_guidelines': 'Upload Guidelines',
            'only_pdf_accepted': 'Only PDF files are accepted',
            'max_file_size': 'Maximum file size: 16MB',
            'make_sure_readable': 'Make sure the PDF is readable and not corrupted',
            'provide_accurate_info': 'Provide accurate title and author information',
            'ai_powered_search': 'AI-Powered Search',
            'ask_ai_assistant': 'Ask Our AI Assistant',
            'your_question': 'Your Question or Search Query',
            'ask_anything': 'Ask our AI assistant anything about books, literature, or get personalized reading recommendations!',
            'ask_placeholder': 'Ask anything about books, literature, or get reading recommendations...',
            'examples': 'Examples: "Recommend a good mystery novel", "What is the theme of Romeo and Juliet?", "Find books about space exploration"',
            'clear': 'Clear',
            'search_with_ai': 'Search with AI',
            'ai_response': 'AI Response',
            'powered_by_openai': 'Powered by OpenAI ChatGPT',
            'copy_response': 'Copy Response',
            'ai_thinking': 'AI is thinking...',
            'please_wait': 'Please wait while our AI assistant processes your query.',
            'quick_questions': 'Quick Questions',
            'book_recommendations': 'Book Recommendations',
            'mystery_novels': 'Mystery novels',
            'classic_literature': 'Classic literature',
            'science_fiction': 'Science fiction',
            'general_questions': 'General Questions',
            'fiction_vs_nonfiction': 'Fiction vs Non-fiction',
            'reading_tips': 'Reading tips',
            'benefits_reading': 'Benefits of reading',
            'welcome_to_smart_library': 'Welcome to Smart Library',
            'please_enter_name': 'Please enter your name to continue',
            'book_added_successfully': 'Book added successfully!',
            'book_deleted_successfully': 'Book deleted successfully!',
            'goodbye': 'Goodbye,',
            'you_have_been_logged_out': 'You have been logged out.',
            'you_were_not_logged_in': 'You were not logged in.',
            'please_log_in': 'Please log in to access this page',
            'no_file_selected': 'No file selected',
            'invalid_file_type': 'Invalid file type. Only PDF files are allowed.',
            'file_not_found': 'File not found',
            'please_enter_search_query': 'Please enter a search query',
            'error_getting_ai_response': 'Error getting AI response',
            'error_deleting_file': 'Error deleting file',
            'book_deleted_from_database': 'Book deleted from database, but file was not found.',
            'built_with_flask': 'Built with Flask and Bootstrap.',
            'language': 'Language',
            'switch_to_english': 'Switch to English',
            'switch_to_arabic': 'Switch to Arabic',
            'book_information': 'Book Information',
            'quick_actions': 'Quick Actions',
            'view_all_books': 'View All Books',
            'delete': 'Delete',
            'search_results': 'Search Results',
            'search_query': 'Search Query',
            'found': 'Found',
            'book': 'book',
            'no_books_found': 'No Books Found',
            'no_books_found_message': 'No books found matching',
            'try_different_search': 'Try a different search term or browse all books.',
            'browse_all_books': 'Browse All Books',
            'back_to_all_books': 'Back to All Books',
            'search_again': 'Search Again',
            'search': 'Search',
            'books': 'Books',
            'articles': 'Articles',
            'digital_repositories': 'Digital Repositories',
            'open_access_websites': 'Open Access Websites',
            'generate_abstract': 'Generate Abstract',
            'abstract': 'Abstract',
            'generating_abstract': 'Generating Abstract...',
            'abstract_generated': 'Abstract Generated',
            'error_generating_abstract': 'Error Generating Abstract',
            'recently_added_books': 'Recently Added Books',
            'all_books': 'All Books',
            'search_books_placeholder': 'Search books...',
            'sail_through_library': 'Sail through your smart library',
            'generate_annotation': 'Annotation',
            'annotation': 'Annotation',
            'generating_annotation': 'Generating Annotation...',
            'annotation_generated': 'Annotation Generated',
            'error_generating_annotation': 'Error Generating Annotation',
            'book_cover_image': 'Book Cover Image',
            'image_guideline': 'Optional image (PNG/JPG/GIF/WEBP) up to 5MB',
            'image_too_large': 'Image file too large. Maximum is 5MB',
            'invalid_image_file': 'Invalid image file',
            'invalid_image_type': 'Invalid image type. Allowed: PNG, JPG, GIF, WEBP',
            'image_required': 'Cover image is required for every book'
        }
    }
    
    return translations[current_lang]

# Authorization helpers
ALLOWED_ADD_BOOK_EMAIL = 'badrelddinahmidat@gmail.com'

def can_add_books():
    """Return True if the current session user is allowed to add books."""
    return session.get('email') == ALLOWED_ADD_BOOK_EMAIL

 

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB max image size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash(get_translations()['please_log_in'], 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    """Check if the uploaded image has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_ALLOWED_EXTENSIONS

def validate_image_file(file_stream):
    """Validate that the uploaded file is a real image.
    Prefer Pillow verification; fall back to imghdr if Pillow is unavailable.
    """
    try:
        file_stream.seek(0)
        if PIL_AVAILABLE and Image is not None:
            with Image.open(file_stream) as img:
                img.verify()
            file_stream.seek(0)
            return True
        # Fallback: imghdr check
        detected = imghdr.what(file_stream) if imghdr else None
        file_stream.seek(0)
        return detected in {'jpeg', 'png', 'gif', 'webp'}
    except Exception:
        file_stream.seek(0)
        return False

def init_database():
    """Initialize the SQLite database with books table."""
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Create books table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            image_filename TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration: add image_filename column if missing
    cursor.execute("PRAGMA table_info(books)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'image_filename' not in columns:
        cursor.execute('ALTER TABLE books ADD COLUMN image_filename TEXT')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/set_language/<language>')
def set_language(language):
    """Set the language for the session."""
    if language in LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/')
@login_required
def index():
    """Homepage displaying search bar, recent books, and all books."""
    conn = get_db_connection()
    # Get recent books (last 6 books)
    recent_books = conn.execute('SELECT * FROM books ORDER BY upload_date DESC LIMIT 6').fetchall()
    # Get all books
    all_books = conn.execute('SELECT * FROM books ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('index.html', recent_books=recent_books, all_books=all_books, t=get_translations(), lang_data=get_language_data(), can_add_book=can_add_books())

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add a new book to the library."""
    t = get_translations()
    # Restrict access to the add page by email
    if not can_add_books():
        flash(t['please_log_in'], 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        
        # Check if file was uploaded
        if 'file' not in request.files:
            flash(t['no_file_selected'], 'error')
            return redirect(request.url)
        
        file = request.files['file']
        image_file = request.files.get('image')
        
        if file.filename == '':
            flash(t['no_file_selected'], 'error')
            return redirect(request.url)
        
        # Validate PDF size
        if file and hasattr(file, 'seek'):
            file.seek(0, os.SEEK_END)
            if file.tell() > MAX_FILE_SIZE:
                file.seek(0)
                flash(t['max_file_size'], 'error')
                return redirect(request.url)
            file.seek(0)

        # Validate image if provided
        image_filename_to_save = None
        if image_file and image_file.filename:
            if not allowed_image(image_file.filename):
                flash(t.get('invalid_image_type', 'Invalid image type. Allowed: PNG, JPG, GIF, WEBP'), 'error')
                return redirect(request.url)
            # size check
            image_file.stream.seek(0, os.SEEK_END)
            if image_file.stream.tell() > MAX_IMAGE_SIZE:
                image_file.stream.seek(0)
                flash(t.get('image_too_large', 'Image file too large'), 'error')
                return redirect(request.url)
            image_file.stream.seek(0)
            # content check
            if not validate_image_file(image_file.stream):
                flash(t.get('invalid_image_file', 'Invalid image file'), 'error')
                return redirect(request.url)

        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Save image if provided
            if image_file and image_file.filename:
                raw_image_name = secure_filename(image_file.filename)
                image_filename_to_save = timestamp + raw_image_name
                image_path = os.path.join(UPLOAD_FOLDER, image_filename_to_save)
                image_file.save(image_path)

            # Save book info to database
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO books (title, author, description, filename, image_filename) VALUES (?, ?, ?, ?, ?)',
                (title, author, description, filename, image_filename_to_save)
            )
            conn.commit()
            conn.close()
            
            flash(t['book_added_successfully'], 'success')
            return redirect(url_for('index'))
        else:
            flash(t['invalid_file_type'], 'error')
    
    return render_template('add_book.html', t=t, lang_data=get_language_data())

@app.route('/book/<int:book_id>')
@login_required
def book_detail(book_id):
    """Display book details and provide download option."""
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    
    if book is None:
        abort(404)
    
    return render_template('book_detail.html', book=book, t=get_translations(), lang_data=get_language_data())

@app.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    """Download a book PDF file."""
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    
    if book is None:
        abort(404)
    
    file_path = os.path.join(UPLOAD_FOLDER, book['filename'])
    
    if not os.path.exists(file_path):
        flash(get_translations()['file_not_found'], 'error')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True, download_name=f"{book['title']}.pdf")

@app.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """Serve uploaded files (images)."""
    safe_name = secure_filename(filename)
    return send_from_directory(UPLOAD_FOLDER, safe_name, conditional=True)

@app.route('/search')
def search():
    """Search books by title or author."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    books = conn.execute(
        'SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY upload_date DESC',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    
    return render_template('search_results.html', books=books, query=query, t=get_translations(), lang_data=get_language_data())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for users to enter their name and email."""
    t = get_translations()
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip()
        
        if not first_name or not last_name or not email:
            flash(t['please_enter_name'], 'error')
            return redirect(request.url)
        
        # Store user info in session
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['email'] = email
        session['logged_in'] = True
        
        flash(f'{t["welcome_back"]} {first_name} {last_name}!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html', t=t, lang_data=get_language_data())

@app.route('/logout')
def logout():
    """Logout user and clear session."""
    t = get_translations()
    if session.get('logged_in'):
        first_name = session.get('first_name', '')
        session.clear()
        flash(f'{t["goodbye"]} {first_name}! {t["you_have_been_logged_out"]}', 'info')
    else:
        flash(t['you_were_not_logged_in'], 'info')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """Delete a book from the library and remove its file."""
    t = get_translations()
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book is None:
        conn.close()
        abort(404)
    
    # Get the filename before deleting from database
    filename = book['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Delete from database
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    # Delete the file if it exists
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(t['book_deleted_successfully'], 'success')
        except Exception as e:
            flash(f'{t["error_deleting_file"]}: {str(e)}', 'error')
    else:
        flash(t['book_deleted_from_database'], 'warning')

    # Delete image file if it exists
    image_filename = book.get('image_filename') if isinstance(book, dict) else book['image_filename']
    if image_filename:
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
    
    return redirect(url_for('index'))

@app.route('/ai_search', methods=['GET', 'POST'])
def ai_search():
    """AI-powered search page using OpenAI ChatGPT API."""
    t = get_translations()
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        
        if not query:
            flash(t['please_enter_search_query'], 'error')
            return render_template('ai_search.html', t=t, lang_data=get_language_data())
        
        try:
            # Get available books from database for context
            conn = get_db_connection()
            books = conn.execute('SELECT title, author, description FROM books').fetchall()
            conn.close()
            
            # Create context about available books
            books_context = ""
            if books:
                books_context = "Available books in the library:\n"
                for book in books:
                    books_context += f"- {book['title']} by {book['author']}"
                    if book['description']:
                        books_context += f" ({book['description'][:100]}...)"
                    books_context += "\n"
            
            # Create the prompt for ChatGPT
            system_prompt = f"""You are a helpful AI assistant for a digital library called "Smart Library". 
            You help users find books, answer questions about literature, and provide reading recommendations.
            
            {books_context}
            
            Please provide helpful, accurate, and engaging responses about books, reading, and literature.
            If the user asks about specific books, check if they're available in the library above.
            Keep responses concise but informative."""
            
            # Make API call to OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return render_template('ai_search.html', 
                                 query=query, 
                                 ai_response=ai_response,
                                 user_logged_in=session.get('logged_in', False),
                                 t=t, lang_data=get_language_data())
            
        except Exception as e:
            flash(f'{t["error_getting_ai_response"]}: {str(e)}', 'error')
            return render_template('ai_search.html', query=query, t=t, lang_data=get_language_data())
    
    return render_template('ai_search.html', user_logged_in=session.get('logged_in', False), t=t, lang_data=get_language_data())

@app.route('/ai_search_api', methods=['POST'])
def ai_search_api():
    """API endpoint for AJAX AI search requests."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Please enter a search query'}), 400
        
        # Get available books from database for context
        conn = get_db_connection()
        books = conn.execute('SELECT title, author, description FROM books').fetchall()
        conn.close()
        
        # Create context about available books
        books_context = ""
        if books:
            books_context = "Available books in the library:\n"
            for book in books:
                books_context += f"- {book['title']} by {book['author']}"
                if book['description']:
                    books_context += f" ({book['description'][:100]}...)"
                books_context += "\n"
        
        # Create the prompt for ChatGPT
        system_prompt = f"""You are a helpful AI assistant for a digital library called "Smart Library". 
        You help users find books, answer questions about literature, and provide reading recommendations.
        
        {books_context}
        
        Please provide helpful, accurate, and engaging responses about books, reading, and literature.
        If the user asks about specific books, check if they're available in the library above.
        Keep responses concise but informative."""
        
        # Make API call to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'query': query,
            'response': ai_response
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting AI response: {str(e)}'}), 500

@app.route('/books')
@login_required
def books():
    """Books page - displays all books in the library."""
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('books.html', books=books, t=get_translations(), lang_data=get_language_data(), can_add_book=can_add_books())

@app.route('/articles')
@login_required
def articles():
    """Articles page - placeholder for articles functionality."""
    return render_template('articles.html', t=get_translations(), lang_data=get_language_data())

@app.route('/digital_repositories')
@login_required
def digital_repositories():
    """Digital Repositories page - placeholder for digital repositories functionality."""
    return render_template('digital_repositories.html', t=get_translations(), lang_data=get_language_data())

@app.route('/open_access_websites')
@login_required
def open_access_websites():
    """Open Access Websites page - placeholder for open access websites functionality."""
    return render_template('open_access_websites.html', t=get_translations(), lang_data=get_language_data())

@app.route('/generate_abstract/<int:book_id>', methods=['POST'])
@login_required
def generate_abstract(book_id):
    """Generate an abstract for a book using AI."""
    t = get_translations()
    try:
        # Get book information
        conn = get_db_connection()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        conn.close()
        
        if book is None:
            return jsonify({'error': 'Book not found'}), 404
        
        # Create prompt for abstract generation
        current_lang = get_current_language()
        language_instruction = "in Arabic" if current_lang == 'ar' else "in English"
        
        system_prompt = f"""You are an AI assistant that creates concise, informative abstracts for books. 
        Generate a well-structured abstract {language_instruction} that summarizes the main themes, key points, and value of the book.
        The abstract should be professional, clear, and between 150-300 words.
        Focus on the book's main content, themes, and significance."""
        
        user_prompt = f"""Please create an abstract for the following book:
        
        Title: {book['title']}
        Author: {book['author']}
        Description: {book['description'] if book['description'] else 'No description available'}
        
        Generate a comprehensive abstract that captures the essence of this book."""
        
        # Make API call to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        abstract = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'abstract': abstract,
            'book_title': book['title'],
            'book_author': book['author']
        })
        
    except Exception as e:
        return jsonify({'error': f'{t["error_generating_abstract"]}: {str(e)}'}), 500

@app.route('/generate_annotation/<int:book_id>', methods=['POST'])
@login_required
def generate_annotation(book_id):
    """Generate annotations for a book using AI."""
    t = get_translations()
    try:
        # Get book information
        conn = get_db_connection()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        conn.close()
        
        if book is None:
            return jsonify({'error': 'Book not found'}), 404
        
        # Create prompt for annotation generation
        current_lang = get_current_language()
        language_instruction = "in Arabic" if current_lang == 'ar' else "in English"
        
        system_prompt = f"""You are an AI assistant that creates detailed annotations and marginal notes for books. 
        Generate comprehensive annotations {language_instruction} that provide insights, explanations, and commentary on the book's content.
        The annotations should be educational, insightful, and help readers understand key concepts, themes, and important details.
        Focus on providing valuable context, explanations of complex ideas, and connections to broader themes.
        Format the annotations as a structured list with clear headings and bullet points."""
        
        user_prompt = f"""Please create detailed annotations for the following book:
        
        Title: {book['title']}
        Author: {book['author']}
        Description: {book['description'] if book['description'] else 'No description available'}
        
        Generate comprehensive annotations that would help readers understand and appreciate this book better.
        Include insights about themes, important concepts, historical context, and any other relevant information."""
        
        # Make API call to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        annotation = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'annotation': annotation,
            'book_title': book['title'],
            'book_author': book['author']
        })
        
    except Exception as e:
        return jsonify({'error': f'{t["error_generating_annotation"]}: {str(e)}'}), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
