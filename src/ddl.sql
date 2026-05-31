-- ============================================
-- Script de création de la base de données
-- Basé sur le diagramme fourni
-- ============================================

DROP DATABASE IF EXISTS AppDb;
CREATE DATABASE AppDb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE AppDb;

-- ============================================
-- TABLES PRINCIPALES
-- ============================================

CREATE TABLE Course (
    Mnemonic VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Credits INT NOT NULL,
    Faculty VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Action (
    Description VARCHAR(255) PRIMARY KEY,
    XpGain INT DEFAULT 0 NOT NULL,
    PointsGain INT DEFAULT 0 NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Level (
    RankLevel INT PRIMARY KEY,
    XpRequired INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE User (
    UID INT AUTO_INCREMENT PRIMARY KEY,
    UName VARCHAR(255) NOT NULL,
    EncryptedPassword VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    RegistrationDate DATE NOT NULL,
    Points INT DEFAULT 0 NOT NULL,
    Xp INT DEFAULT 0 NOT NULL,
    Title VARCHAR(100) NULL,
    RankLevel INT DEFAULT 1 NOT NULL,
    FOREIGN KEY (RankLevel) REFERENCES Level(RankLevel) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Summary (
    SID INT AUTO_INCREMENT PRIMARY KEY,
    AuthorID INT NOT NULL,
    Course VARCHAR(20) NOT NULL,
    PublicationDate DATE NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Version VARCHAR(20) DEFAULT '1.0' NOT NULL,
    Visibility ENUM('public', 'private', 'restricted') DEFAULT 'private' NOT NULL,
    FOREIGN KEY (AuthorID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (Course) REFERENCES Course(Mnemonic) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE File (
    SID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE,
    Type_mime VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    Size INT NOT NULL,
    Content LONGBLOB NOT NULL,
    UploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Transaction (
    TID INT AUTO_INCREMENT PRIMARY KEY,
    Description TEXT,
    UID INT NOT NULL,
    Amount INT NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Object (
    OID INT PRIMARY KEY,
    Price INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Type VARCHAR(20),
    Description TEXT
) ENGINE=InnoDB;

-- ============================================
-- TABLES DE RELATIONS (Many-to-Many)
-- ============================================
CREATE TABLE Rates (
    UID INT,
    SID INT,
    Note INT NOT NULL,
    Comment VARCHAR(255),
    PRIMARY KEY (UID, SID),
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE 
 ) ENGINE=InnoDB;

CREATE TABLE Owns (
    UID INT,
    OID INT,
    Quantity INT DEFAULT 1,
    isActive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (UID, OID),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- INITIALISATION DES TABLES
-- ============================================

INSERT INTO Action (Description, XpGain, PointsGain) VALUES
('Publication d''un résumé', 100, 50),
('Évaluation d''un résumé', 10, 5),
('Commentaire constructif reçu', 20, 10),
('Inscription sur la plateforme', 50, 20),
('Résumé signalé (sanction)', -50, -25),
('Achat d''un titre cosmétique', 5, 0),
('Résumé mis en favori par un tiers', 15, 10),
('Première connexion de la journée', 5, 2);

INSERT INTO Level (RankLevel, XpRequired) VALUES
(1, 0),
(2, 100),
(3, 300),
(4, 600),
(5, 1000),
(6, 1500),
(7, 2100),
(8, 2800),
(9, 3600),
(10, 4500);

-- ============================================
-- TRIGGERS
-- ============================================

-- Pour la sécurité, impossible de supprimer un fichier dont le résumé associé existe toujours
DELIMITER //
CREATE TRIGGER block_file_sole_deletion
BEFORE DELETE ON File
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Summary WHERE SID = OLD.SID) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erreur : Impossible de supprimer un fichier directement. Vous devez supprimer le résumé associé.';
    END IF;
END //
DELIMITER ;

SELECT 'Base de données créée avec succès!' AS Message;
SHOW TABLES;