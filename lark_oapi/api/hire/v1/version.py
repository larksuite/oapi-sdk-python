from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.advertisement: Advertisement = Advertisement(config)
        self.agency: Agency = Agency(config)
        self.application: Application = Application(config)
        self.application_interview: ApplicationInterview = ApplicationInterview(config)
        self.attachment: Attachment = Attachment(config)
        self.background_check_order: BackgroundCheckOrder = BackgroundCheckOrder(config)
        self.diversity_inclusion: DiversityInclusion = DiversityInclusion(config)
        self.eco_account: EcoAccount = EcoAccount(config)
        self.eco_account_custom_field: EcoAccountCustomField = EcoAccountCustomField(config)
        self.eco_background_check: EcoBackgroundCheck = EcoBackgroundCheck(config)
        self.eco_background_check_custom_field: EcoBackgroundCheckCustomField = EcoBackgroundCheckCustomField(config)
        self.eco_background_check_package: EcoBackgroundCheckPackage = EcoBackgroundCheckPackage(config)
        self.eco_exam: EcoExam = EcoExam(config)
        self.eco_exam_paper: EcoExamPaper = EcoExamPaper(config)
        self.ehr_import_task: EhrImportTask = EhrImportTask(config)
        self.ehr_import_task_for_internship_offer: EhrImportTaskForInternshipOffer = EhrImportTaskForInternshipOffer(
            config)
        self.employee: Employee = Employee(config)
        self.evaluation: Evaluation = Evaluation(config)
        self.evaluation_task: EvaluationTask = EvaluationTask(config)
        self.exam: Exam = Exam(config)
        self.exam_marking_task: ExamMarkingTask = ExamMarkingTask(config)
        self.external_application: ExternalApplication = ExternalApplication(config)
        self.external_background_check: ExternalBackgroundCheck = ExternalBackgroundCheck(config)
        self.external_interview: ExternalInterview = ExternalInterview(config)
        self.external_interview_assessment: ExternalInterviewAssessment = ExternalInterviewAssessment(config)
        self.external_referral_reward: ExternalReferralReward = ExternalReferralReward(config)
        self.interview: Interview = Interview(config)
        self.interview_feedback_form: InterviewFeedbackForm = InterviewFeedbackForm(config)
        self.interview_record: InterviewRecord = InterviewRecord(config)
        self.interview_record_attachment: InterviewRecordAttachment = InterviewRecordAttachment(config)
        self.interview_registration_schema: InterviewRegistrationSchema = InterviewRegistrationSchema(config)
        self.interview_round_type: InterviewRoundType = InterviewRoundType(config)
        self.interview_task: InterviewTask = InterviewTask(config)
        self.interviewer: Interviewer = Interviewer(config)
        self.job: Job = Job(config)
        self.job_manager: JobManager = JobManager(config)
        self.job_function: JobFunction = JobFunction(config)
        self.job_process: JobProcess = JobProcess(config)
        self.job_publish_record: JobPublishRecord = JobPublishRecord(config)
        self.job_requirement: JobRequirement = JobRequirement(config)
        self.job_requirement_schema: JobRequirementSchema = JobRequirementSchema(config)
        self.job_schema: JobSchema = JobSchema(config)
        self.job_type: JobType = JobType(config)
        self.location: Location = Location(config)
        self.minutes: Minutes = Minutes(config)
        self.note: Note = Note(config)
        self.offer: Offer = Offer(config)
        self.offer_application_form: OfferApplicationForm = OfferApplicationForm(config)
        self.offer_custom_field: OfferCustomField = OfferCustomField(config)
        self.offer_schema: OfferSchema = OfferSchema(config)
        self.questionnaire: Questionnaire = Questionnaire(config)
        self.referral: Referral = Referral(config)
        self.referral_account: ReferralAccount = ReferralAccount(config)
        self.referral_website_job_post: ReferralWebsiteJobPost = ReferralWebsiteJobPost(config)
        self.registration_schema: RegistrationSchema = RegistrationSchema(config)
        self.resume_source: ResumeSource = ResumeSource(config)
        self.role: Role = Role(config)
        self.subject: Subject = Subject(config)
        self.talent: Talent = Talent(config)
        self.talent_external_info: TalentExternalInfo = TalentExternalInfo(config)
        self.talent_folder: TalentFolder = TalentFolder(config)
        self.talent_object: TalentObject = TalentObject(config)
        self.talent_operation_log: TalentOperationLog = TalentOperationLog(config)
        self.talent_pool: TalentPool = TalentPool(config)
        self.termination_reason: TerminationReason = TerminationReason(config)
        self.test: Test = Test(config)
        self.todo: Todo = Todo(config)
        self.tripartite_agreement: TripartiteAgreement = TripartiteAgreement(config)
        self.user_role: UserRole = UserRole(config)
        self.website: Website = Website(config)
        self.website_channel: WebsiteChannel = WebsiteChannel(config)
        self.website_delivery: WebsiteDelivery = WebsiteDelivery(config)
        self.website_delivery_task: WebsiteDeliveryTask = WebsiteDeliveryTask(config)
        self.website_job_post: WebsiteJobPost = WebsiteJobPost(config)
        self.website_site_user: WebsiteSiteUser = WebsiteSiteUser(config)
