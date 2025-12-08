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
    advisorid BIGSERIAL PRIMARY KEY, --REFERENCES users(userid) ON DELETE CASCADE
    advisortype VARCHAR(10)
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
    activestatus BOOLEAN DEFAULT TRUE, 
    dateadvised TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb,
    classes JSONB 
) INHERITS (users);

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
    cumulativegpa NUMERIC(3,2)
);

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
    corecourses JSONB,
    concentrations JSONB
);

CREATE TABLE appointments (
    appointmentid BIGSERIAL PRIMARY KEY, 
    advisorid BIGINT REFERENCES advisor (advisorid) ON DELETE CASCADE, 
    studentid BIGINT REFERENCES student (studentid) ON DELETE CASCADE,
    starttime TIMESTAMP WITH TIME ZONE NOT NULL, 
    endtime TIMESTAMP WITH TIME ZONE NOT NULL,
    appointmentstatus VARCHAR(50) NOT NULL CHECK (appointmentstatus IN ('Scheduled', 'Completed', 'Canceled', 'No-Show')),
    notes TEXT,
    createdat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- INSERTIONS --

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Jake', 'Student', 'jake00@uafs.edu', 4790000000, 'student', 'University of Arkansas - Fort Smith', 3.20, 'B.S. in Computer Science', 'General',
            '', 'Junior', FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP);


INSERT INTO admin (firstname, lastname, email, phonenumber, role, school)
VALUES ('Andrew', 'Appleyard', 'aapply00@uafs.edu', 1112223334, 'admin', 'UAFS');


INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Andrew', 'Mackey', 'amackey00@uafs.edu', 3332226666, 'advisor', 'UAFS');

INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Israel', 'Cuevas', 'icuevas00@uafs.edu', 3332226666, 'advisor', 'UAFS');

INSERT INTO advisor (firstname, lastname, email, phonenumber, role, school)
VALUES ('Brittany', 'Bright', 'bbright00@uafs.edu', 3332226666, 'advisor', 'UAFS');


-- -- userid | firstname | lastname | email | phonenumber | role | school | studentid 
-- -- | gpa | major | majorconcentration | minor | classstanding | financialhold | advisinghold | academichold 
-- -- | registrationstatus | advisingstatus | activestatus | dateadvised 

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Yash', 'Patel', 'ypatel00@uafs.edu', 4448889999, 'student', 'University of Arkansas - Fort Smith', 3.61, 'B.S. in Computer Science', 'General',
             '', 'Sophomore', FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)

VALUES ('Christopher', 'Monterroza', 'cmonte00@uafs.edu', 4448889999, 'student', 'University of Arkansas - Fort Smith', 3.61, 'B.S. in Computer Science', 'Artificial Intelligence',
             'Math', 'Senior', FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, CURRENT_TIMESTAMP);

INSERT INTO student (firstname, lastname, email, phonenumber, role, school, gpa, major, majorconcentration,
            minor, classstanding, financialhold, advisinghold, academichold, registrationstatus, advisingstatus,
            activestatus, dateadvised)
VALUES ('Robert', 'Farrar', 'rfarra00@uafs.edu', 4448889999, 'student', 'University of Arkansas - Fort Smith', 3.61, 'B.S. in Computer Science', 'General',
             'Math', 'Senior', FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP);



--  advisorandstudentid | studentid | advisorid 

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (1, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (2, 1);

INSERT INTO advisor_and_students (studentid, advisorid)
VALUES (3, 2);


INSERT INTO transcript (studentid, program, concentration, year, institution, coursemap, cumulativegpa)
VALUES(
    2,
    'B.S. in Computer Science',
    'General',
    'Sophomore',
    'University of Arkansas - Fort Smith',
    '[
      {
        "semester": "Freshman Fall",
        "year": 2024,
        "courses": [
          { "code": "ENGL 1013", "title": "English Composition I", "credits": 3, "grade": "A" },
          { "code": "MATH 2804", "title": "Calculus I", "credits": 4, "grade": "B" },
          { "code": "CS 1093", "title": "Computer Science Concepts", "credits": 3, "grade": "A" },
          { "code": "FA/HUM/SOCSCI 1103", "title": "Introduction to Humanities", "credits": 3, "grade": "B" },
          { "code": "STEM 1001", "title": "College Prep for STEM Majors", "credits": 1, "grade": "A" }
        ],
        "semester_gpa": 3.55
      },
      {
        "semester": "Freshman Spring",
        "year": 2025,
        "courses": [
          { "code": "ENGL 1023", "title": "English Composition II", "credits": 3, "grade": "A" },
          { "code": "MATH 2854", "title": "Calculus II", "credits": 4, "grade": "B" },
          { "code": "CS 1014", "title": "Foundations of Programming I", "credits": 4, "grade": "A" },
          { "code": "CS 1044", "title": "Foundations of Networking", "credits": 4, "grade": "B" }
        ],
        "semester_gpa": 3.65
      },
      {
        "semester": "Sophomore Fall",
        "year": 2025,
        "courses": [
          { "code": "PHYS 2054", "title": "General Physics I", "credits": 4, "grade": "B" },
          { "code": "CS 2053", "title": "Foundations of CyberSecurity", "credits": 3, "grade": "A" },
          { "code": "CS 1024", "title": "Foundations of Programming II", "credits": 4, "grade": "A" },
          { "code": "CS 2003", "title": "Data Structures", "credits": 3, "grade": "B" }
        ],
        "semester_gpa": 3.55
      }
    ]'::jsonb,
    3.61
);

