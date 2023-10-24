from .resource import *


class V2(object):
    def __init__(self, config: Config) -> None:
        self.bp: Bp = Bp(config)
        self.company: Company = Company(config)
        self.contract: Contract = Contract(config)
        self.department: Department = Department(config)
        self.employee: Employee = Employee(config)
        self.employees_bp: EmployeesBp = EmployeesBp(config)
        self.employees_job_data: EmployeesJobData = EmployeesJobData(config)
        self.job: Job = Job(config)
        self.job_change: JobChange = JobChange(config)
        self.job_family: JobFamily = JobFamily(config)
        self.job_level: JobLevel = JobLevel(config)
        self.location: Location = Location(config)
        self.person: Person = Person(config)
        self.pre_hire: PreHire = PreHire(config)
        self.probation: Probation = Probation(config)
        self.probation_assessment: ProbationAssessment = ProbationAssessment(config)
