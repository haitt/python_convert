-- Create database if not exists
CREATE DATABASE IF NOT EXISTS file_converter;
USE file_converter;

-- Create conversions table
CREATE TABLE IF NOT EXISTS conversions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    converted_filename VARCHAR(255) NOT NULL,
    conversion_type ENUM('pdf_to_word', 'word_to_pdf') NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    error_message TEXT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_status ON conversions(status);
CREATE INDEX idx_created_at ON conversions(created_at);
CREATE INDEX idx_conversion_type ON conversions(conversion_type); 