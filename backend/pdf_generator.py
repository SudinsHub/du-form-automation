from abc import ABC, abstractmethod
from http.client import HTTPException
import traceback
from weasyprint import HTML, CSS
from sqlalchemy.orm import Session
import models
import crud
from jinja2 import Template
import base64
from io import BytesIO


class PDFGenerator(ABC):
    """Abstract base class for PDF generators"""

    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def generate(self, data) -> dict:
        """Generate PDF and return base64 data with filename"""
        pass

    def _generate_pdf_from_html(self, html_content: str, filename: str) -> dict:
        """Common PDF generation logic"""
        try:
            pdf_buffer = BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)

            pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')

            return {
                "pdf_data": pdf_base64,
                "filename": filename
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDF: {str(e)}"
            )


class IndividualPDFGenerator(PDFGenerator):
    """Generator for individual teacher remuneration PDFs"""

    def generate(self, data):
        """Generate individual teacher remuneration PDF"""
        try:
            # Fetch data
            teacher = self.db.query(models.Teacher).filter(
                models.Teacher.id == data.teacher_id
            ).first()
            if not teacher:
                raise HTTPException(status_code=404, detail="Teacher not found")

            semester = self.db.query(models.ExamSemester).filter(
                models.ExamSemester.id == data.exam_semester_id
            ).first()
            if not semester:
                raise HTTPException(status_code=404, detail="Semester not found")

            remuneration_data = crud.get_teacher_remuneration(
                self.db, data.teacher_id, data.exam_semester_id
            )

            chairman = self.db.query(models.Teacher).filter(
                models.Teacher.id == semester.chairman_id
            ).first()

            # HTML Template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Dhaka University Examination Remuneration Bill</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');

                    body {
                        font-family: 'Noto Sans Bengali', 'Kalpurush', Arial, sans-serif;
                        margin: 30px 40px;
                        font-size: 14px;
                        line-height: 1.8;
                        color: #000;
                    }

                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }

                    td {
                        padding: 8px;
                        vertical-align: top;
                    }

                    .header {
                        text-align: center;
                        font-weight: 700;
                        margin-bottom: 10px;
                    }

                    .header-title {
                        font-size: 20px;
                        margin-bottom: 8px;
                    }

                    .header-subtitle {
                        font-size: 12px;
                        line-height: 1.6;
                        margin-bottom: 25px;
                        padding: 0 50px;
                    }

                    .section-title {
                        font-weight: 600;
                        margin-top: 20px;
                        margin-bottom: 10px;
                        font-size: 14px;
                    }

                    .info-row {
                        margin-bottom: 12px;
                        line-height: 1.8;
                    }

                    .item-row {
                        margin-bottom: 8px;
                        padding-left: 20px;
                        line-height: 1.7;
                    }

                    .dotted-line {
                        border-bottom: 1px dotted #000;
                        display: inline-block;
                        min-width: 150px;
                        margin: 0 5px;
                    }

                    .note {
                        font-size: 12px;
                        margin-top: 10px;
                        margin-bottom: 10px;
                        line-height: 1.7;
                        padding: 0 10px;
                    }

                    .signature-section {
                        margin-top: 40px;
                        display: flex;
                        justify-content: space-between;
                    }

                    .signature-box {
                        text-align: center;
                        width: 45%;
                    }

                    .signature-line {
                        border-top: 1px solid #000;
                        margin-bottom: 8px;
                        padding-top: 50px;
                    }

                    .filled-data {
                        font-weight: 600;
                    }

                    .calculation-table {
                        margin-top: 25px;
                        margin-bottom: 25px;
                        border: 1px solid #000;
                        width: 100%;
                    }

                    .calculation-table th, .calculation-table td {
                        border: 1px solid #000;
                        padding: 10px 8px;
                        text-align: center;
                        font-size: 13px;
                    }

                    .calculation-table th {
                        background-color: #f5f5f5;
                        font-weight: 600;
                    }

                    .calculation-table td:nth-child(2) {
                        text-align: left;
                        padding-left: 15px;
                    }

                    .bill-serial {
                        text-align: right;
                        margin-bottom: 15px;
                        font-size: 13px;
                    }

                    .intro-text {
                        margin-top: 25px;
                        margin-bottom: 20px;
                        line-height: 1.8;
                        text-align: justify;
                    }

                    .payment-row {
                        margin-top: 25px;
                        margin-bottom: 15px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }

                    .payment-item {
                        display: flex;
                        align-items: center;
                    }

                    .footer-signatures {
                        margin-top: 35px;
                        display: flex;
                        justify-content: space-between;
                        gap: 20px;
                    }

                    .footer-sig-box {
                        text-align: center;
                        flex: 1;
                    }

                    .footer-note {
                        margin-top: 30px;
                        font-size: 12px;
                    }

                    .controller-signature {
                        margin-top: 20px;
                        text-align: right;
                    }

                    .controller-signature .signature-line {
                        width: 200px;
                        float: right;
                        margin-bottom: 8px;
                    }

                    .clear {
                        clear: both;
                    }
                </style>
            </head>
            <body>
                <div class="bill-serial">বিলের ক্রমিক নং: {{ bill_serial }}</div>

                <div class="header header-title">ঢাকা বিশ্ববিদ্যালয়</div>

                <div class="header header-subtitle">
                    (পরীক্ষার ফল প্রকাশের এক বৎসরের মধ্যে নির্দিষ্ট বিভাগীয় পরীক্ষা পরিষদের সভাপতির মাধ্যমে পরীক্ষা নিয়ন্ত্রকের অফিসে পারিশ্রমিকের বিল পেশ করিতে হইবে)।
                </div>

                <div class="info-row">
                    পরীক্ষকের নাম: জনাব/ডঃ/অধ্যাপক <span class="filled-data">{{ teacher.name }}</span>
                </div>

                <div class="info-row">
                    পদবী সহকারে ঠিকানা: <span class="filled-data">{{ teacher.designation }}, {{ teacher.department }}, University of Dhaka</span>
                </div>

                <div class="intro-text">
                    <span class="filled-data">{{ semester.year }}</span> সনের পরীক্ষা সমূহের প্রশ্নপত্র প্রণয়ন, সমন্বয় সাধন এবং উত্তরপত্র মূল্যায়ন ইত্যাদির জন্য আমার পারিশ্রমিক দাবীসমূহ নিম্নে সন্নিবেশিত হইল:-
                </div>

                {% if question_preparations %}
                <div class="section-title">(১) প্রশ্নপত্র প্রণয়ন:</div>
                {% for prep in question_preparations %}
                <div class="item-row">
                    ({{ loop.index }}) একটি <span class="filled-data">{{ prep.section_type }}</span> <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ prep.course.course_code }}</span> বিষয় <span class="filled-data">{{ prep.course.course_title }}</span> পত্র/কোর্স
                </div>
                {% endfor %}
                {% endif %}

                {% if question_moderations %}
                <div class="section-title">(২) প্রশ্নপত্র সমন্বয় সাধন:</div>
                {% for mod in question_moderations %}
                <div class="item-row">
                    <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ mod.course.course_code }}</span> বিষয় <span class="filled-data">{{ mod.question_count }}</span>টা প্রশ্নপত্র <span class="filled-data">{{ mod.team_member_count }}</span> জন সদস্য
                </div>
                {% endfor %}
                {% endif %}

                {% if script_evaluations %}
                <div class="section-title">(৩) উত্তরপত্র মূল্যায়ন করা:</div>
                {% for eval in script_evaluations %}
                <div class="item-row">
                    ({{ loop.index }}) <span class="filled-data">{{ eval.script_type }}</span> খাতা <span class="filled-data">{{ eval.script_count }}</span> জন সদস্য <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ eval.course.course_code }}</span> বিষয় <span class="filled-data">{{ eval.course.course_title }}</span> পত্র/কোর্স
                </div>
                {% endfor %}
                {% endif %}

                {% if practical_exams %}
                <div class="section-title">(৪) ব্যবহারিক পরীক্ষা:</div>
                {% for practical in practical_exams %}
                <div class="item-row">
                    {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ practical.course.course_code }}</span> কেন্দ্রের <span class="filled-data">{{ practical.student_count }}</span> জন পরীক্ষার্থীর জন্য <span class="filled-data">{{ practical.course.course_title }}</span> বিষয়ে <span class="filled-data">{{ practical.day_count }}</span> দিন
                </div>
                {% endfor %}
                {% endif %}

                {% if viva_exams %}
                <div class="section-title">(৫) মৌখিক পরীক্ষা:</div>
                {% for viva in viva_exams %}
                <div class="item-row">
                    {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ viva.course.course_title }}</span> বিষয়ে কেন্দ্রের <span class="filled-data">{{ viva.student_count }}</span> জন পরীক্ষার্থীর জন্য
                </div>
                {% endfor %}
                {% endif %}

                {% if tabulations %}
                <div class="section-title">(৬) পরীক্ষার ফল সন্নিবেশকরণ:</div>
                {% for tab in tabulations %}
                <div class="item-row">
                    {{ semester.year }} সনের <span class="filled-data">{{ tab.course.course_title }}</span> বিষয়ে <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ tab.student_count }}</span> জন পরীক্ষার্থীর জন্য
                </div>
                {% endfor %}
                {% endif %}

                {% if answer_sheet_reviews %}
                <div class="section-title">(৭) উত্তরপত্র নিরীক্ষা:</div>
                {% for review in answer_sheet_reviews %}
                <div class="item-row">
                    {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ review.course.course_title }}</span> বিষয়ের <span class="filled-data">{{ review.answer_sheet_count }}</span> উত্তরপত্র নিরীক্ষা
                </div>
                {% endfor %}
                {% endif %}

                {% if other_remunerations %}
                <div class="section-title">অন্যান্য:</div>
                {% for other in other_remunerations %}
                <div class="item-row">
                    <span class="filled-data">{{ other.remuneration_type }}</span>: <span class="filled-data">{{ other.details }}</span>
                    {% if other.page_count %} - <span class="filled-data">{{ other.page_count }}</span> পৃষ্ঠা{% endif %}
                </div>
                {% endfor %}
                {% endif %}

                <div class="section-title">(৮) ডাক মাশুল ও সংশ্লিষ্ট অন্যান্য বিবিধ খরচ:-</div>
                <div class="note">
                    (ডাক মাশুলের এবং সংশ্লিষ্ট অন্যান্য বিবিধ খরচের রশিদ বিলের সহিত সংযুক্ত না থাকিলে উহা পরিশোধযোগ্য বলিয়া গণ্য হইবে না)।
                </div>
                <div class="note">
                    বিঃ দ্রঃ-৮ নং ক্রমানুসারে বিবিধ খরচের ভাউচার (পোষ্টাল রশিদ ও ক্যাশমেমো) এর গায়ে পরীক্ষকের স্বাক্ষর থাকা প্রয়োজন।
                </div>

                <!-- Payment Calculation Table -->
                <div class="section-title" style="margin-top: 35px;">সম্মানীর হিসাব:</div>
                <table class="calculation-table">
                    <thead>
                        <tr>
                            <th style="width: 10%;">ক্রমিক</th>
                            <th style="width: 45%;">কার্যক্রমের বিবরণ</th>
                            <th style="width: 15%;">পরিমাণ</th>
                            <th style="width: 15%;">হার</th>
                            <th style="width: 15%;">মোট টাকা</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>১</td><td>প্রশ্নপত্র প্রণয়ন</td><td></td><td></td><td></td></tr>
                        <tr><td>২</td><td>প্রশ্নপত্র সমন্বয় সাধন</td><td></td><td></td><td></td></tr>
                        <tr><td>৩</td><td>উত্তরপত্র মূল্যায়ন</td><td></td><td></td><td></td></tr>
                        <tr><td>৪</td><td>ব্যবহারিক পরীক্ষা</td><td></td><td></td><td></td></tr>
                        <tr><td>৫</td><td>মৌখিক পরীক্ষা</td><td></td><td></td><td></td></tr>
                        <tr><td>৬</td><td>ফল সন্নিবেশকরণ</td><td></td><td></td><td></td></tr>
                        <tr><td>৭</td><td>উত্তরপত্র নিরীক্ষা</td><td></td><td></td><td></td></tr>
                        <tr><td>৮</td><td>অন্যান্য</td><td></td><td></td><td></td></tr>
                        <tr style="font-weight: 600;">
                            <td colspan="4" style="text-align: right; padding-right: 15px;">সর্বমোট =</td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>

                <div class="section-title">
                    (৯) প্রত্যয়ন করা যাইতেছে যে অত্র বিলের টাকা পূর্বে গ্রহণ করা হয় নাই।
                </div>

                <div class="payment-row">
                    <div class="payment-item">
                        মোট টাকা: <span class="dotted-line"></span>
                    </div>
                    <div class="payment-item">
                        তারিখ: <span class="filled-data">{{ current_date }}</span>
                    </div>
                </div>

                <div class="signature-section">
                    <div class="signature-box">
                        <div class="signature-line"></div>
                        <div>প্রতি স্বাক্ষর</div>
                        <div>পরীক্ষা পরিষদের সভাপতি</div>
                        <div style="margin-top: 8px;"><span class="filled-data">{{ chairman.name }}</span></div>
                    </div>
                    <div class="signature-box">
                        <div class="signature-line"></div>
                        <div>পরীক্ষক/নিরীক্ষক/সন্নিবেশকের স্বাক্ষর</div>
                        <div style="margin-top: 8px;">বিভাগ: <span class="filled-data">{{ teacher.department }}</span></div>
                        <div>বর্তমান ঠিকানা: <span class="filled-data">{{ teacher.department }}, University of Dhaka</span></div>
                    </div>
                </div>

                <div style="margin-top: 30px; line-height: 1.8;">
                    কে (অংকে) টাকা <span class="dotted-line"></span> পয়সা <span class="dotted-line"></span> ''মাত্র দেওয়া যাইতে পারে।
                </div>

                <div class="footer-signatures">
                    <div class="footer-sig-box">
                        <div class="signature-line"></div>
                        <div>পরীক্ষক/নিরীক্ষক/সন্নিবেশকের স্বাক্ষর</div>
                    </div>
                    <div class="footer-sig-box">
                        <div class="signature-line"></div>
                        <div>তারিখ</div>
                    </div>
                    <div class="footer-sig-box">
                        <div class="signature-line"></div>
                        <div>(বিলে উল্লেখিত সমুদয় টাকা বুঝিয়া পাইলাম)</div>
                        <div style="margin-top: 5px;">স্বাক্ষর</div>
                    </div>
                </div>

                <div class="footer-note">
                    বিঃ দ্রঃ- (ক) ২০০.০০ টাকার উর্ধে দাবী রাজস্ব টিকিট ব্যতীত পরিশোধ করা যাইবে না।
                </div>

                <div class="controller-signature">
                    <div class="signature-line"></div>
                    <div>পরীক্ষা উপ-নিয়ন্ত্রক</div>
                    <div>ঢাকা বিশ্ববিদ্যালয়।</div>
                </div>

                <div class="footer-note clear">
                    (খ) পরীক্ষক সরকারী চাকুরীয়া হইলে যথাযথ কর্মকর্তার অনুমতি ব্যতিরেকে দাবী পরিশোধ করা হইবে না।
                </div>
            </body>
            </html>
            """

            template = Template(html_template)

            html_content = template.render(
                teacher=teacher,
                semester=semester,
                chairman=chairman,
                question_preparations=remuneration_data.get('question_preparations', []),
                question_moderations=remuneration_data.get('question_moderations', []),
                script_evaluations=remuneration_data.get('script_evaluations', []),
                practical_exams=remuneration_data.get('practical_exams', []),
                viva_exams=remuneration_data.get('viva_exams', []),
                tabulations=remuneration_data.get('tabulations', []),
                answer_sheet_reviews=remuneration_data.get('answer_sheet_reviews', []),
                other_remunerations=remuneration_data.get('other_remunerations', []),
                current_date="২০২৫-০১-০৭",
                bill_serial="001"
            )

            filename = f"remuneration_bill_{teacher.name}_{semester.year}_{semester.semester_name}.pdf"
            return self._generate_pdf_from_html(html_content, filename)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate individual PDF: {str(e)}"
            )


class CumulativePDFGenerator(PDFGenerator):
    """Generator for cumulative remuneration report PDFs"""

    def generate(self, data):
        """Generate cumulative remuneration report PDF"""
        print("[CumulativePDFGenerator] Started PDF generation...")

        try:
            print("[CumulativePDFGenerator] Fetching semester info...")
            semester = self.db.query(models.ExamSemester).filter(
                models.ExamSemester.id == data.exam_semester_id
            ).first()
            if not semester:
                raise HTTPException(status_code=404, detail="Semester not found")

            print("[CumulativePDFGenerator] Fetching cumulative report...")
            report_data = crud.get_cumulative_report(self.db, data.exam_semester_id)

            print("[CumulativePDFGenerator] Fetching all courses...")
            all_courses = {course.course_code: course for course in self.db.query(models.Course).all()}

            # HTML Template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Cumulative Remuneration Report</title>
                <style>
                    body { 
                        font-family: 'Arial', sans-serif; 
                        margin: 10px 10px 10px 5px;  /* top right bottom left */
                        font-size: 10px; 
                    }
                    table { 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 10px;
                        font-size: 8px;  /* Make table text smaller if needed */
                    }
                    th, td { 
                        border: 1px solid #000; 
                        padding: 3px;  /* Reduced padding */
                        text-align: left; 
                        vertical-align: top; 
                        word-wrap: break-word;  /* Allow text to wrap */
                    }
                    th { 
                        background-color: #f0f0f0; 
                        font-weight: bold; 
                    }
                    .header { 
                        text-align: center; 
                        font-weight: bold; 
                        margin-bottom: 15px; 
                    }
                    .subheader { 
                        text-align: center; 
                        margin-bottom: 10px; 
                    }
                    .section-title { 
                        font-weight: bold; 
                        margin-top: 10px; 
                        margin-bottom: 5px; 
                    }
                    .signature { 
                        margin-top: 50px; 
                        text-align: right; 
                    }
                    .signature div { 
                        border-top: 1px solid #000; 
                        width: 250px; 
                        margin-left: auto; 
                        text-align: center; 
                        padding-top: 5px; 
                    }
                    

                </style>
            </head>
            <body>
                <div class="header">
                    <h2>{{ semester.semester_name }} Examination {{ semester.year }}</h2>
                    <h3>Department of Computer Science and Engineering</h3>
                    <h3>University of Dhaka</h3>
                    <p>Bill Statement</p>
                    <p>Date of Submission of Bill: {{ "____________" }}</p>
                    <p>Exam started on: {{ semester.exam_start_date.strftime('%d %B, %Y') if semester.exam_start_date else 'N/A' }}</p>
                    <p>Exam ended on: {{ semester.exam_end_date.strftime('%d %B, %Y') if semester.exam_end_date else 'N/A' }}</p>
                    <p>Result Published on: {{ semester.result_publish_date.strftime('%d %B, %Y') if semester.result_publish_date else 'N/A' }}</p>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Name and Address of the Examiner</th>
                            <th>Code Course</th>
                            <th>Moderation Setter Question</th>
                            <th>Preparation Printing</th>
                            <th>Scripts Evaluation (Final/Incourse/Assignment/Practical)</th>
                            <th>Script Evaluation Practical</th>
                            <th>Tabulation (Students)</th>
                            <th>Honorarium Total / (Chair/Member)</th>
                            <th>Committee Member</th>
                            <th>Stencil (Pages)</th>
                            <th>Answer Sheet Review</th>
                            <th>Other Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in report_data %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>
                                {{ item.teacher.name }},<br>
                                {{ item.teacher.designation }}. Dept. of {{ item.teacher.department }}, DU
                            </td>
                            <td>
                                {# List all course codes for any activity #}
                                {% for qp in item.details.question_preparations %}{{ all_courses[qp.course_code].course_code if qp.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for qm in item.details.question_moderations %}{{ all_courses[qm.course_code].course_code if qm.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for se in item.details.script_evaluations %}{{ all_courses[se.course_code].course_code if se.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for pe in item.details.practical_exams %}{{ all_courses[pe.course_code].course_code if pe.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for ve in item.details.viva_exams %}{{ all_courses[ve.course_code].course_code if ve.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for tab in item.details.tabulations %}{{ all_courses[tab.course_code].course_code if tab.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                                {% for asr in item.details.answer_sheet_reviews %}{{ all_courses[asr.course_code].course_code if asr.course_code in all_courses else 'N/A' }}<br>{% endfor %}
                            </td>
                            <td>
                                {% for qm in item.details.question_moderations %}
                                    {% if qm.team_member_count == 1 %}1st Examiner{% elif qm.team_member_count == 2 %}2nd Examiner{% elif qm.team_member_count == 3 %}3rd Examiner{% endif %}<br>
                                    {{ qm.question_count }} Sets<br>
                                {% endfor %}
                            </td>
                            <td>
                                {% for or_item in item.details.other_remunerations %}
                                    {% if or_item.remuneration_type == 'Question Preparation and Printing' %}
                                        {{ or_item.details }}<br>
                                        {% if or_item.page_count %}({{ or_item.page_count }} Pages){% endif %}<br>
                                    {% endif %}
                                {% endfor %}
                            </td>
                            <td>
                                {% for se in item.details.script_evaluations %}
                                    {% if se.script_type == 'Final' %}{{ se.script_count }} Final<br>{% endif %}
                                    {% if se.script_type == 'Incourse' %}{{ se.script_count }} Incourse<br>{% endif %}
                                    {% if se.script_type == 'Assignment' %}{{ se.script_count }} Assignment<br>{% endif %}
                                {% endfor %}
                            </td>
                            <td>
                                {% for pe in item.details.practical_exams %}
                                    {{ pe.day_count }} Days ({{ pe.student_count }} Students)<br>
                                {% endfor %}
                            </td>
                            <td>
                                {% for tab in item.details.tabulations %}
                                    {{ tab.student_count }}<br>
                                {% endfor %}
                            </td>
                            <td>
                                {% for or_item in item.details.other_remunerations %}
                                    {% if or_item.remuneration_type == 'Exam Committee Honorium' %}
                                        {{ or_item.details }}<br>
                                    {% endif %}
                                {% endfor %}
                            </td>
                            <td>
                                {% for or_item in item.details.other_remunerations %}
                                    {% if or_item.remuneration_type == 'Exam Committee Honorium' %}
                                        {% if 'Member' in or_item.details %}Member{% elif 'Chair' in or_item.details %}Chair{% endif %}
                                    {% endif %}
                                {% endfor %}
                            </td>
                            <td>
                                {% for or_item in item.details.other_remunerations %}
                                    {% if or_item.remuneration_type == 'Stencil' %}
                                        {{ or_item.page_count }} Pages<br>
                                    {% endif %}
                                {% endfor %}
                            </td>
                            <td>
                               {% for asr in item.details.answer_sheet_reviews %}
                                    {{ all_courses[asr.course_code].course_code if asr.course_code in all_courses else 'N/A' }} ({{ asr.answer_sheet_count }} Answer Sheets)<br>
                                {% endfor %}
                            </td>
                            <td>
                                {% for or_item in item.details.other_remunerations %}
                                    {# Display other remuneration types not specifically handled in their own columns #}
                                    {% if or_item.remuneration_type not in ['Exam Committee Honorium', 'Stencil', 'Question Preparation and Printing'] %}
                                        {{ or_item.remuneration_type }}: {{ or_item.details }}
                                        {% if or_item.page_count %}({{ or_item.page_count }} Pages){% endif %}<br>
                                    {% endif %}
                                {% endfor %}
                                {% for ve in item.details.viva_exams %}
                                    Viva Exam: {{ all_courses[ve.course_code].course_code if ve.course_code in all_courses else 'N/A' }} ({{ ve.student_count }} Students)<br>
                                {% endfor %}
 
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

                <div class="signature">
                    <p>Mobile No. of the Exam Committee Chairman: {{ chairman.mobile_no if chairman.mobile_no else '' }}</p>
                    <div>
                        ({{ chairman.name if chairman else '' }})<br>
                        {{ chairman.designation if chairman else '' }}, Chairman, {{ semester.semester_name }} Examination Committee, {{ semester.year }}<br>
                        Department of Computer Science & Engineering,<br>
                        University of Dhaka<br>
                        সভাপতি<br>
                        পরীক্ষা কমিটি,<br>
                        বর্ষ বি, এসসি, (অনাস।)<br>
                        কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং <br>
                        ঢাকা বিশ্ববিদ্যালয়
                    </div>
                </div>
            </body>
            </html>
            """

            template = Template(html_template)

            print("[CumulativePDFGenerator] Fetching chairman info...")
            chairman = self.db.query(models.Teacher).filter(
                models.Teacher.id == semester.chairman_id
            ).first()

            print("[CumulativePDFGenerator] Rendering HTML...")
            html_content = template.render(
                semester=semester,
                chairman=chairman,
                report_data=report_data,
                all_courses=all_courses
            )

            print("[CumulativePDFGenerator] Generating PDF...")
            filename = f"cumulative_report_{semester.year}_{semester.semester_name}.pdf"
            return self._generate_pdf_from_html(html_content, filename)

        except HTTPException:
            raise
        except Exception as e:
            print("[CumulativePDFGenerator] ERROR:", e)
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate cumulative PDF: {str(e)}"
            )


class PDFGeneratorFactory:
    """Factory for creating PDF generators"""

    @staticmethod
    def create_generator(generator_type: str, db: Session) -> PDFGenerator:
        """Create a PDF generator based on type"""
        if generator_type == "individual":
            return IndividualPDFGenerator(db)
        elif generator_type == "cumulative":
            return CumulativePDFGenerator(db)
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")


# # Legacy functions for backward compatibility (deprecated)
# def generate_individual_pdf(db: Session, data):
#     """Legacy function - use PDFGeneratorFactory instead"""
#     generator = PDFGeneratorFactory.create_generator("individual", db)
#     return generator.generate(data)


# def generate_cumulative_pdf(db: Session, data):
#     """Legacy function - use PDFGeneratorFactory instead"""
#     generator = PDFGeneratorFactory.create_generator("cumulative", db)
#     return generator.generate(data)
