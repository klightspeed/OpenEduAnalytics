import random
from DataGenUtil import *
import json
from faker import Faker

GENDER = ['Male','Female']
BOOLEAN = [True, False]
OPERATIONAL_STATUS = ['Active','Inactive']
CHARTER_STATUS = ['School Charter', 'Open Enrollment Charter', 'Not a Charter School']
GRADE_LEVEL = ['First Grade','Second Grade','Third Grade','Fourth Grade','Fifth Grade','Sixth Grade','Seventh Grade','Eighth Grade','Ninth Grade','Tenth Grade','Eleventh Grade','Twelfth Grade']
SCHOOL_TYPES = ['High School', 'Middle School', 'Elementary School']
SUBJECT_NAMES = [('Math','Algebra'), ('Math','Geometry'), ('Language','English'), ('History','World History'),
('Science','Biology'), ('Science','Health'), ('Technology',' Programming'), ('Physical Education','Sports'), ('Arts','Music')]


class EdFiDataGenerator:
    def __init__(self,number_students_per_school=100, include_optional_fields=True, school_year='2021', credit_conversion_factor = 2.0, number_of_grades_per_school = 5, is_current_school_year = True, graduation_plans_per_school = 10):
        # Set a seed value in Faker so it generates same values every run.
        self.faker = Faker('en_US')
        Faker.seed(1)

        self.include_optional_fields = include_optional_fields
        self.graduation_plans_per_school = graduation_plans_per_school
        self.school_year = school_year
        self.country = 'United States of America'
        self.number_students_per_school = number_students_per_school
        self.credit_conversion_factor = credit_conversion_factor
        self.number_of_grades_per_school = number_of_grades_per_school
        self.is_current_school_year = is_current_school_year

    def generate_data(self, num_of_schools, writer):
        for _ in range(num_of_schools):
            school_data = self.create_school()
           
            writer.write(f'EdFi/School.json',obj_to_json(school_data))
            writer.write(f'EdFi/Student.json',list_of_dict_to_json(school_data['_Students']))
            writer.write(f'EdFi/StudentSchoolAssociation.json',list_of_dict_to_json(school_data['_StudentAssociation']))
            writer.write(f'EdFi/Course.json',list_of_dict_to_json(school_data['_Courses']))
            writer.write(f'EdFi/Calendar.json',obj_to_json(school_data['_Calendar'])+"\n")

    def create_school(self):
        school_type = random.choice(SCHOOL_TYPES)
        school_name = self.faker.city() + ' ' + school_type
        school = {
            'Id': self.faker.uuid4().replace('-',''),
            'SchoolId': self.faker.random_number(digits=5),
            'NameOfInstitution': school_name,
            'OperationalStatusDescriptor': self.getDescriptorString('OperationalStatusDescriptor',random.choice(OPERATIONAL_STATUS)),
            'ShortNameOfInstitution': ''.join([word[0] for word in school_name.split()]),
            'Website':''.join(['www.',school_name.lower().replace(' ',''),'.com']),
            'AdministrativeFundingControlDescriptor': self.getDescriptorString('AdministrativeFundingControlDescriptor',random.choice(['public', 'private']) + ' School'),
            'CharterStatusDescriptor': self.getDescriptorString('CharterStatusDescriptor',random.choice(CHARTER_STATUS)),
            'SchoolTypeDescriptor': self.getDescriptorString('SchoolTypeDescriptor','Regular'),
            'TitleIPartASchoolDesignationDescriptor': self.getDescriptorString('TitleIPartASchoolDesignationDescriptor','Not A Title I School'),
            'Addresses': self.create_address() if self.include_optional_fields else '',
            'EducationOrganizationCategories':[{'EducationOrganizationCategoryDescriptor': self.getDescriptorString('educationOrganizationCategoryDescriptor','School')}],
            'IdentificationCodes': [
                {
                    'educationOrganizationIdentificationSystemDescriptor': self.getDescriptorString('educationOrganizationIdentificationSystemDescriptor','SEA'),
                    'identificationCode': self.faker.random_number(digits=10)
                }
            ],
            'InstitutionTelephones': self.create_telephones(),
            'InternationalAddresses': [],
            'SchoolCategories': [
                {
                    'SchoolCategoryDescriptor': self.getDescriptorString('SchoolCategoryDescriptor',school_type)
                }
            ],
            'gradeLevels': [
                {'gradeLevelDescriptor': self.getDescriptorString('GradeLevelDescriptor',random.choice(GRADE_LEVEL))} for _ in range(4)
            ]
        }

        school['_SchoolYear'] = self.create_school_year()
        school['_Calendar'] = self.create_calendar(school)
        school['_Students'] = self.create_students()
        school['_Courses'] = self.create_courses(school['SchoolId'],school['Id'],school_name)
        school['_GraduationPlan'] = self.create_graduation_plans(school)
        school['_StudentAssociation'] = self.create_student_school_association(school)

        return school

    def create_students(self):
        students = []
        for _ in range(self.number_students_per_school):
            gender = random.choice(GENDER)
            fname = self.faker.first_name_male() if gender == 'Male' else self.faker.first_name_female()
            students.append({
                'Id': self.faker.uuid4().replace('-',''),
                'StudentUniqueId': self.faker.random_number(digits=5),
                "BirthCity": self.faker.city(),
                "BirthDate": str(self.faker.date_between(start_date='-18y',end_date='-5y')),
                "BirthSexDescriptor": self.getDescriptorString('birthStateAbbreviationDescriptor', gender),
                "FirstName": fname,
                "IdentificationDocuments": [],
                "LastSurname": self.faker.last_name(),
                "OtherNames": [
                    {
                        "OtherNameTypeDescriptor": self.getDescriptorString('otherNameTypeDescriptor','Nickname'),
                        "FirstName": self.faker.first_name_male() if gender == 'Male' else self.faker.first_name_female(),
                        "PersonalTitlePrefix": 'Mr' if gender == 'Male' else 'Ms'
                    }
                ],
                "PersonalIdentificationDocuments": [],
                "PersonalTitlePrefix": 'Mr' if gender == 'Male' else 'Ms',
                "Visas": [],
                "_etag": self.faker.random_number(digits=10)
        })
        return students


    def create_student_school_association(self,school):
        result = []
        graduation_plan_ids = [gp['Id'] for gp in school['_GraduationPlan']]
        for student in school['_Students']:
            result.append({
                'Id': self.faker.uuid4().replace('-',''),
                "GraduationPlanReference": {
                    "EducationOrganizationId": school['SchoolId'],
                    "GraduationPlanTypeDescriptor": "uri://ed-fi.org/GraduationPlanTypeDescriptor#Minimum",
                    "GraduationSchoolYear": self.school_year,
                    "Link": {
                        "rel": "GraduationPlan",
                        "href": '/ed-fi/graduationPlans/{}'.format(random.choice(graduation_plan_ids))
                    }
                },
                "SchoolReference": {
                    "SchoolId": school['SchoolId'],
                    "Link": {
                        "rel": "School",
                        "href": '/ed-fi/schools/{}'.format(school['Id'])
                    }
                },
                "StudentReference": {
                    "StudentUniqueId": student['StudentUniqueId'],
                    "Link": {
                        "rel": "Student",
                        "href": "/ed-fi/students/{}".format(student['Id'])
                    }
                },
                "EntryDate": str(self.faker.date_between(start_date='-5y',end_date='today')),
                "EntryGradeLevelDescriptor": "uri://ed-fi.org/GradeLevelDescriptor#{}".format(random.choice(GRADE_LEVEL)),
                "AlternativeGraduationPlans": [],
                "EducationPlans": [],
                "_etag": self.faker.random_number(digits=10)
            })
        return result

    def create_calendar(self,school):
        return {
            'Id': self.faker.uuid4().replace('-',''),
            'CalendarCode':self.faker.random_number(digits=5),
            "SchoolReference": {
                "SchoolId": school['SchoolId'],
                "Link": {
                    "rel": "School",
                    "href": "/ed-fi/schools/{}".format(school['Id'])
                }
            },
            "SchoolYearTypeReference": {
                "SchoolYear": self.school_year,
                "Link": {
                    "rel": "SchoolYearType",
                    "href": "/ed-fi/schoolYearTypes/{}".format(school['_SchoolYear']['Id'])
                }
            },
            'CalendarTypeDescriptor': self.getDescriptorString('calendarTypeDescriptor','Student Specific'),
            'GradeLevel': []
        }

    def create_address(self):
        address = []
        state = self.faker.state_abbr()
        for n in ['Physical', 'Mailing']:
            address.append({
                'AddressType':n,
                'City':self.faker.city(),
                'PostalCode':self.faker.postcode(),
                'StateAbbreviation':state,
                'StreetNumberName':self.faker.street_name()
            })
        return address

    def create_courses(self,school_id,id,school_name):
        courses = []
        for subject,course_name in SUBJECT_NAMES:
            courses.append({
                "Id": self.faker.uuid4().replace('-',''),
                "EducationOrganizationReference": {
                    "EducationOrganizationId": school_id,
                    "Link": {
                        "rel": "School",
                        "href": "/ed-fi/schools/{}".format(id)
                    }
                },
                "CourseCode": self.faker.random_number(digits=5),
                "AcademicSubjectDescriptor": self.getDescriptorString('academicSubjectDescriptor', subject),
                "CourseDefinedByDescriptor": self.getDescriptorString('CourseDefinedByDescriptor','SEA'),
                "CourseDescription": 'Description about {}'.format(course_name),
                "CourseGPAApplicabilityDescriptor": self.getDescriptorString('CourseGPAApplicabilityDescriptor',random.choice(['Applicable','Not Applicable'])),
                "CourseTitle": course_name,
                "HighSchoolCourseRequirement": random.choice(BOOLEAN),
                "NumberOfParts": 1,
                "CompetencyLevels": [],
                "IdentificationCodes": [
                    {
                        "CourseIdentificationSystemDescriptor": self.getDescriptorString('CourseIdentificationSystemDescriptor','LEA course code'),
                        "CourseCatalogURL": "http://www.{}.edu/coursecatalog".format(school_name.lower().replace(' ','')),
                        "IdentificationCode": '{}-{}'.format(course_name[0:3].upper(),random.choice(range(1,5)))
                    },
                    {
                        "CourseIdentificationSystemDescriptor": self.getDescriptorString('CourseIdentificationSystemDescriptor','State course code'),
                        "IdentificationCode": self.faker.random_number(digits=5)
                    }
                ],
                "LearningObjectives": [],
                "LearningStandards": [
                    {
                        "LearningStandardReference": {
                            "LearningStandardId": self.faker.random_number(digits=5),
                            "Link": {
                                "rel": "LearningStandard",
                                "href": "/ed-fi/learningStandards/{}".format(self.faker.uuid4().replace('-',''))
                            }
                        }
                    }
                ],
                "LevelCharacteristics": [
                    {
                        "CourseLevelCharacteristicDescriptor": self.getDescriptorString('CourseLevelCharacteristicDescriptor','Core Subject')
                    }
                ],
                "OfferedGradeLevels": [],
                "_etag": self.faker.random_number(digits=10)
            })
        return courses


    def create_graduation_plans(self, school):
        graduation_plans = []
        for _ in range(self.graduation_plans_per_school):
            graduation_plans.append({
                'Id': self.faker.uuid4().replace('-',''),
                "EducationOrganizationReference": {
                    "EducationOrganizationId": school['SchoolId'],
                    "link": {
                        "rel": "School",
                        "href": "/ed-fi/schools/{}".format(school['Id'])
                    }
                },
                "GraduationSchoolYearTypeReference": {
                    "SchoolYear": self.school_year,
                    "Link": {
                        "rel": "SchoolYearType",
                        "href": "/ed-fi/schoolYearTypes/{}".format(school['_SchoolYear']['Id'])
                    }
                },
                "GraduationPlanTypeDescriptor": self.getDescriptorString('GraduationPlanTypeDescriptor', random.choice(['Minimum','Recommended'])),
                "TotalRequiredCredits": random.choice(range(20,30)),
                "CreditsByCourses": [],
                "CreditsByCreditCategories": [
                    {
                        "CreditCategoryDescriptor": self.getDescriptorString('CreditCategoryDescriptor','Honors'),
                        "Credits": random.choice(range(5,15))
                    }
                ],
                "CreditsBySubjects": [],
                "RequiredAssessments": [],
                "_etag": self.faker.random_number(digits=10)
            })
        return graduation_plans

    def create_school_year(self):
        return {
            'Id': self.faker.uuid4().replace('-',''),
            'SchoolYear': self.school_year,
            'CurrentSchoolYear': self.is_current_school_year,
            'schoolYearDescription': 'Description about school year',
            '_etag': self.faker.random_number(digits=10)
        }

    def getDescriptorString(self, key, value):
        return "uri://ed-fi.org/{}#{}".format(key,value)

    def create_telephones(self):
        return [
            {
                'InstitutionTelephoneNumberTypeDescriptor': self.getDescriptorString('InstitutionTelephoneNumberTypeDescriptor', _),
                "TelephoneNumber": self.faker.phone_number()
            }
            for _ in ['Fax','Main']
        ]