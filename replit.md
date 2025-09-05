# Certificate Verification System

## Overview

This is a Flask-based certificate verification system that provides blockchain-simulated security for digital certificates. The application enables universities to issue tamper-proof certificates and allows students, recruiters, and administrators to verify their authenticity through multiple methods including QR code scanning and manual ID verification.

The system implements a simplified blockchain architecture to ensure certificate integrity, generates unique QR codes for each certificate, and provides role-based access control for different user types (administrators, students, and recruiters).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Authentication**: Flask-Login for session management with role-based access control
- **Database**: SQLite by default with PostgreSQL support via environment configuration
- **File Management**: Local file storage in uploads directory with hash-based integrity verification
- **Security**: Password hashing using Werkzeug, SHA-256 file hashing, and simulated blockchain validation

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap 5 with Font Awesome icons for responsive design
- **JavaScript**: Vanilla JS with HTML5 QR code scanner integration
- **Styling**: Custom CSS with dark theme support and responsive layouts

### Data Model Design
- **Users**: Supports three roles (admin, student, recruiter) with secure password storage
- **Certificates**: Core entity with unique IDs, file storage, blockchain simulation, and QR code generation
- **Blockchain Simulation**: Previous hash linking for certificate chain integrity
- **File Storage**: Secure file handling with hash verification and upload validation

### Authentication & Authorization
- **Session-based authentication** using Flask-Login
- **Role-based access control** with different permissions for admins, students, and recruiters
- **Secure password handling** with salted hashing
- **Protected routes** requiring login for sensitive operations

### Certificate Processing Pipeline
- **File Upload**: Secure file handling with extension validation and size limits
- **Hash Generation**: SHA-256 file integrity verification
- **Blockchain Simulation**: Previous hash linking for tamper detection
- **QR Code Generation**: Automatic QR code creation for mobile verification
- **Unique ID Generation**: Cryptographically secure certificate identifiers

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework for routing and request handling
- **SQLAlchemy**: Database ORM with support for multiple database backends
- **Flask-Login**: User session management and authentication

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme from CDN
- **Font Awesome 6**: Icon library from CDN
- **HTML5 QR Code Scanner**: Client-side QR code scanning functionality

### Security & Cryptography
- **Werkzeug**: Password hashing and secure filename handling
- **hashlib**: SHA-256 hash generation for file integrity
- **secrets**: Cryptographically secure random ID generation

### File Processing
- **PIL (Pillow)**: Image processing for QR code generation
- **qrcode**: QR code generation library
- **Werkzeug file utilities**: Secure file upload handling

### Database Configuration
- **SQLite**: Default development database
- **PostgreSQL**: Production database support via DATABASE_URL environment variable
- **Connection pooling**: Configured with pool_recycle and pool_pre_ping for reliability

### Deployment & Infrastructure
- **ProxyFix middleware**: Support for reverse proxy deployments
- **Environment-based configuration**: Flexible settings via environment variables
- **File upload limits**: 16MB maximum file size with configurable upload directory