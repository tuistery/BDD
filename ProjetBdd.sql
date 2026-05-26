-- ============================================
-- Script de création de la base de données
-- Basé sur le diagramme fourni
-- ============================================

DROP DATABASE IF EXISTS ProjetBdd;
CREATE DATABASE ProjetBdd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ProjetBdd;

-- ============================================
-- TABLES PRINCIPALES
-- ============================================

-- Table AcademicYear
CREATE TABLE AcademicYear (
    Years VARCHAR(20) PRIMARY KEY,
    StartDate DATE,
    EndDate DATE
) ENGINE=InnoDB;

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

-- Table File
CREATE TABLE Files (
    FID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE,
    Type_mime VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    Size INT NOT NULL,
    Content LONGBLOB NOT NULL,
    UploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table Summary
CREATE TABLE Summary (
    SID INT PRIMARY KEY,
    AuthorID INT NOT NULL,
    FileID INT NOT NULL,
    Course VARCHAR(20) NOT NULL,
    PublicationDate DATE NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Version VARCHAR(20) DEFAULT '1.0',
    Visibility ENUM('public', 'private', 'restricted') DEFAULT 'private',
    FOREIGN KEY (AuthorID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (Course) REFERENCES Course(Mnemonic) ON DELETE CASCADE,
    FOREIGN KEY (FileID) REFERENCES Files(FID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Contribution
CREATE TABLE Contribution (
    CID INT PRIMARY KEY,
    UID INT NOT NULL,
    Contribution TEXT NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
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
    NID INT,
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
    Price DECIMAL(10, 2) NOT NULL,
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

-- Relation Belong_to (Course - AcademicYear)
CREATE TABLE Belong_to (
    Mnemonic VARCHAR(20),
    Years VARCHAR(20),
    PRIMARY KEY (Mnemonic, Years),
    FOREIGN KEY (Mnemonic) REFERENCES Course(Mnemonic) ON DELETE CASCADE,
    FOREIGN KEY (Years) REFERENCES AcademicYear(Years) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Is_apply_to (Summary - Contribution)
CREATE TABLE Is_apply_to (
    SID INT,
    CID INT,
    PRIMARY KEY (SID, CID),
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Is_defined (Contribution - Action)
CREATE TABLE Is_defined (
    CID INT,
    ActionDescription VARCHAR(255),
    PRIMARY KEY (CID, ActionDescription),
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE,
    FOREIGN KEY (ActionDescription) REFERENCES Action(Description) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Do (User - Contribution)
CREATE TABLE Do (
    UID INT,
    CID INT,
    PRIMARY KEY (UID, CID),
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Concern (Transaction - Contribution)
CREATE TABLE Concern (
    TID INT,
    CID INT,
    PRIMARY KEY (TID, CID),
    FOREIGN KEY (TID) REFERENCES Transaction(TID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Buy (Transaction - Inventory) - CORRECTION ICI !
-- La clé étrangère doit référencer TID vers Transaction.TID, pas Quantity
CREATE TABLE Buy (
    TID INT,
    OID INT,
    OwnerID INT,
    Quantity INT NOT NULL,
    PRIMARY KEY (TID, OID, OwnerID),
    FOREIGN KEY (TID) REFERENCES Transaction(TID) ON DELETE CASCADE,
    FOREIGN KEY (OID, OwnerID) REFERENCES Inventory(OID, OwnerID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Contain (Inventory - Object)
-- Déjà gérée par la clé étrangère dans Inventory

-- ============================================
-- INDEX pour améliorer les performances
-- ============================================

CREATE INDEX idx_user_email ON User(Email);
CREATE INDEX idx_summary_course ON Summary(Course);
CREATE INDEX idx_summary_author ON Summary(AuthorID);
CREATE INDEX idx_transaction_user ON Transaction(UID);
CREATE INDEX idx_contribution_user ON Contribution(UID);

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
(0, 0),
(1, 100),
(2, 200),
(3, 300),
(4, 400),
(5, 500),
(6, 600),
(7, 700),
(8, 800),
(9, 900),
(10, 1000);

-- En cas de suppression d'un résumé, le fichier associé est aussi supprimé
DELIMITER //

CREATE TRIGGER delete_file_on_summary_delete
BEFORE DELETE ON Summary
FOR EACH ROW
BEGIN
    IF OLD.FileID IS NOT NULL THEN
        DELETE FROM Files WHERE FID = OLD.FileID;
    END IF;
END //

DELIMITER ;

SELECT 'Base de données créée avec succès!' AS Message;
SHOW TABLES;