INSERT INTO transcript (studentid, program, concentration, year, institution, coursemap, cumulativegpa)
VALUES(
    1,
    'B.S. in Computer Science',
    'General',
    'Sophomore',
    'University of Arkansas - Fort Smith',
    '[
      {
        "semester": "Freshman Fall",
        "year": 2024,
        "courses": [
          { "code": "ENGL 1013", "title": "English Composition I", "credits": 3, "grade": "A" },
          { "code": "MATH 2804", "title": "Calculus I", "credits": 4, "grade": "B" },
          { "code": "CS 1093", "title": "Computer Science Concepts", "credits": 3, "grade": "A" },
          { "code": "FA/HUM/SOCSCI 1103", "title": "Introduction to Humanities", "credits": 3, "grade": "B" },
          { "code": "STEM 1001", "title": "College Prep for STEM Majors", "credits": 1, "grade": "A" }
        ],
        "semester_gpa": 3.55
      },
      {
        "semester": "Freshman Spring",
        "year": 2025,
        "courses": [
          { "code": "ENGL 1023", "title": "English Composition II", "credits": 3, "grade": "A" },
          { "code": "MATH 2854", "title": "Calculus II", "credits": 4, "grade": "B" },
          { "code": "CS 1014", "title": "Foundations of Programming I", "credits": 4, "grade": "A" },
          { "code": "CS 1044", "title": "Foundations of Networking", "credits": 4, "grade": "B" }
        ],
        "semester_gpa": 3.65
      },
      {
        "semester": "Sophomore Fall",
        "year": 2025,
        "courses": [
          { "code": "PHYS 2054", "title": "General Physics I", "credits": 4, "grade": "B" },
          { "code": "CS 2053", "title": "Foundations of CyberSecurity", "credits": 3, "grade": "A" },
          { "code": "CS 1024", "title": "Foundations of Programming II", "credits": 4, "grade": "A" },
          { "code": "CS 2003", "title": "Data Structures", "credits": 3, "grade": "B" }
        ],
        "semester_gpa": 3.52
      },
      {
        "semester": "Junior Spring",
        "year": 2025,
        "courses": [
          { "code": "MATH 2443", "title": "Discrete Mathematics I", "credits": 3, "grade": "B+" },
          { "code": "CS 2033", "title": "Algorithms", "credits": 3, "grade": "A" },
          { "code": "CS 3043", "title": "Database Systems", "credits": 3, "grade": "A" },
          { "code": "COMM 1303", "title": "Public Speaking", "credits": 3, "grade": "B" }
        ],
        "semester_gpa": 3.45
      }
    ]'::jsonb,
    3.61
);

