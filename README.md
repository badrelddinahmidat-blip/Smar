# Smart Library Web Application

A modern, responsive web application built with Flask for managing and reading digital books in PDF format, featuring AI-powered search capabilities.

## Features

- 📚 **Book Management**: Add, view, and download books
- 🔍 **Search Functionality**: Search books by title or author
- 🤖 **AI-Powered Search**: Ask questions and get intelligent responses using OpenAI ChatGPT
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🎨 **Modern UI**: Clean interface built with Bootstrap 5
- 📄 **PDF Support**: Upload and download PDF files
- 💾 **SQLite Database**: Simple and reliable data storage
- 🔒 **File Validation**: Secure file upload with size and type restrictions
- 👤 **User Authentication**: Simple login system with personalized experience

## Screenshots

The application includes:
- Homepage with book listings
- Add book form with file upload
- Book detail pages
- Search results
- Responsive navigation

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   # If you have git installed
   git clone <repository-url>
   cd digital-library
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API (for AI search)**
   - Get your API key from: https://platform.openai.com/api-keys
   - Edit the `.env` file and replace `your_openai_api_key_here` with your actual API key
   - Change the Flask secret key to a secure value

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your web browser and go to: `http://localhost:5000`

## Project Structure

```
digital-library/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── library.db            # SQLite database (created automatically)
├── uploads/              # Directory for uploaded PDF files
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── add_book.html     # Add book form
│   ├── book_detail.html  # Book details page
│   └── search_results.html # Search results
└── static/               # Static files
    ├── style.css         # Custom CSS
    └── script.js         # JavaScript functions
```

## Usage

### Adding Books

1. Click "Add New Book" from the homepage or navigation
2. Fill in the book details:
   - **Title**: The book title (required)
   - **Author**: The author name (required)
   - **Description**: Brief description (optional)
   - **PDF File**: Select a PDF file (required, max 16MB)
3. Click "Add Book" to upload

### Viewing Books

- **Homepage**: Browse all available books
- **Book Cards**: Each book is displayed in a card with title, author, and description
- **View Details**: Click "View Details" to see full book information
- **Download**: Click "Download" to get the PDF file

### Searching Books

- Use the search bar in the navigation
- Search by book title or author name
- Results are displayed on a dedicated search page

### AI-Powered Search

- Click "AI Search" in the navigation
- Ask questions about books, literature, or get reading recommendations
- Examples: "Recommend a good mystery novel", "What is the theme of Romeo and Juliet?"
- Get intelligent responses powered by OpenAI ChatGPT
- Copy responses to clipboard for easy sharing

## Configuration

### File Upload Settings

The application is configured with the following limits:
- **Maximum file size**: 16MB
- **Allowed file types**: PDF only
- **Upload directory**: `uploads/`

To modify these settings, edit the configuration variables in `app.py`:

```python
UPLOAD_FOLDER = 'uploads'           # Upload directory
ALLOWED_EXTENSIONS = {'pdf'}        # Allowed file extensions
MAX_FILE_SIZE = 16 * 1024 * 1024    # Max file size in bytes
```

### Database

The application uses SQLite for data storage. The database file (`library.db`) is created automatically when you first run the application.

**Database Schema:**
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT,
    filename TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Running in Development Mode

The application runs in debug mode by default, which provides:
- Automatic reloading when code changes
- Detailed error messages
- Debug console

### Customization

#### Styling
- Edit `static/style.css` to customize the appearance
- The application uses Bootstrap 5 for responsive design
- Font Awesome icons are included for better UI

#### Functionality
- Add new routes in `app.py`
- Create new templates in the `templates/` directory
- Add JavaScript functionality in `static/script.js`

## Security Considerations

### Production Deployment

For production deployment, consider:

1. **Change the secret key**:
   ```python
   app.secret_key = 'your-production-secret-key'
   ```

2. **Disable debug mode**:
   ```python
   app.run(debug=False)
   ```

3. **Use environment variables** for sensitive configuration

4. **Implement user authentication** if needed

5. **Add file type validation** beyond just extension checking

6. **Use HTTPS** for secure file uploads

### File Upload Security

The application includes basic security measures:
- File extension validation
- Secure filename handling
- File size limits
- Upload directory isolation

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

2. **Permission denied for uploads**
   - Ensure the `uploads/` directory has write permissions

3. **Database errors**
   - Delete `library.db` to reset the database
   - The database will be recreated on next run

4. **File upload fails**
   - Check file size (must be under 16MB)
   - Ensure file is a valid PDF
   - Check upload directory permissions

### Error Messages

- **"No file selected"**: Make sure to select a PDF file
- **"Invalid file type"**: Only PDF files are allowed
- **"File not found"**: The uploaded file may have been moved or deleted

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Create an issue in the project repository

## Future Enhancements

Potential features for future versions:
- User authentication and authorization
- Book categories and tags
- Reading progress tracking
- Book ratings and reviews
- Advanced search filters
- Bulk book upload
- Book cover image support
- API endpoints for mobile apps
