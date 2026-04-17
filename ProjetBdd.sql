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

CREATE TABLE Notes (
    NID VARCHAR(50),
    UID VARCHAR(50),
    SID VARCHAR(50),
    Note INT,
    Comment VARCHAR(255),
    PRIMARY KEY (UID, SID),
    FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE,
    FOREIGN KEY (SID) REFERENCES Summary(SID) ON DELETE CASCADE 
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

INSERT INTO Course (Mnemonic, Name, Credits, Faculty) VALUES
-- Cours d'Informatique
('INFOH100', 'Introduction à la programmation', 5, 'Informatique'),
('INFOH101', 'Algorithmique', 5, 'Informatique'),
('INFOH102', 'Structures de données', 5, 'Informatique'),
('INFOH200', 'Programmation orientée objet', 5, 'Informatique'),
('INFOH201', 'Programmation avancée', 5, 'Informatique'),
('INFOH202', 'Développement web', 5, 'Informatique'),
('INFOH203', 'Bases de données avancées', 5, 'Informatique'),
('INFOH300', 'Systèmes d\'exploitation', 5, 'Informatique'),
('INFOH301', 'Réseaux informatiques', 5, 'Informatique'),
('INFOH302', 'Sécurité informatique', 5, 'Informatique'),
('INFOH303', 'Bases de données', 5, 'Informatique'),
('INFOH304', 'Génie logiciel', 5, 'Informatique'),
('INFOH305', 'Architecture des ordinateurs', 5, 'Informatique'),
('INFOH306', 'Compilation', 5, 'Informatique'),
('INFOH307', 'Programmation concurrente', 5, 'Informatique'),
('INFOH308', 'Cloud computing', 5, 'Informatique'),
('INFOH309', 'Big Data', 5, 'Informatique'),
('INFOH310', 'Machine learning', 5, 'Informatique'),
('INFOH311', 'Intelligence artificielle', 5, 'Informatique'),
('INFOH312', 'Vision par ordinateur', 5, 'Informatique'),

-- Cours de Mathématiques
('MATH100', 'Mathématiques discrètes', 5, 'Mathématiques'),
('MATH101', 'Analyse 1', 5, 'Mathématiques'),
('MATH102', 'Analyse 2', 5, 'Mathématiques'),
('MATH200', 'Algèbre linéaire', 5, 'Mathématiques'),
('MATH201', 'Probabilités', 5, 'Mathématiques'),
('MATH202', 'Statistiques', 5, 'Mathématiques'),
('MATH203', 'Optimisation', 5, 'Mathématiques'),
('MATH204', 'Processus stochastiques', 5, 'Mathématiques'),

-- Cours de Sciences (Physique)
('PHYS100', 'Physique générale', 5, 'Sciences'),
('PHYS101', 'Mécanique', 5, 'Sciences'),
('PHYS102', 'Électricité et magnétisme', 5, 'Sciences'),
('PHYS200', 'Thermodynamique', 5, 'Sciences'),
('PHYS201', 'Optique', 5, 'Sciences'),

-- Cours d'Économie
('ECON100', 'Introduction à l\'économie', 5, 'Économie'),
('ECON101', 'Microéconomie', 5, 'Économie'),
('ECON102', 'Macroéconomie', 5, 'Économie'),
('ECON200', 'Économie internationale', 5, 'Économie'),
('ECON201', 'Économétrie', 5, 'Économie'),

-- Cours de Langues
('LANG100', 'Anglais académique', 3, 'Langues'),
('LANG101', 'Communication écrite', 3, 'Langues'),
('LANG102', 'Communication orale', 3, 'Langues'),
('LANG200', 'Anglais avancé', 3, 'Langues'),
('LANG201', 'Rédaction scientifique', 3, 'Langues'),

-- Cours de Gestion
('MGMT100', 'Introduction au management', 5, 'Gestion'),
('MGMT200', 'Gestion de projet', 5, 'Gestion'),
('MGMT201', 'Entrepreneuriat', 5, 'Gestion'),
('MGMT202', 'Management stratégique', 5, 'Gestion');

INSERT INTO Action (Description, XpGain, CoinGain) VALUES
('Publication d’un résumé', 100, 50),
('Évaluation d’un résumé', 10, 5),
('Commentaire constructif reçu', 20, 10),
('Inscription sur la plateforme', 50, 20),
('Résumé signalé (sanction)', -50, -25),
('Achat d’un titre cosmétique', 5, 0),
('Résumé mis en favori par un tiers', 15, 10),
('Première connexion de la journée', 5, 2);

-- Table Object (TOUS les objets)
INSERT INTO Object (OID, Price, Name, Description) VALUES
('1', 50.00, 'Débutant', 'Attribué aux nouveaux contributeurs'),
('2', 100.00, 'Apprenti', 'Premier niveau de contribution'),
('3', 200.00, 'Contributeur actif', 'Publie régulièrement des résumés'),
('4', 500.00, 'Contributeur expert', 'Publie des résumés de qualité'),
('5', 1000.00, 'Expert SQL', 'Maîtrise des bases de données'),
('6', 1500.00, 'Top Contributeur', 'Parmi les meilleurs utilisateurs'),
('7', 2000.00, 'Maître du savoir', 'Expert académique reconnu'),
('8', 3000.00, 'Légende du campus', 'Statut exceptionnel'),
('9', 300.00, 'Profil sombre', 'Thème sombre pour le profil'),
('10', 300.00, 'Profil clair', 'Thème clair alternatif'),
('11', 400.00, 'Thème nuit', 'Interface nocturne'),
('12', 400.00, 'Thème pastel', 'Couleurs douces'),
('13', 150.00, 'Icône étoile', 'Icône spéciale'),
('14', 200.00, 'Icône flamme', 'Activité élevée'),
('15', 250.00, 'Icône trophée', 'Symbole de réussite'),
('16', 150.00, 'Icône livre', 'Passion pour l\'étude'),
('17', 300.00, 'Icône cerveau', 'Intellect élevé'),
('18', 400.00, 'Badge bronze', 'Badge bronze'),
('19', 800.00, 'Badge argent', 'Badge argent'),
('20', 1200.00, 'Badge or', 'Badge or'),
('21', 2000.00, 'Badge diamant', 'Badge premium'),
('22', 100.00, 'Cadre simple', 'Cadre basique'),
('23', 600.00, 'Cadre premium', 'Cadre avancé'),
('24', 1200.00, 'Cadre doré', 'Cadre luxueux'),
('25', 700.00, 'Effet brillant', 'Effet visuel'),
('26', 900.00, 'Effet feu', 'Effet animé'),
('27', 900.00, 'Effet glace', 'Effet givré'),
('28', 800.00, 'Titre étudiant modèle', 'Utilisateur exemplaire'),
('29', 1200.00, 'Titre mentor', 'Aide les autres'),
('30', 2000.00, 'Titre professeur', 'Très expérimenté'),
('31', 1100.00, 'Badge IA', 'Spécialiste IA'),
('32', 900.00, 'Badge math', 'Expert mathématiques'),
('33', 900.00, 'Badge physique', 'Expert physique'),
('34', 900.00, 'Badge économie', 'Expert économie'),
('35', 300.00, 'Icône fusée', 'Progression rapide'),
('36', 300.00, 'Icône éclair', 'Réactivité'),
('37', 300.00, 'Icône cible', 'Précision'),
('38', 800.00, 'Thème sombre premium', 'Thème sombre avancé'),
('39', 900.00, 'Thème néon', 'Couleurs flashy'),
('40', 2500.00, 'Titre VIP', 'Utilisateur premium'),
('41', 3000.00, 'Titre élite', 'Top utilisateurs'),
('42', 150.00, 'Badge participation', 'Participation active'),
('43', 300.00, 'Badge fidélité', 'Utilisateur régulier'),
('44', 700.00, 'Cadre arc-en-ciel', 'Cadre coloré'),
('45', 1000.00, 'Effet holographique', 'Effet futuriste');

-- Table Badge (type="badge")
INSERT INTO Badge (OID, Symbol) VALUES
('1', '🎓'),
('2', '📚'),
('3', '✨'),
('4', '⭐'),
('5', '🗄️'),
('18', '🥉'),
('19', '🥈'),
('20', '🥇'),
('21', '💎'),
('31', '🤖'),
('32', '➕'),
('33', '⚛️'),
('34', '📈'),
('42', '👥'),
('43', '🔥');

-- Table Title (type="titre")
INSERT INTO Title (OID, Label) VALUES
('1', 'Débutant'),
('2', 'Apprenti'),
('3', 'Contributeur actif'),
('4', 'Contributeur expert'),
('5', 'Expert SQL'),
('6', 'Top Contributeur'),
('7', 'Maître du savoir'),
('8', 'Légende du campus'),
('28', 'Étudiant modèle'),
('29', 'Mentor'),
('30', 'Professeur'),
('40', 'VIP'),
('41', 'Élite');

-- Table Theme (type="theme")
INSERT INTO Theme (OID, Colors) VALUES
('9', '#1a1a1a,#ffffff'),
('10', '#ffffff,#000000'),
('11', '#0a0a0a,#16213e'),
('12', '#ffd1dc,#c9a0dc'),
('38', '#0d0d0d,#2a2a2a'),
('39', '#ff00ff,#00ffff');

SELECT 'Base de données créée avec succès!' AS Message;
SHOW TABLES;

DROP USER IF EXISTS 'enigma'@'localhost';

CREATE USER 'enigma'@'localhost' IDENTIFIED BY 'Eni@2006';

GRANT ALL PRIVILEGES ON ProjetBdd.* TO 'enigma'@'localhost';

FLUSH PRIVILEGES;