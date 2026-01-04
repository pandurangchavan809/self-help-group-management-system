-- # 🟢 STEP 1: CREATE DATABASE

CREATE DATABASE mahila_bachat_gat
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE mahila_bachat_gat;

-- # 🟢 STEP 2: SHG GROUPS (CORE TABLE)

CREATE TABLE shg_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_number VARCHAR(50) NOT NULL UNIQUE,
    shg_name VARCHAR(150) NOT NULL,
    village VARCHAR(150),
    
    president_username VARCHAR(100) UNIQUE,
    president_password VARCHAR(255),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- # 🟢 STEP 3: MEMBERS (VIEW-ONLY USERS)

CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    mobile VARCHAR(10) NOT NULL,

    monthly_deposit INT DEFAULT 500,
    status ENUM('active','left') DEFAULT 'active',
    join_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shg_id) REFERENCES shg_groups(id)
);

-- # 🟢 STEP 4: DEPOSITS (MONTHLY SAVINGS)


CREATE TABLE deposits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT NOT NULL,
    member_id INT NOT NULL,

    amount INT NOT NULL,
    deposit_month INT NOT NULL,
    deposit_year INT NOT NULL,

    remarks VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shg_id) REFERENCES shg_groups(id),
    FOREIGN KEY (member_id) REFERENCES members(id),

    UNIQUE (member_id, deposit_month, deposit_year)
);


-- # 🟢 STEP 5: LOANS (NO DURATION MODEL)

CREATE TABLE loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT NOT NULL,
    member_id INT NOT NULL,

    loan_amount INT NOT NULL,
    interest_rate FLOAT DEFAULT 0,
    loan_date DATE NOT NULL,

    status ENUM('active','closed') DEFAULT 'active',
    closed_date DATE,

    remarks VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shg_id) REFERENCES shg_groups(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
);


-- # 🟢 STEP 6: LOAN PAYMENTS (INTEREST + PRINCIPAL)


CREATE TABLE loan_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,

    payment_type ENUM('interest','principal') NOT NULL,
    amount INT NOT NULL,
    payment_date DATE DEFAULT CURRENT_DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (loan_id) REFERENCES loans(id)
);

-- # 🟢 STEP 7: TRANSACTION LOG (TRUST & AUDIT)

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT NOT NULL,
    member_id INT,

    txn_type ENUM('deposit','loan_given','loan_payment') NOT NULL,
    reference_id INT,
    amount INT NOT NULL,

    created_by ENUM('president','admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shg_id) REFERENCES shg_groups(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- # 🟢 STEP 8: SMS LOG (FOR VERIFICATION)


CREATE TABLE sms_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT NOT NULL,
    member_id INT,

    mobile VARCHAR(10),
    message TEXT,
    status ENUM('sent','failed') DEFAULT 'sent',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shg_id) REFERENCES shg_groups(id)
);

-- # 🟢 STEP 9: ADMIN USERS (YOU)

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- # 🟢 STEP 10: SYSTEM AUDIT LOG (OPTIONAL BUT POWERFUL)

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shg_id INT,
    action TEXT,
    performed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
