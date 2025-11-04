-- script to build database

<<<<<<< HEAD
-- login information
-- DB_HOST='localhost'
-- DB_PORT='5432'
-- DB_NAME='advising'
-- DB_USER='username'

-- CREATE DATABASE IF NOT EXISTS advising;

=======
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
SELECT 'CREATE DATABASE advising'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'advising')\gexec

\c advising;

CREATE TABLE users 
(
    userid BIGSERIAL PRIMARY KEY, 
    firstname VARCHAR(50), 
    lastname VARCHAR(50), 
    email VARCHAR(50) UNIQUE NOT NULL, 
    phonenumber BIGINT, 
<<<<<<< HEAD
    role VARCHAR(10) CHECK (role IN ('admin', 'advisor', 'student')), 
=======
    role VARCHAR(10) CHECK (LOWER(role) IN ('admin', 'advisor', 'student')), 
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
    school VARCHAR(50)
);

CREATE TABLE admin 
(
<<<<<<< HEAD
    adminid BIGINT PRIMARY KEY REFERENCES users(userid)
=======
    adminid BIGSERIAL PRIMARY KEY --REFERENCES users(userid) ON DELETE CASCADE
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
) INHERITS (users);

CREATE TABLE advisor 
(
<<<<<<< HEAD
    advisorid BIGINT PRIMARY KEY REFERENCES users(userid)
=======
    advisorid BIGSERIAL PRIMARY KEY --REFERENCES users(userid) ON DELETE CASCADE
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
) INHERITS (users);

CREATE TABLE student 
(
<<<<<<< HEAD
    BIGINT PRIMARY KEY REFERENCES users(userid),
    classes JSONB, 
=======
    studentid BIGSERIAL PRIMARY KEY, --REFERENCES users(userid) ON DELETE CASCADE,
    -- classes JSONB, 
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
    gpa FLOAT,
    major VARCHAR(50), 
    majorconcentration VARCHAR(50), 
    minor VARCHAR(50), 
    classstanding VARCHAR(50), 
    financialhold BOOLEAN DEFAULT FALSE, 
    advisinghold BOOLEAN DEFAULT FALSE, 
    academichold BOOLEAN DEFAULT FALSE, 
    registrationstatus BOOLEAN DEFAULT FALSE, 
    advisingstatus BOOLEAN DEFAULT FALSE, 
    activestatus BOOLEAN DEFAULT TRUE, -- get this done!!!
    dateadvised TIMESTAMP
) INHERITS (users);

-- CREATE TABLE admin_and_advisors 
-- (
--     adminandadvisorid BIGSERIAL PRIMARY KEY, 
--     advisorid BIGINT REFERENCES advisor (advisorid) ON DELETE CASCADE, 
--     adminid BIGINT REFERENCES admin (adminid) ON DELETE CASCADE
-- );

CREATE TABLE advisor_and_students 
(
    advisorandstudentid BIGSERIAL PRIMARY KEY, 
    studentid BIGINT REFERENCES student (studentid) ON DELETE CASCADE, 
    advisorid BIGINT REFERENCES advisor (advisorid) ON DELETE CASCADE
);

CREATE TABLE transcript 
(
    transcriptid BIGSERIAL PRIMARY KEY, 
    studentid BIGINT REFERENCES student (studentid) ON DELETE CASCADE, 
    coursemap JSONB, 
    coursecode VARCHAR(15), 
    subject VARCHAR(50), 
    hours BIGINT
);

-- insertions --


CREATE TABLE currentcourses (
    currentcourseid BIGSERIAL PRIMARY KEY,
    section VARCHAR(100),
    courseavailability VARCHAR(15),
    deliverymode VARCHAR(15),
    meetingpattern VARCHAR(300),
    courselocation VARCHAR(100),
    instructor VARCHAR(50),
    capacity VARCHAR(5),
    enrolled VARCHAR(5),
    academicperiod VARCHAR(100),
    startdate VARCHAR(20)
);

INSERT INTO admin (firstname, lastname, email, phonenumber, role, school)
<<<<<<< HEAD
VALUES ('TestAdmin', 'Works', 'ta@uafs.edu', 4445556666, 'admin', 'UAFS');

INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Andrew', 'Mackey', 'amackey00@uafs.edu', 3332226666, 'advisor', 'UAFS');

INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Israel', 'Cuevas', 'icuevas00@uafs.edu', 3332226666, 'advisor', 'UAFS');

INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Brittany', 'Bright', 'bbright00@uafs.edu', 3332226666, 'advisor', 'UAFS');

-- userid | firstname | lastname | email | phonenumber | role | school | studentid | classes 
-- | gpa | major | majorconcentration | minor | classstanding | financialhold | advisinghold | academichold 
-- | registrationstatus | advisingstatus | activestatus | dateadvised 
INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Elysia', 'Aeides', 'ely00@uafs.edu', 4448889999, 'student', 'UAFS', '{}'::jsonb, 3.7, 'Astrophysics', 'General',
            '', 'Senior', FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Albedo', 'Kreidenprez', 'akreiden00@uafs.edu', 1234546788, 'student', 'UAFS', '{}'::jsonb, 4.0, 'BioChem', 'General',
            'Art', 'Junior', FALSE, TRUE, TRUE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Alice', 'K', 'ak00@uafs.edu', 1234546788, 'student', 'UAFS', '{}'::jsonb, 2.8, 'Chemistry', 'General',
            '', 'Senior', FALSE, TRUE, TRUE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Jean', 'Gunhildr', 'jgunhil00@uafs.edu', 1234546788, 'student', 'UAFS', '{}'::jsonb, 3.8, 'Business', 'General',
            '', 'Junior', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Barbara', 'Gunhildr', 'bgunhil00@uafs.edu', 9872452765, 'student', 'UAFS', '{}'::jsonb, 3.5, 'Music', 'Vocal',
            '', 'Freshman', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, classes, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Ayaka', 'Kamisato', 'akamisato01@uafs.edu', 9872452765, 'student', 'UAFS', '{}'::jsonb, 3.5, 'Business', 'Marketing',
            'Literature', 'Sophomore', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

--  advisorandstudentid | studentid | advisorid 

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (1, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (2, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (3, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (4, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (5, 2);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (6, 2);
=======
VALUES ('TestAdmin', 'Test', 'ta@uafs.edu', 4445556666, 'admin', 'UAFS');



-- INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
-- VALUES ('Andrew', 'Mackey', 'amackey00@uafs.edu', 3332226666, 'advisor', 'UAFS');

-- INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
-- VALUES ('Israel', 'Cuevas', 'icuevas00@uafs.edu', 3332226666, 'advisor', 'UAFS');

-- INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
-- VALUES ('Brittany', 'Bright', 'bbright00@uafs.edu', 3332226666, 'advisor', 'UAFS');



-- -- userid | firstname | lastname | email | phonenumber | role | school | studentid 
-- -- | gpa | major | majorconcentration | minor | classstanding | financialhold | advisinghold | academichold 
-- -- | registrationstatus | advisingstatus | activestatus | dateadvised 

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Cyrene', 'Aeides', 'ely00@uafs.edu', 4448889999, 'student', 'UAFS', 3.7, 'Astrophysics', 'General',
--             '', 'Senior', FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP);

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Albedo', 'Kreidenprez', 'akreiden00@uafs.edu', 1234546788, 'student', 'UAFS', 4.0, 'BioChem', 'General',
--             'Art', 'Junior', FALSE, TRUE, TRUE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Alice', 'K', 'ak00@uafs.edu', 1234546788, 'student', 'UAFS', 2.8, 'Chemistry', 'General',
--             '', 'Senior', FALSE, TRUE, TRUE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Jean', 'Gunhildr', 'jgunhil00@uafs.edu', 1234546788, 'student', 'UAFS', 3.8, 'Business', 'General',
--             '', 'Junior', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Barbara', 'Gunhildr', 'bgunhil00@uafs.edu', 9872452765, 'student', 'UAFS', 3.5, 'Music', 'Vocal',
--             '', 'Freshman', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);

-- INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
--             minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
--             activestatus, dateadvised)
-- VALUES ('Ayaka', 'Kamisato', 'akamisato01@uafs.edu', 9872452765, 'student', 'UAFS', 3.5, 'Business', 'Marketing',
--             'Literature', 'Sophomore', FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, CURRENT_TIMESTAMP);



--  advisorandstudentid | studentid | advisorid 

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (1, 6);

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (2, 1);

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (3, 1);

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (4, 1);

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (5, 2);

-- INSERT INTO advisor_and_students (studentid, advisorid)
-- VALUES (6, 2);
>>>>>>> b2cb8a3dd49f141e150077986ee47be1bfec2304
