# PDF/Word File Converter

A modern web application for converting between PDF and Word documents using LibreOffice, built with Flask, Docker Compose, Nginx, and MySQL.

## Features

- **PDF to Word Conversion**: Convert PDF files to editable Word documents
- **Word to PDF Conversion**: Convert Word documents to PDF format
- **Modern UI**: Beautiful, responsive web interface with drag-and-drop support
- **Real-time Progress**: Live status updates during conversion
- **File Management**: Automatic file cleanup and organized storage
- **Database Tracking**: MySQL database to track conversion history
- **Docker Deployment**: Easy deployment with Docker Compose

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL 8.0
- **Web Server**: Nginx
- **File Conversion**: LibreOffice (headless mode)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone or download the project files**

2. **Start the application**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost`

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Project Structure

```
python_convert/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── nginx.conf            # Nginx configuration
├── init.sql              # Database initialization
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── script.js     # Frontend JavaScript
├── uploads/              # Uploaded files (created automatically)
├── converted/            # Converted files (created automatically)
└── README.md             # This file
```

## Usage

### Converting Files

1. **Choose Conversion Type**:
   - Click "PDF to Word" to convert PDF files to Word documents
   - Click "Word to PDF" to convert Word documents to PDF files

2. **Upload File**:
   - Drag and drop your file onto the upload area, or
   - Click "Choose File" to select a file from your computer

3. **Start Conversion**:
   - Click "Start Conversion" to begin the process
   - Monitor the progress in real-time

4. **Download Result**:
   - Once conversion is complete, click "Download File" to get your converted document

### Supported File Types

- **PDF to Word**: `.pdf` files
- **Word to PDF**: `.docx` and `.doc` files
- **Maximum file size**: 100MB

## Configuration

### Environment Variables

The application uses the following environment variables (configured in `docker-compose.yml`):

- `MYSQL_HOST`: Database host (default: `db`)
- `MYSQL_USER`: Database username (default: `converter`)
- `MYSQL_PASSWORD`: Database password (default: `converter123`)
- `MYSQL_DATABASE`: Database name (default: `file_converter`)

### Customizing the Setup

1. **Change Database Credentials**:
   Edit the environment variables in `docker-compose.yml`

2. **Modify File Size Limits**:
   Update `client_max_body_size` in `nginx.conf` and `MAX_CONTENT_LENGTH` in `app.py`

3. **Change Ports**:
   Modify the port mappings in `docker-compose.yml`

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload and start file conversion
- `GET /status/<id>`: Check conversion status
- `GET /download/<id>`: Download converted file
- `GET /conversions`: List recent conversions

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Check what's using port 80
   sudo lsof -i :80
   # Or change the port in docker-compose.yml
   ```

2. **Permission Issues**:
   ```bash
   # Ensure proper permissions for upload/converted directories
   sudo chown -R $USER:$USER uploads converted
   ```

3. **Database Connection Issues**:
   ```bash
   # Restart the database service
   docker-compose restart db
   ```

4. **LibreOffice Conversion Failures**:
   - Check file format compatibility
   - Ensure file is not corrupted
   - Verify file size is within limits

### Logs

View application logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs nginx
docker-compose logs db
```

### Data Persistence

- **Database**: Data is persisted in a Docker volume (`mysql_data`)
- **Files**: Uploaded and converted files are stored in local directories
- **Backup**: Consider backing up the `mysql_data` volume and file directories

## Development

### Local Development Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL** (or use Docker):
   ```bash
   docker run --name mysql-converter -e MYSQL_ROOT_PASSWORD=root123 -e MYSQL_DATABASE=file_converter -e MYSQL_USER=converter -e MYSQL_PASSWORD=converter123 -p 3306:3306 -d mysql:8.0
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

### Adding New Features

1. **New Conversion Types**: Modify the conversion logic in `app.py`
2. **UI Changes**: Update `templates/index.html` and `static/css/style.css`
3. **API Extensions**: Add new routes in `app.py`

## Security Considerations

- File upload validation and sanitization
- SQL injection prevention with SQLAlchemy
- CORS configuration for API endpoints
- File size limits to prevent DoS attacks
- Temporary file cleanup

## Performance Optimization

- Nginx reverse proxy for static file serving
- Gzip compression enabled
- Database indexing for faster queries
- Background processing for file conversions
- File cleanup to manage disk space

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue with detailed information about your problem 