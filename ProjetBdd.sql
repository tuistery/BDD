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
    UID VARCHAR(50) PRIMARY KEY,
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
    SID VARCHAR(50) PRIMARY KEY,
    AuthorID VARCHAR(50) NOT NULL,
    Course VARCHAR(20) NOT NULL,
    PublicationDate DATE NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Version VARCHAR(20) DEFAULT '1.0',
    Visibility ENUM('public', 'private', 'restricted') DEFAULT 'private',
    FOREIGN KEY (AuthorID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (Course) REFERENCES Course(Mnemonic) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Contribution
CREATE TABLE Contribution (
    CID VARCHAR(50) PRIMARY KEY,
    UID VARCHAR(50) NOT NULL,
    Contribution TEXT NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Transaction
CREATE TABLE Transaction (
    TID VARCHAR(50) PRIMARY KEY,
    Description TEXT,
    UID VARCHAR(50) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Object
CREATE TABLE Object (
    OID VARCHAR(50) PRIMARY KEY,
    Price DECIMAL(10, 2) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Description TEXT
) ENGINE=InnoDB;

-- Table Title (Spécialisation de Object)
CREATE TABLE Title (
    OID VARCHAR(50) PRIMARY KEY,
    Label VARCHAR(255) NOT NULL,
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Theme (Spécialisation de Object)
CREATE TABLE Theme (
    OID VARCHAR(50) PRIMARY KEY,
    Colors VARCHAR(100),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Badge (Spécialisation de Object)
CREATE TABLE Badge (
    OID VARCHAR(50) PRIMARY KEY,
    Symbol VARCHAR(255),
    FOREIGN KEY (OID) REFERENCES Object(OID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table Inventory
CREATE TABLE Inventory (
    OID VARCHAR(50),
    OwnerID VARCHAR(50),
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
    SID VARCHAR(50),
    CID VARCHAR(50),
    PRIMARY KEY (SID, CID),
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Is_defined (Contribution - Action)
CREATE TABLE Is_defined (
    CID VARCHAR(50),
    ActionDescription VARCHAR(255),
    PRIMARY KEY (CID, ActionDescription),
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE,
    FOREIGN KEY (ActionDescription) REFERENCES Action(Description) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Do (User - Contribution)
CREATE TABLE Do (
    UID VARCHAR(50),
    CID VARCHAR(50),
    PRIMARY KEY (UID, CID),
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Concern (Transaction - Contribution)
CREATE TABLE Concern (
    TID VARCHAR(50),
    CID VARCHAR(50),
    PRIMARY KEY (TID, CID),
    FOREIGN KEY (TID) REFERENCES Transaction(TID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Contribution(CID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relation Buy (Transaction - Inventory) - CORRECTION ICI !
-- La clé étrangère doit référencer TID vers Transaction.TID, pas Quantity
CREATE TABLE Buy (
    TID VARCHAR(50),
    OID VARCHAR(50),
    OwnerID VARCHAR(50),
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


INSERT INTO Course (Mnemonic, Name, Faculty) VALUES
('INFO-F101', 'Programmation', 'Sciences'),
('INFO-F102', 'Informatique et méthodes numériques', 'Sciences'),
('MATH-F113', 'Mathématiques générales I', 'Sciences'),
('MATH-F114', 'Mathématiques générales II', 'Sciences'),
('PHYS-F101', 'Physique I', 'Sciences'),
('PHYS-F102', 'Physique II', 'Sciences'),
('INFO-F201', 'Calculabilité', 'Sciences'),
('INFO-F202', 'Systèmes d\'exploitation', 'Sciences'),
('INFO-F203', 'Algorithmique et structures de données', 'Sciences'),
('INFO-F205', 'Introduction aux bases de données', 'Sciences'),
('INFO-F209', 'Programmation orientée objet', 'Sciences'),
('MATH-F205', 'Probabilités et statistique', 'Sciences'),
('INFO-F301', 'Compilation', 'Sciences'),
('INFO-F302', 'Réseaux informatiques', 'Sciences'),
('INFO-F303', 'Bases de données', 'Sciences'),
('INFO-F307', 'Théorie des langages', 'Sciences'),
('INFO-F308', 'Architecture des ordinateurs', 'Sciences'),
('INFO-F309', 'Génie logiciel', 'Sciences'),
('INFO-F401', 'Intelligence artificielle', 'Sciences'),
('INFO-F403', 'Introduction à l\'algorithmique', 'Sciences'),
('INFO-F404', 'Techniques de l\'intelligence artificielle', 'Sciences'),
('INFO-F405', 'Sécurité informatique', 'Sciences'),
('INFO-F408', 'Programmation de systèmes mobiles', 'Sciences'),
('INFO-F409', 'Apprentissage automatique', 'Sciences'),
('INFO-F410', 'Techniques avancées de programmation', 'Sciences'),
('INFO-F501', 'Compression de données', 'Sciences'),
('INFO-F505', 'Cloud computing et virtualisation', 'Sciences'),
('INFO-F514', 'Big Data', 'Sciences'),
('INFO-H515', 'Projet d\'informatique', 'Sciences'),
('INFO-Y080', 'Mémoire de fin d\'études', 'Sciences'),
('INFO-F422', 'Systèmes informatiques', 'Sciences'),
('INFO-F424', 'Calcul scientifique', 'Sciences'),
('INFO-H415', 'Analyse de données complexes', 'Sciences'),
('INFO-H417', 'Robotique', 'Sciences'),
('INFO-H423', 'Projet de développement', 'Sciences');

SELECT 'Base de données créée avec succès!' AS Message;
SHOW TABLES;

DROP USER IF EXISTS 'enigma'@'localhost';

CREATE USER 'enigma'@'localhost' IDENTIFIED BY 'Eni@2006';

GRANT ALL PRIVILEGES ON ProjetBdd.* TO 'enigma'@'localhost';

FLUSH PRIVILEGES;