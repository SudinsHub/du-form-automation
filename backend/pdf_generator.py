from weasyprint import HTML, CSS
from sqlalchemy.orm import Session
import models
import crud
from jinja2 import Template
import base64
from io import BytesIO

def generate_individual_pdf(db: Session, data):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == data.teacher_id).first()
    semester = db.query(models.ExamSemester).filter(models.ExamSemester.id == data.exam_semester_id).first()
    remuneration_data = crud.get_teacher_remuneration(db, data.teacher_id, data.exam_semester_id)
    
    print("Got remuneration_data :", remuneration_data)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dhaka University Examination Remuneration Bill</title>
        <style>
            body { font-family: 'Arial', sans-serif; margin: 20px; font-size: 12px; }
            table { width: 100%; border-collapse: collapse; }
            td { padding: 5px; vertical-align: top; }
            .header { text-align: center; font-weight: bold; }
            .section-title { font-weight: bold; margin-top: 15px; }
            .dotted-line { border-bottom: 1px dotted #000; flex-grow: 1; }
            .flex-container { display: flex; align-items: baseline; }
            .note { font-size: 0.9em; margin-top: 10px; }
            .signature-line { margin-top: 40px; border-top: 1px solid #000; text-align: center; width: 30%; }
            .filled-data { font-weight: bold; }
            .calculation-table { margin-top: 20px; border: 1px solid #000; }
            .calculation-table th, .calculation-table td { border: 1px solid #000; padding: 8px; text-align: center; }
            .calculation-table th { background-color: #f0f0f0; }
        </style>
    </head>
    <body>
        <div style="text-align: right;">বিলের ক্রমিক নং: {{ bill_serial }}</div>
        <h2 class="header">ঢাকা বিশ্ববিদ্যালয়</h2>
        <div class="header" style="font-size: 0.9em;">(পরীক্ষার ফল প্রকাশের এক বৎসরের মধ্যে নির্দিষ্ট বিভাগীয় পরীক্ষা পরিষদের সভাপতির মাধ্যমে পরীক্ষা নিয়ন্ত্রকের অফিসে পারিশ্রমিকের বিল পেশ করিতে হইবে)।</div>
        
        <div style="margin-top: 20px;">
            <div class="flex-container">
                পরীক্ষকের নাম: জনাব/ডঃ/অধ্যাপক <span class="filled-data">{{ teacher.name }}</span>
            </div>
            <div class="flex-container" style="margin-top: 5px;">
                পদবী সহকারে ঠিকানা <span class="filled-data">{{ teacher.designation }}, {{ teacher.address }}</span>
            </div>
        </div>
        
        <div style="margin-top: 15px;">
            <span class="filled-data">{{ semester.year }}</span> সনের পরীক্ষা সমূহের প্রশ্নপত্র প্রণয়ন, সমন্বয় সাধন এবং উত্তরপত্র মূল্যায়ন ইত্যাদির জন্য আমার পারিশ্রমিক দাবীসমূহ নিম্নে সন্নিবেশিত হইল:-
        </div>
        
        {% if question_preparations %}
        <div class="section-title">(১) প্রশ্নপত্র প্রণয়ন:</div>
        {% for prep in question_preparations %}
        <div class="flex-container">
            ({{ loop.index0 + 1 }}) একটি <span class="filled-data">{{ prep.section_type }}</span> <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ prep.course.course_code }}</span> বিষয় <span class="filled-data">{{ prep.course.course_title }}</span> পত্র/কোর্স
        </div>
        {% endfor %}
        {% endif %}
        
        {% if question_moderations %}
        <div class="section-title">(২) প্রশ্নপত্র সমন্বয় সাধন:</div>
        {% for mod in question_moderations %}
        <div class="flex-container">
            <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ mod.course.course_code }}</span> বিষয় <span class="filled-data">{{ mod.question_count }}</span>টা প্রশ্নপত্র <span class="filled-data">{{ mod.team_member_count }}</span> জন সদস্য
        </div>
        {% endfor %}
        {% endif %}
        
        {% if script_evaluations %}
        <div class="section-title">(৩) উত্তরপত্র মূল্যায়ন করা:</div>
        {% for eval in script_evaluations %}
        <div class="flex-container">
            ({{ loop.index0 + 1 }}) <span class="filled-data">{{ eval.script_type }}</span> খাতা <span class="filled-data">{{ eval.script_count }}</span> জন সদস্য <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ eval.course.course_code }}</span> বিষয় <span class="filled-data">{{ eval.course.course_title }}</span> পত্র/কোর্স
        </div>
        {% endfor %}
        {% endif %}
        
        {% if practical_exams %}
        <div class="section-title">(৪) ব্যবহারিক পরীক্ষা:</div>
        {% for practical in practical_exams %}
        <div class="flex-container">
            {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ practical.course.course_code }}</span> কেন্দ্রের <span class="filled-data">{{ practical.student_count }}</span> জন পরীক্ষার্থীর জন্য <span class="filled-data">{{ practical.course.course_title }}</span> বিষয়ে <span class="filled-data">{{ practical.day_count }}</span> দিন
        </div>
        {% endfor %}
        {% endif %}
        
        {% if viva_exams %}
        <div class="section-title">(৫) মৌখিক পরীক্ষা:</div>
        {% for viva in viva_exams %}
        <div class="flex-container">
            {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ viva.course.course_title }}</span> বিষয়ে কেন্দ্রের <span class="filled-data">{{ viva.student_count }}</span> জন পরীক্ষার্থীর জন্য
        </div>
        {% endfor %}
        {% endif %}
        
        {% if tabulations %}
        <div class="section-title">(৬) পরীক্ষার ফল সন্নিবেশকরণ:</div>
        {% for tab in tabulations %}
        <div class="flex-container">
            {{ semester.year }} সনের <span class="filled-data">{{ tab.course.course_title }}</span> বিষয়ে <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ tab.student_count }}</span> জন পরীক্ষার্থীর জন্য
        </div>
        {% endfor %}
        {% endif %}
        
        {% if answer_sheet_reviews %}
        <div class="section-title">(৭) উত্তরপত্র নিরীক্ষাঃ</div>
        {% for review in answer_sheet_reviews %}
        <div class="flex-container">
            {{ semester.year }} সনের <span class="filled-data">{{ semester.semester_name }}</span> পরীক্ষার <span class="filled-data">{{ review.course.course_title }}</span> বিষয়ের <span class="filled-data">{{ review.answer_sheet_count }}</span> উত্তরপত্র নিরীক্ষা
        </div>
        {% endfor %}
        {% endif %}
        
        {% if other_remunerations %}
        <div class="section-title">অন্যান্য:</div>
        {% for other in other_remunerations %}
        <div class="flex-container">
            <span class="filled-data">{{ other.remuneration_type }}</span>: <span class="filled-data">{{ other.details }}</span>
            {% if other.page_count %} - <span class="filled-data">{{ other.page_count }}</span> পৃষ্ঠা{% endif %}
        </div>
        {% endfor %}
        {% endif %}
        
        <div class="section-title">(৮) ডাক মাশুল ও সংশ্লিষ্ট অন্যান্য বিবিধ খরচ:-</div>
        <div class="note">(ডাক মাশুলের এবং সংশ্লিষ্ট অন্যান্য বিবিধ খরচের রশিদ বিলের সহিত সংযুক্ত না থাকিলে উহা পরিশোধযোগ্য বলিয়া গণ্য হইবে না)।</div>
        <div class="note">বিঃ দ্রঃ-৮ নং ক্রমানুসারে বিবিধ খরচের ভাউচার (পোষ্টাল রশিদ ও ক্যাশমেমো) এর গায়ে পরীক্ষকের স্বাক্ষর থাকা প্রয়োজন।</div>
        
        <!-- Payment Calculation Table -->
        <div class="section-title" style="margin-top: 30px;">সম্মানীর  হিসাব:</div>
        <table class="calculation-table">
            <thead>
                <tr>
                    <th>ক্রমিক</th>
                    <th>কার্যক্রমের বিবরণ</th>
                    <th>পরিমাণ</th>
                    <th>হার</th>
                    <th>মোট টাকা</th>
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
                <tr><td colspan="4" style="text-align: right; font-weight: bold;">সর্বমোট =</td><td></td></tr>
            </tbody>
        </table>
        
        <div class="section-title" style="margin-top: 20px;">
            (৯) প্রত্যয়ন করা যাইতেছে যে অত্র বিলের টাকা পূর্বে গ্রহণ করা হয় নাই।
        </div>
        
        <div style="margin-top: 20px; display: flex; justify-content: space-between;">
            <div>
                মোট টাকা: <div class="dotted-line" style="width: 200px;"></div>
            </div>
            <div>
                তারিখ: <span class="filled-data">{{ current_date }}</span>
            </div>
        </div>
        
        <div style="margin-top: 30px; display: flex; justify-content: space-between;">
            <div style="text-align: center;">
                <div class="signature-line"></div>
                প্রতি স্বাক্ষর <br>
                পরীক্ষা পরিষদের সভাপতি <br>
                {{ chairman.name }}
            </div>
            <div style="text-align: center;">
                <div class="signature-line"></div>
                পরীক্ষক/নিরীক্ষক/সন্নিবেশকের স্বাক্ষর <br>
                বিভাগ: {{ teacher.department }} <br>
                বর্তমান ঠিকানা: {{ teacher.address }}
            </div>
        </div>
        
        <div style="margin-top: 30px;">
            <div class="flex-container">
                কে (অংকে) টাকা <div class="dotted-line"></div> পয়সা <div class="dotted-line"></div> ''মাত্র দেওয়া যাইতে পারে।
            </div>
        </div>
        
        <div style="margin-top: 30px; display: flex; justify-content: space-between;">
            <div style="text-align: center;">
                <div class="signature-line"></div>
                পরীক্ষক/নিরীক্ষক/সন্নিবেশকের স্বাক্ষর
            </div>
            <div style="text-align: center;">
                <div class="signature-line"></div>
                তারিখ
            </div>
            <div style="text-align: center;">
                <div class="signature-line"></div>
                (বিলে উল্লেখিত সমুদয় টাকা বুঝিয়া পাইলাম)
                <br>
                স্বাক্ষর
            </div>
        </div>
        
        <div class="note" style="margin-top: 30px;">
            বিঃ দ্রঃ- (ক) ২০০.০০ টাকার উর্ধে দাবী রাজস্ব টিকিট ব্যতীত পরিশোধ করা যাইবে না।
        </div>
        
        <div style="text-align: right; margin-top: 10px;">
            <div class="signature-line" style="float: right;"></div>
            পরীক্ষা উপ-নিয়ন্ত্রক <br>
            ঢাকা বিশ্ববিদ্যালয়।
        </div>
        
        <div class="note" style="clear: both; margin-top: 10px;">
            (খ) পরীক্ষক সরকারী চাকুরীয়া হইলে যথাযথ কর্মকর্তার অনুমতি ব্যতিরেকে দাবী পরিশোধ করা হইবে না।
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    chairman = db.query(models.Teacher).filter(models.Teacher.id == semester.chairman_id).first()
    
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
    
    # Generate PDF
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    # Return base64 encoded PDF
    pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
    
    return {
        "pdf_data": pdf_base64,
        "filename": f"remuneration_bill_{teacher.name}_{semester.year}_{semester.semester_name}.pdf"
    }

