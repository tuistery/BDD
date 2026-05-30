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

-- Table Course
CREATE TABLE Course (
    Mnemonic VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Credits INT NOT NULL,
    Faculty VARCHAR(100)
) ENGINE=InnoDB;

-- Table Action
CREATE TABLE Action (
    Description VARCHAR(255) PRIMARY KEY,
    XpGain INT DEFAULT 0,
    CoinGain INT DEFAULT 0
) ENGINE=InnoDB;

-- Table Levels
CREATE TABLE Levels (
    RankLevel INT PRIMARY KEY,
    XpRequired INT NOT NULL
) ENGINE=InnoDB;

-- Table User
CREATE TABLE User (
    UID INT PRIMARY KEY,
    UName VARCHAR(255) NOT NULL,
    Pass VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    RegistrationDate DATE NOT NULL,
    Points INT DEFAULT 0,
    Xp INT DEFAULT 0,
    Title VARCHAR(100),
    RankLevel INT,
    FOREIGN KEY (RankLevel) REFERENCES Levels(RankLevel) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Table Summary
CREATE TABLE Summary (
    SID INT PRIMARY KEY,
    AuthorID INT NOT NULL,
    Course VARCHAR(20) NOT NULL,
    PublicationDate DATE NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Version VARCHAR(20) DEFAULT '1.0',
    Visibility ENUM('public', 'private', 'restricted') DEFAULT 'private',
    FOREIGN KEY (AuthorID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (Course) REFERENCES Course(Mnemonic) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table File
CREATE TABLE Files (
    SID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE,
    Type_mime VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    Size INT NOT NULL,
    Content LONGBLOB NOT NULL,
    UploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Transaction
CREATE TABLE Transaction (
    TID INT PRIMARY KEY,
    Description TEXT,
    UID INT NOT NULL,
    Amount INT NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Notes (
    UID INT,
    SID INT,
    Note INT,
    Comment VARCHAR(255),
    PRIMARY KEY (UID, SID),
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE 
 ) ENGINE=InnoDB;

-- Table Object
CREATE TABLE Object (
    OID INT PRIMARY KEY,
    Price INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Description TEXT
) ENGINE=InnoDB;

-- Table Title (Spécialisation de Object)
CREATE TABLE Title (
    OID INT PRIMARY KEY,
    Label VARCHAR(255) NOT NULL,
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Theme (Spécialisation de Object)
CREATE TABLE Theme (
    OID INT PRIMARY KEY,
    Colors VARCHAR(100),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Badge (Spécialisation de Object)
CREATE TABLE Badge (
    OID INT PRIMARY KEY,
    Symbol VARCHAR(255),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Inventory
CREATE TABLE Inventory (
    OID INT,
    OwnerID INT,
    Quantity INT DEFAULT 1,
    isActive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (OID, OwnerID),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE,
    FOREIGN KEY (OwnerID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- TABLES DE RELATIONS (Many-to-Many)
-- ============================================

-- Relation Contain (Inventory - Object)
-- Déjà gérée par la clé étrangère dans Inventory

-- ============================================
-- INDEX pour améliorer les performances
-- ============================================

CREATE INDEX idx_user_email ON User(Email);
CREATE INDEX idx_summary_course ON Summary(Course);
CREATE INDEX idx_summary_author ON Summary(AuthorID);
CREATE INDEX idx_transaction_user ON Transaction(UID);

INSERT INTO Action (Description, XpGain, CoinGain) VALUES
('Publication d''un résumé', 100, 50),
('Évaluation d''un résumé', 10, 5),
('Commentaire constructif reçu', 20, 10),
('Inscription sur la plateforme', 50, 20),
('Résumé signalé (sanction)', -50, -25),
('Achat d''un titre cosmétique', 5, 0),
('Résumé mis en favori par un tiers', 15, 10),
('Première connexion de la journée', 5, 2);

INSERT INTO Levels (RankLevel, XpRequired) VALUES
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

-- Pour la sécurité, impossible de supprimer un fichier dont le résumé associé existe toujours
DELIMITER //
CREATE TRIGGER block_file_sole_deletion
BEFORE DELETE ON Files
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