INSERT INTO transcript (studentid, program, concentration, year, institution, coursemap, cumulativegpa)
VALUES(
    3,
    'B.S. in Computer Science',
    'General',
    'Sophomore',
    'University of Arkansas - Fort Smith',
    '[
      {
        "semester": "Freshman Fall",
        "year": 2024,
        "courses": [
          { "code": "ENGL 1013", "title": "English Composition I", "credits": 3, "grade": "A" },
          { "code": "MATH 2804", "title": "Calculus I", "credits": 4, "grade": "B" },
          { "code": "CS 1093", "title": "Computer Science Concepts", "credits": 3, "grade": "A" },
          { "code": "FA/HUM/SOCSCI 1103", "title": "Introduction to Humanities", "credits": 3, "grade": "B" },
          { "code": "STEM 1001", "title": "College Prep for STEM Majors", "credits": 1, "grade": "A" }
        ],
        "semester_gpa": 3.55
      },
      {
        "semester": "Freshman Spring",
        "year": 2025,
        "courses": [
          { "code": "ENGL 1023", "title": "English Composition II", "credits": 3, "grade": "A" },
          { "code": "MATH 2854", "title": "Calculus II", "credits": 4, "grade": "B" },
          { "code": "CS 1014", "title": "Foundations of Programming I", "credits": 4, "grade": "A" },
          { "code": "CS 1044", "title": "Foundations of Networking", "credits": 4, "grade": "B" }
        ],
        "semester_gpa": 3.65
      },
      {
        "semester": "Sophomore Fall",
        "year": 2025,
        "courses": [
          { "code": "PHYS 2054", "title": "General Physics I", "credits": 4, "grade": "B" },
          { "code": "CS 2053", "title": "Foundations of CyberSecurity", "credits": 3, "grade": "A" },
          { "code": "CS 1024", "title": "Foundations of Programming II", "credits": 4, "grade": "A" },
          { "code": "CS 2003", "title": "Data Structures", "credits": 3, "grade": "B" }
        ],
        "semester_gpa": 3.55
      }
    ]'::jsonb,
    3.61
);

-- INSERT INTO transcript (studentid, program, concentration, year, institution, coursemap, cumulativegpa) VALUES (36, 'B.S. in Computer Science', 'General', 'Sophomore', 'University of Arkansas - Fort Smith', '[{"semester":"Freshman Fall","year":2024,"courses":[{"code":"ENGL 1013","title":"English Composition I","credits":3,"grade":"A"},{"code":"MATH 2804","title":"Calculus I","credits":4,"grade":"B+"},{"code":"CS 1093","title":"Computer Science Concepts","credits":3,"grade":"A-"},{"code":"FA/HUM/SOCSCI 1103","title":"Introduction to Humanities","credits":3,"grade":"B"},{"code":"STEM 1001","title":"College Prep for STEM Majors","credits":1,"grade":"A"}],"semester_gpa":3.55},{"semester":"Freshman Spring","year":2025,"courses":[{"code":"ENGL 1023","title":"English Composition II","credits":3,"grade":"A-"},{"code":"MATH 2854","title":"Calculus II","credits":4,"grade":"B"},{"code":"CS 1014","title":"Foundations of Programming I","credits":4,"grade":"A"},{"code":"CS 1044","title":"Foundations of Networking","credits":4,"grade":"B+"}],"semester_gpa":3.65},{"semester":"Sophomore Fall","year":2025,"courses":[{"code":"PHYS 2054","title":"General Physics I","credits":4,"grade":"B"},{"code":"CS 2053","title":"Foundations of CyberSecurity","credits":3,"grade":"A-"},{"code":"CS 1024","title":"Foundations of Programming II","credits":4,"grade":"A"},{"code":"CS 2003","title":"Data Structures","credits":3,"grade":"B+"}],"semester_gpa":3.55}]'::jsonb, 3.61);

UPDATE student SET classes = '[
  {"number": "CSCE 20003", "name": "Data Structures"},
  {"number": "CSCE 20303", "name": "Web Systems"},
  {"number": "MATH 26103", "name": "Discrete Mathematics I"},
  {"number": "SPCH 10003", "name": "Intro to Speech Communication"},
  {"number": "PHYS 2064", "name": "General Physics II (Lab Science II)"}
]'::jsonb WHERE studentid = 2;

UPDATE student SET classes = '[
  {"number": "CSCE 20003", "name": "Data Structures"},
  {"number": "CSCE 20303", "name": "Web Systems"},
  {"number": "MATH 26103", "name": "Discrete Mathematics I"},
  {"number": "SPCH 10003", "name": "Intro to Speech Communication"},
  {"number": "PHYS 2064", "name": "General Physics II (Lab Science II)"}
]'::jsonb WHERE studentid = 3;

UPDATE student SET classes = '[
  {"number": "CSCE 20003", "name": "Data Structures"},
  {"number": "CSCE 20303", "name": "Web Systems"},
  {"number": "MATH 26103", "name": "Discrete Mathematics I"},
  {"number": "SPCH 10003", "name": "Intro to Speech Communication"},
  {"number": "PHYS 2064", "name": "General Physics II (Lab Science II)"}
]'::jsonb WHERE studentid = 4;