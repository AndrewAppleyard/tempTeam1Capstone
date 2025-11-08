import json

#TODO
#API endpoints
#RAG system
#userclass
#don't need to do the same for email just a grab and check then update if
#condition true else send back email telling them why
def generate_schedule():

    data = '''{
    "student_id": "ua104",
    "name": "Andrew Appleyard",
    "semester": "Spring 2026",
    "courses": [
        {
        "code": "CSCE 30003-0001",
        "title": "Distributed Systems",
        "credits": 3,
        "delivery_mode": "In-Person",
        "meeting_pattern": "Monday/Wednesday | 2:00 PM - 3:15 PM",
        "location": "UAFS | Baldor Tech Computer Lab-BD147",
        "instructor": "Israel B Cuevas"
        },
        {
        "code": "CSCE 30503-0001",
        "title": "Operating Systems",
        "credits": 3,
        "delivery_mode": "In-Person",
        "meeting_pattern": "Tuesday/Thursday | 2:00 PM - 3:15 PM",
        "location": "UAFS | Baldor Tech Computer Lab-BD144",
        "instructor": "Brian Paul McLaughlan"
        },
        {
        "code": "CSCE 31103-0001",
        "title": "Artificial Intelligence",
        "credits": 3,
        "delivery_mode": "In-Person",
        "meeting_pattern": "Tuesday/Thursday | 9:30 AM - 10:45 AM",
        "location": "UAFS | Baldor Tech Computer Lab-BD147",
        "instructor": "Israel B Cuevas"
        },
        {
        "code": "GEN_ED FA/Hum/SocSci",
        "title": "Fine Arts/Humanities/Social Sciences requirement",
        "credits": 3,
        "delivery_mode": "Online/Variable",
        "meeting_pattern": "To Be Determined",
        "location": "UAFS",
        "instructor": "TBD"
        },
        {
        "code": "CSCE 43733-9001",
        "title": "Information Retrieval",
        "credits": 3,
        "delivery_mode": "In-Person",
        "meeting_pattern": "Tuesday/Thursday | 6:50 PM - 8:05 PM",
        "location": "UAFS | Baldor Tech Computer Lab-BD147",
        "instructor": "Andrew Lee Mackey"
        }
        ]
        }'''
    
    schedule = json.loads(data)
    #add to database instead of return and then pull from database to display
    return schedule