-- script to build database

\if NOT EXISTS (SELECT FROM pg_database WHERE datname = 'advising')
  CREATE DATABASE advising;
\endif

\c advising;

CREATE TABLE users 
(
    userid BIGSERIAL PRIMARY KEY, 
    firstname VARCHAR(50), 
    lastname VARCHAR(50), 
    email VARCHAR(50) UNIQUE NOT NULL, 
    phonenumber BIGINT, 
    role VARCHAR(10) CHECK (LOWER(role) IN ('admin', 'advisor', 'student')), 
    school VARCHAR(50)
);

CREATE TABLE admin 
(
    adminid BIGSERIAL PRIMARY KEY --REFERENCES users(userid) ON DELETE CASCADE
) INHERITS (users);

CREATE TABLE advisor 
(
    advisorid BIGSERIAL PRIMARY KEY --REFERENCES users(userid) ON DELETE CASCADE
) INHERITS (users);

CREATE TABLE student 
(
    studentid BIGSERIAL PRIMARY KEY, --REFERENCES users(userid) ON DELETE CASCADE,
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
    dateadvised TIMESTAMP,
    classes JSONB
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
    program VARCHAR(100),
    concentration VARCHAR(100),
    year VARCHAR(50),
    institution VARCHAR(150),
    coursemap JSONB, 
    cumulative_gpa NUMERIC(3,2)
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

CREATE TABLE degreeplans (
    degree VARCHAR(50) PRIMARY KEY,
    institution VARCHAR(50) NOT NULL,
    majorcode VARCHAR(10) NOT NULL,
    credithourstotal INTEGER,
    notes JSONB,
    corecourses,
    concentrations
);

INSERT INTO admin (firstname, lastname, email, phonenumber, role, school)
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

-- INSERT INTO transcript (studentid, student_name, student_uid, program, concentration, year, institution, transcript, cumulative_gpa)
/* VALUES (
    1,
    'B.S. in Computer Science',
    'General',
    'Junior',
    'University of Arkansas - Fort Smith',
    '[
      {
        "semester": "Freshman Fall",
        "year": 2024,
        "courses": [
          { "code": "ENGL 1013", "title": "English Composition I", "credits": 3, "grade": "A" },
          { "code": "MATH 2804", "title": "Calculus I", "credits": 4, "grade": "B+" },
          { "code": "CS 1093", "title": "Computer Science Concepts", "credits": 3, "grade": "A-" },
          { "code": "FA/HUM/SOCSCI 1103", "title": "Introduction to Humanities", "credits": 3, "grade": "B" },
          { "code": "STEM 1001", "title": "College Prep for STEM Majors", "credits": 1, "grade": "A" }
        ],
        "semester_gpa": 3.55
      },
      {
        "semester": "Freshman Spring",
        "year": 2025,
        "courses": [
          { "code": "ENGL 1023", "title": "English Composition II", "credits": 3, "grade": "A-" },
          { "code": "MATH 2854", "title": "Calculus II", "credits": 4, "grade": "B" },
          { "code": "CS 1014", "title": "Foundations of Programming I", "credits": 4, "grade": "A" },
          { "code": "CS 1044", "title": "Foundations of Networking", "credits": 4, "grade": "B+" }
        ],
        "semester_gpa": 3.65
      },
      {
        "semester": "Sophomore Fall",
        "year": 2025,
        "courses": [
          { "code": "PHYS 2054", "title": "General Physics I", "credits": 4, "grade": "B" },
          { "code": "CS 2053", "title": "Foundations of CyberSecurity", "credits": 3, "grade": "A-" },
          { "code": "CS 1024", "title": "Foundations of Programming II", "credits": 4, "grade": "A" },
          { "code": "CS 2003", "title": "Data Structures", "credits": 3, "grade": "B+" }
        ],
        "semester_gpa": 3.55
      }
    ]',
    3.61
); */