CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isi VARCHAR(255) NOT NULL,
    dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO notes (isi) VALUES
    ('Pipeline Jenkins pertama berhasil dijalankan'),
    ('Aplikasi terhubung ke MySQL lewat Docker Compose');