def generate_cumulative_pdf(db: Session, data):
    semester = db.query(models.ExamSemester).filter(models.ExamSemester.id == data.exam_semester_id).first()
    report_data = crud.get_cumulative_report(db, data.exam_semester_id)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Cumulative Remuneration Report</title>
        <style>
            body { font-family: 'Arial', sans-serif; margin: 20px; font-size: 12px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #000; padding: 8px; text-align: left; }
            th { background-color: #f0f0f0; font-weight: bold; }
            .header { text-align: center; font-weight: bold; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>{{ semester.semester_name }} Examination {{ semester.year }}</h2>
            <h3>Department of Computer Science and Engineering</h3>
            <h3>University of Dhaka</h3>
            <p>Bill Statement</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Serial No.</th>
                    <th>Name and Address of the Examiner</th>
                    <th>Activities</th>
                    <th>Total Amount (To be calculated)</th>
                </tr>
            </thead>
            <tbody>
                {% for item in report_data %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ item.teacher.name }}<br>{{ item.teacher.designation }}, {{ item.teacher.department }}</td>
                    <td>
                        {% if item.details.question_preparations %}Question Preparation, {% endif %}
                        {% if item.details.script_evaluations %}Script Evaluation, {% endif %}
                        {% if item.details.practical_exams %}Practical Exam, {% endif %}
                        {% if item.details.viva_exams %}Viva Exam, {% endif %}
                        {% if item.details.tabulations %}Tabulation, {% endif %}
                        {% if item.details.answer_sheet_reviews %}Answer Sheet Review, {% endif %}
                        {% if item.details.other_remunerations %}Others{% endif %}
                    </td>
                    <td>_____________</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div style="margin-top: 30px; text-align: right;">
            <div style="margin-top: 40px;">
                <div style="border-top: 1px solid #000; width: 200px; margin-left: auto; text-align: center; padding-top: 10px;">
                    (Professor {{ chairman.name }})<br>
                    Chairman, {{ semester.semester_name }} Examination Committee, {{ semester.year }}<br>
                    Department of Computer Science & Engineering,<br>
                    University of Dhaka
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    chairman = db.query(models.Teacher).filter(models.Teacher.id == semester.chairman_id).first()
    
    html_content = template.render(
        semester=semester,
        chairman=chairman,
        report_data=report_data
    )
    
    # Generate PDF
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    # Return base64 encoded PDF
    pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
    
    return {
        "pdf_data": pdf_base64,
        "filename": f"cumulative_report_{semester.year}_{semester.semester_name}.pdf"
    }
